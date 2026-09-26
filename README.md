# 🎵 Discord Music Bot

A feature-rich Discord Music Bot built with **Python**, **discord.py**, **yt-dlp**, and **FFmpeg**. The bot allows users to join voice channels, search and play music, manage a queue, skip songs, shuffle tracks, enable looping, and control playback directly from Discord.

---

## ✨ Features

* 🎵 Play music using a song name, search query, or YouTube URL
* 🔊 Automatically join the user's voice channel
* 📋 Music queue management
* ⏭️ Skip the currently playing song
* ⏸️ Pause and ▶️ Resume playback using buttons
* 🛑 Stop playback and disconnect
* 🔀 Shuffle the music queue
* 🔁 Loop the current song
* 🗑️ Remove songs from the queue
* 👋 Automatically disconnect when the bot is alone in a voice channel
* ⚡ Supports both **prefix commands** and **Discord slash commands**
* 🎛️ Interactive playback controls
* 🔄 Automatically plays the next queued song

---

## 🛠️ Technologies Used

* **Python**
* **discord.py**
* **yt-dlp**
* **FFmpeg**
* **python-dotenv**
* **Discord API**

The bot uses Discord intents and enables the `message_content` intent for command processing.

---

## 📁 Project Structure

```text
Discord-Music-Bot/
│
├── Music.py
├── .env
├── requirements.txt
└── README.md
```

### Files

**Music.py**
Main bot application containing commands, music playback, queue management, Discord interactions, and FFmpeg configuration.

**.env**
Stores the Discord bot token securely.

**requirements.txt**
Contains the Python dependencies required to run the bot.

**README.md**
Project documentation and setup instructions.

---

## ⚙️ Requirements

Before running the bot, install:

* Python 3.9+
* FFmpeg
* A Discord Bot Application
* Discord Bot Token
* Internet connection

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/discord-music-bot.git
cd discord-music-bot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install discord.py yt-dlp python-dotenv
```

You can also create a `requirements.txt` file:

```text
discord.py
yt-dlp
python-dotenv
```

Then install:

```bash
pip install -r requirements.txt
```

---

## 🎧 FFmpeg Setup

The bot uses FFmpeg to process and stream audio in Discord. The current configuration expects FFmpeg at:

```text
C:\ffmpeg\bin\ffmpeg.exe
```

This path is configured in `Music.py`.

If FFmpeg is installed somewhere else, update:

```python
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
```

to the location of your FFmpeg executable.

---

## 🔐 Environment Variables

Create a `.env` file in the project directory:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

The bot loads the token using `python-dotenv`:

```python
load_dotenv()
```

and starts using:

```python
bot.run(os.getenv("DISCORD_TOKEN"))
```

The token should **never be committed to GitHub**.
Add `.env` to `.gitignore`:

```text
.env
venv/
__pycache__/
```

---

## 🤖 Discord Bot Configuration

When creating the Discord bot, make sure the required intents and permissions are configured.

The application uses:

```python
intents = discord.Intents.default()
intents.message_content = True
```

The bot is then created with:

```python
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)
```

For voice functionality, the bot needs appropriate permissions to:

* View Channel
* Connect
* Speak
* Send Messages
* Embed Links

---

# 🎮 Commands

The bot supports both **prefix commands** and **slash commands**.

---

## 🔊 Join

### Prefix

```text
!join
```

### Slash

```text
/join
```

Joins the voice channel that the user is currently connected to.

---

## 🎵 Play

### Prefix

```text
!play <song name>
```

Example:

```text
!play Shape of You
```

### Slash

```text
/play <song name>
```

Example:

```text
/play Never Gonna Give You Up
```

The bot searches for the requested song using **yt-dlp**, extracts the audio stream, adds it to the queue, and starts playback when appropriate.

---

## ⏭️ Skip

### Prefix

```text
!skip
```

### Slash

```text
/skip
```

Skips the currently playing song and allows the next queued song to play.

---

## 📋 Queue

### Prefix

```text
!queue
```

### Slash

```text
/queue
```

Displays the current music queue.

The bot displays up to the first 10 queued songs in the queue embed.

---

## 🗑️ Remove

### Prefix

```text
!remove <index>
```

Example:

```text
!remove 2
```

### Slash

```text
/remove <index>
```

Removes a specific song from the queue based on its queue number.

---

## 🔀 Shuffle

### Prefix

```text
!shuffle
```

### Slash

```text
/shuffle
```

Randomizes the order of songs currently waiting in the queue.

---

## 🔁 Loop

### Prefix

```text
!loop_cmd
```

### Slash

```text
/loop
```

Toggles loop mode.

When loop mode is enabled, the currently played song is added back to the queue after it starts playing.

---

## 👋 Disconnect

### Prefix

```text
!disconnect
```

### Slash

```text
/disconnect
```

Stops playback, clears the queue, and disconnects the bot from the voice channel.

---

# 🎛️ Music Controls

When a song starts playing, the bot sends a **Now Playing** embed with interactive buttons.

Available controls:

```text
⏸ Pause
▶️ Resume
⏹ Stop
```

The Pause button pauses the current audio, Resume continues playback, and Stop stops playback, clears the queue, and disconnects the bot.

---

# 🔄 Automatic Queue Playback

The bot automatically handles the next song in the queue.

The `play_next()` function:

1. Checks the voice connection.
2. Checks whether another song is playing.
3. Retrieves the next song from the queue.
4. Creates an FFmpeg audio source.
5. Starts playback.
6. Automatically schedules the next song after playback finishes.

A `playing_next` flag is also used to prevent multiple `play_next()` operations from running simultaneously.

---

# 🚪 Automatic Disconnect

The bot automatically disconnects when it is the only member remaining in the voice channel.

This is handled using Discord's `on_voice_state_update` event.

---

# 🔎 Music Search

The bot uses **yt-dlp** to search for and extract audio.

Its configuration includes:

```python
"format": "bestaudio/best"
```

and:

```python
"default_search": "ytsearch"
```

This allows users to enter song names rather than requiring a direct URL.

---

# ⚡ Slash Command Support

The bot supports Discord application commands such as:

```text
/join
/play
/skip
/queue
/remove
/shuffle
/loop
/disconnect
```

Slash commands are synchronized when the bot starts through `setup_hook()`.

---

# ▶️ Running the Bot

After completing the setup, run:

```bash
python Music.py
```

If everything is configured correctly, the terminal will show:

```text
Logged in as <bot-name>
```

The bot will then be available in your Discord server.

---

# 🧩 Troubleshooting

### Bot does not join the voice channel

Make sure:

* You are connected to a voice channel.
* The bot has **Connect** and **Speak** permissions.
* Your Discord bot is online.

### FFmpeg error

Verify that FFmpeg exists at:

```text
C:\ffmpeg\bin\ffmpeg.exe
```

If not, update `FFMPEG_PATH` in `Music.py`.

### Commands are not working

Check that:

* The bot is online.
* `message_content` intent is enabled.
* The bot has permission to read and send messages.
* For slash commands, give Discord some time to synchronize the commands.

### Music cannot be loaded

Make sure:

```bash
pip install --upgrade yt-dlp
```

and verify that you have a working internet connection.

---

# 🔒 Security

Never expose your Discord bot token.

Use:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

and keep `.env` out of version control.

If a bot token is accidentally exposed, regenerate it immediately through the Discord Developer Portal.

---

# 🚀 Future Improvements

Possible enhancements include:

* 🎚️ Audio filters
* 🎼 Playlist support
* 💾 Persistent queues
* 👥 Per-server music queues
* 📊 Now-playing progress indicator
* 🎨 Custom music dashboard
* ⏱️ Automatic inactivity timeout
* 🎤 Support for additional audio sources
* 📝 Command help menu

---

# 👨‍💻 Author

**Meher Sarana Papineni**

Built as a Discord music bot project using Python and Discord API technologies.
