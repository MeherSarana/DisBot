# 🎵 DisBot — Advanced Discord Music Bot

A feature-rich Discord music bot built with **Python**, **discord.py**, **yt-dlp**, and **FFmpeg**.

DisBot supports:

* ▶️ Play songs via YouTube search or direct links
* 📜 Playlist support
* 🎶 Queue system
* ⏭ Skip songs
* 🔀 Shuffle queue
* 🔁 Loop mode
* 📋 Embedded queue display
* 🎛 Interactive music control buttons
* 🔌 Auto disconnect when voice channel is empty

---

# 🚀 Features

## Core Music Commands

```bash
!play <song name or YouTube URL>
!join
!skip
!queue
!remove <index>
!shuffle
!loop
!disconnect
```

---

# 🛠 Requirements

Before installing, make sure you have:

* Python 3.10+
* FFmpeg installed and added to PATH
* Discord Bot Token
* Git

---

# 📥 Installation Guide

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/MeherSarana/DisBot.git
cd DisBot
```

---

## 2️⃣ Create Virtual Environment

### Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing:

```bash
pip install discord.py yt-dlp pynacl python-dotenv
```

---

# 🎧 Install FFmpeg

## Windows:

1. Download FFmpeg from:
   [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Extract files
3. Add the `bin` folder to System PATH

Example:

```text
C:\ffmpeg\bin
```

## Verify Installation:

```bash
ffmpeg -version
```

---

# 🔐 Environment Variables Setup

Create a `.env` file in the root folder:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

---

# 🤖 Discord Developer Portal Setup

## Steps:

1. Go to Discord Developer Portal
2. Create New Application
3. Go to **Bot** tab
4. Click **Add Bot**
5. Enable:

   * Message Content Intent
   * Server Members Intent (optional)
6. Copy token into `.env`

---

# 🔗 Invite Bot to Your Server

In OAuth2 → URL Generator:

### Scopes:

* `bot`
* `applications.commands`

### Permissions:

* Send Messages
* Connect
* Speak
* Use Slash Commands
* Read Message History

---

# ▶️ Running the Bot

```bash
python Music.py
```

If successful:

```text
Logged in as YourBotName
```

---

# 📌 Example Usage

```bash
!play interstellar theme
!play https://youtube.com/playlist?...
!queue
!skip
!loop
```

---

# 📂 Project Structure

```text
DisBot/
│
├── Music.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 🔒 Security Notes

⚠️ Never upload your real bot token.

Use `.gitignore`:

```gitignore
.env
venv/
__pycache__/
```

If token is exposed:

* Reset token immediately in Discord Developer Portal

---

# 🌍 Deployment Options

You can host DisBot 24/7 on:

* Railway
* Render
* Replit
* VPS
* Docker

---

# 🧠 Future Improvements

Planned upgrades:

* Spotify support
* Slash commands
* Lavalink integration
* Multi-server queue system
* Advanced embeds
* Volume control
* Docker deployment

---

# 🤝 Contributing

Pull requests are welcome.

To contribute:

```bash
git fork
git checkout -b feature-name
```

---

# 📜 License

MIT License

---

# 👨‍💻 Author

**Meher Sarana**

GitHub: [https://github.com/MeherSarana](https://github.com/MeherSarana)

---

# ⭐ Support

If you like this project:

* Star the repository
* Fork it
* Share it with others

---

## 🎶 Enjoy your Discord Music Bot!

