# CLI YouTube Music Player

A command-line music player written in Python that allows you to search for, play, and manage playlists of songs directly from YouTube.

## Features

* 🔎 **Search** for any song on YouTube.
* ▶️ **Play** audio directly from a stream without downloading the file.
* ⏯️ **Playback Controls** including pause, resume, and stop.
* 📝 **Playlist Management** to create playlists, add songs, and remove songs.
* 🔄 **Looping** for both individual songs and entire playlists.
* 🚫 **Ad-Free** playback by using the direct audio stream.

## Prerequisites

Before you begin, you must have the following installed on your system:

* **Python 3.x**
* **VLC Media Player**: This script uses `python-vlc`, which requires a local installation of VLC. You can download it from the [official VideoLAN website](https://www.videolan.org/vlc/).

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
    cd YOUR_REPOSITORY_NAME
    ```

2.  **(Recommended) Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, simply execute the main script:
```bash
python main.py