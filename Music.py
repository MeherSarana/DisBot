import discord
from discord.ext import commands
import yt_dlp
import random
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")



intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# yt-dlp settings
ytdl_format_options = {
    'format': 'bestaudio/best',
    # 'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'ignoreerrors': True
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
    "options": "-vn -loglevel panic"
}

# music queue
music_queue = []
loop = False


# ---------------- BOT READY ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ---------------- AUTO DISCONNECT ----------------
@bot.event
async def on_voice_state_update(member, before, after):

    if member.bot:
        return

    voice_client = member.guild.voice_client

    if voice_client is None:
        return

    channel = voice_client.channel

    if len(channel.members) == 1:
        await voice_client.disconnect()


# ---------------- MUSIC CONTROL BUTTONS ----------------
class MusicControls(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.primary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):

        vc = interaction.guild.voice_client

        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸ Paused", ephemeral=True)

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.success)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):

        vc = interaction.guild.voice_client

        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶ Resumed", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):

        vc = interaction.guild.voice_client

        if vc:
            await vc.disconnect()
            music_queue.clear()
            await interaction.response.send_message("⏹ Disconnected", ephemeral=True)


# ---------------- PLAY NEXT SONG ----------------
async def play_next(ctx):

    global music_queue, loop

    if len(music_queue) == 0:
        return

    song = music_queue.pop(0)

    title = song["title"]
    url = song["url"]

    if loop:
        music_queue.append(song)

    source = discord.FFmpegPCMAudio(url, **ffmpeg_options)

    ctx.voice_client.play(
        source,
        after=lambda e: bot.loop.create_task(play_next(ctx))
    )

    embed = discord.Embed(
        title="🎵 Now Playing",
        description=title,
        color=discord.Color.green()
    )

    await ctx.send(embed=embed, view=MusicControls())


# ---------------- JOIN ----------------
@bot.command()
async def join(ctx):

    if ctx.author.voice:

        channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            await channel.connect()

        else:
            await ctx.voice_client.move_to(channel)

    else:
        await ctx.send("Join a voice channel first!")


# ---------------- PLAY ----------------
@bot.command()
async def play(ctx, *, search):

    if ctx.author.voice is None:
        await ctx.send("Join a voice channel first!")
        return

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await voice_channel.connect()

    try:
        info = ytdl.extract_info(search, download=False)
    except Exception:
        await ctx.send("❌ Could not play that video. It may be unavailable.")
        return
    # Playlist detected
    if 'entries' in info:

        count = 0

        for entry in info['entries']:

            if entry is None:
                continue

            music_queue.append({
                "title": entry["title"],
                "url": entry["url"]
            })

            count += 1

        await ctx.send(f"📜 Added **{count} songs** from playlist")

    else:

        title = info['title']
        url = info['url']

        music_queue.append({
            "title": title,
            "url": url
        })

        await ctx.send(f"Added to queue: **{title}**")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)


# ---------------- SKIP ----------------
@bot.command()
async def skip(ctx):

    vc = ctx.voice_client

    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏭ Song skipped")


# ---------------- QUEUE ----------------
@bot.command()
async def queue(ctx):

    if len(music_queue) == 0:
        await ctx.send("Queue is empty")
        return

    embed = discord.Embed(
        title="🎵 Music Queue",
        color=discord.Color.blue()
    )

    description = ""

    for i, song in enumerate(music_queue[:10]):
        description += f"**{i+1}.** {song['title']}\n"

    embed.description = description
    embed.set_footer(text=f"{len(music_queue)} songs in queue")

    await ctx.send(embed=embed)


# ---------------- REMOVE ----------------
@bot.command()
async def remove(ctx, index: int):

    if index <= 0 or index > len(music_queue):
        await ctx.send("Invalid index")
        return

    removed = music_queue.pop(index - 1)

    await ctx.send(f"Removed **{removed}**")


# ---------------- SHUFFLE ----------------
@bot.command()
async def shuffle(ctx):

    if len(music_queue) < 2:
        await ctx.send("Not enough songs to shuffle")
        return

    random.shuffle(music_queue)

    await ctx.send("🔀 Queue shuffled")


# ---------------- LOOP ----------------
@bot.command()
async def loop(ctx):

    global loop
    loop = not loop
    if loop:
        await ctx.send("🔁 Loop enabled")
    else:
        await ctx.send("Loop disabled")


# ---------------- DISCONNECT ----------------
@bot.command()
async def disconnect(ctx):

    vc = ctx.voice_client

    if vc:
        await vc.disconnect()
        music_queue.clear()
        await ctx.send("Disconnected")

<<<<<<< HEAD
bot.run(TOKEN)
=======
bot.run(TOKEN)
>>>>>>> 20aaee02773d99e25c78f0e15927eb06de915379
