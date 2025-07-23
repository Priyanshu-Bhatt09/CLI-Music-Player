import argparse
import vlc
import time
import yt_dlp
import sys
import msvcrt  # Windows-only
import json
import os
from youtubesearchpython import VideosSearch

PLAYLIST_FILE = "playlists.json"

def load_playlists():
    """Loads playlists from a JSON file."""
    if not os.path.exists(PLAYLIST_FILE):
        return {}
    try:
        with open(PLAYLIST_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {} # Return empty dict if file is corrupted or empty

def save_playlists(playlists):
    """Saves playlists to a JSON file."""
    with open(PLAYLIST_FILE, 'w') as f:
        json.dump(playlists, f, indent=4)

def search_song(song_name):
    """Searches for a song on YouTube and returns the top results."""
    print(f"Searching for '{song_name}'...")
    videos_search = VideosSearch(song_name, limit=5)
    results = videos_search.result()['result']
    return results

def play_audio(song_info, loop=False):
    """
    Plays audio from a YouTube URL with non-blocking controls.
    Returns True if playback was stopped by the user, False otherwise.
    """
    video_url = song_info['link']
    print(f"\nGetting audio stream for: {song_info['title']}...")
    
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info['url']
    except Exception as e:
        print(f"Error fetching audio stream: {e}")
        return False

    instance = vlc.Instance("--quiet")
    
    # Outer loop for song repetition (if loop=True)
    while True:
        player = instance.media_player_new()
        media = instance.media_new(audio_url)
        player.set_media(media)
        player.play()

        print("\n Playing... Press 'p' to pause/resume, 's' to stop.")
        paused = False
        
        # Inner loop for playback and key press checking
        while player.get_state() not in [vlc.State.Ended, vlc.State.Stopped, vlc.State.Error]:
            time.sleep(0.1)
            if msvcrt.kbhit():
                char = msvcrt.getch().decode().lower()
                if char == 'p':
                    player.pause()
                    paused = not paused
                    status = " Paused" if paused else " Playing"
                    print(f"\r{status}...", end="")
                elif char == 's':
                    player.stop()
                    print("\n Playback stopped.")
                    return True # User stopped the song
        
        player.stop()
        if not loop:
            break
        
        print("\n Looping the song...")
        time.sleep(1)
    
    return False # Song finished naturally

def add_to_playlist(song_info, playlists):
    """Handles adding a song to a playlist."""
    print("\n--- Add to Playlist ---")
    if playlists:
        print("Existing playlists:")
        for i, name in enumerate(playlists.keys()):
            print(f"  {i + 1}. {name}")

    choice = input("\nEnter playlist name (or type a new name to create one): ").strip()
    if not choice:
        print("Invalid name.")
        return

    song_data = {'title': song_info['title'], 'link': song_info['link'], 'duration': song_info['duration']}
    
    playlists.setdefault(choice, []).append(song_data)
    print(f"Added '{song_info['title']}' to playlist '{choice}'.")
    save_playlists(playlists)

def remove_from_playlist(playlist_name, playlists):
    """Shows songs in a playlist and lets the user remove one."""
    playlist = playlists.get(playlist_name)
    if not playlist:
        print("Playlist not found.")
        return

    while True:
        print(f"\n--- Songs in '{playlist_name}' ---")
        if not playlist:
            print("This playlist is empty.")
            break
            
        for i, song in enumerate(playlist):
            print(f"  {i + 1}. {song['title']}")
        print("\nEnter song number to remove, or 'b' to go back.")
        
        choice = input("Your choice: ").lower()
        if choice == 'b':
            break

        try:
            song_index = int(choice) - 1
            if 0 <= song_index < len(playlist):
                removed_song = playlist.pop(song_index)
                print(f"Removed '{removed_song['title']}'.")
                save_playlists(playlists)
            else:
                print("Invalid number.")
        except ValueError:
            print("Invalid input. Please enter a number or 'b'.")

def manage_playlists_menu(playlists):
    """Displays playlists and provides options to play, loop, or edit."""
    print("\n--- Manage Playlists ---")
    if not playlists:
        print("No playlists exist yet.")
        return

    playlist_names = list(playlists.keys())
    for i, name in enumerate(playlist_names):
        print(f"  {i + 1}. {name} ({len(playlists[name])} songs)")
    
    try:
        choice = int(input("\nSelect a playlist number to manage: "))
        playlist_name = playlist_names[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    while True:
        print(f"\n--- Managing '{playlist_name}' ---")
        print("1. Play Playlist (play once)")
        print("2. Play Playlist on Loop")
        print("3. Remove a Song from Playlist")
        print("4. Back to Main Menu")
        action = input("Your choice: ")

        if action in ['1', '2']:
            play_on_loop = (action == '2')
            playlist = playlists[playlist_name]
            
            while True:
                user_stopped = False
                for i, song in enumerate(playlist):
                    print(f"\nPlaying from '{playlist_name}' ({i+1}/{len(playlist)})")
                    if play_audio(song): # play_audio returns True if user stops it
                        user_stopped = True
                        break
                
                if not play_on_loop or user_stopped:
                    break
                print(f"\n Playlist '{playlist_name}' finished. Looping...")
            
        elif action == '3':
            remove_from_playlist(playlist_name, playlists)
        elif action == '4':
            break
        else:
            print("Invalid choice.")

def main_menu():
    """The main interactive menu for the music player."""
    while True:
        playlists = load_playlists()
        print("\n=====================")
        print("  CLI Music Player ")
        print("=====================")
        print("1. Search for a Song")
        print("2. Manage Playlists")
        print("3. Exit")
        
        choice = input("Enter your choice: ")

        if choice == '1':
            song_query = input("Enter song name to search: ")
            search_results = search_song(song_query)

            if not search_results:
                print("No results found.")
                continue
            
            for i, video in enumerate(search_results):
                print(f"  {i+1}. {video['title']} ({video['duration']})")
            
            try:
                song_choice = int(input("\nEnter song number: "))
                selected_song = search_results[song_choice - 1]
                
                action = input("Enter 'p' to play, 'a' to add to playlist: ").lower()
                if action == 'p':
                    loop_choice = input("Loop this song? (y/n): ").lower()
                    play_audio(selected_song, loop=(loop_choice == 'y'))
                elif action == 'a':
                    add_to_playlist(selected_song, playlists)
            except (ValueError, IndexError):
                print("Invalid input.")

        elif choice == '2':
            manage_playlists_menu(playlists)
        
        elif choice == '3':
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()