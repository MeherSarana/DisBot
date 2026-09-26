import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import random
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------- INTENTS ----------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------- SLASH COMMAND SYNC ----------------

@bot.event
async def setup_hook():
    # Sync slash commands with Discord.
    # Global commands may take some time to appear the first time.
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash commands.")


# ---------------- FFMPEG ----------------

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
    "options": "-vn -loglevel panic"
}


# ---------------- YT-DLP ----------------

ytdl_format_options = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
    "js_runtimes": {
        "deno": {}
    }
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


# ---------------- MUSIC STATE ----------------

music_queue = []
loop_enabled = False

# Prevent multiple play_next() tasks from running simultaneously
playing_next = False


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

    if not voice_client.is_connected():
        return

    channel = voice_client.channel

    # Bot is the only member in the voice channel
    if len(channel.members) == 1:
        await voice_client.disconnect()


# ---------------- MUSIC CONTROL BUTTONS ----------------

class MusicControls(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Pause",
        style=discord.ButtonStyle.primary
    )
    async def pause(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        vc = interaction.guild.voice_client

        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message(
                "⏸ Paused",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Nothing is playing.",
                ephemeral=True
            )

    @discord.ui.button(
        label="Resume",
        style=discord.ButtonStyle.success
    )
    async def resume(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        vc = interaction.guild.voice_client

        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message(
                "▶ Resumed",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Nothing is paused.",
                ephemeral=True
            )

    @discord.ui.button(
        label="Stop",
        style=discord.ButtonStyle.danger
    )
    async def stop(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        global music_queue

        vc = interaction.guild.voice_client

        if vc:

            if vc.is_playing() or vc.is_paused():
                vc.stop()

            music_queue.clear()

            await vc.disconnect()

            await interaction.response.send_message(
                "⏹ Disconnected",
                ephemeral=True
            )

        else:
            await interaction.response.send_message(
                "Bot is not connected.",
                ephemeral=True
            )


# ---------------- PLAY NEXT SONG ----------------

async def play_next(ctx):

    global music_queue
    global loop_enabled
    global playing_next

    # Prevent multiple play_next() calls
    if playing_next:
        return

    playing_next = True

    try:

        vc = ctx.voice_client

        # Check voice connection
        if vc is None or not vc.is_connected():
            print("No active voice connection.")
            return

        # Don't start another song while one is already playing
        if vc.is_playing() or vc.is_paused():
            return

        # Queue empty
        if len(music_queue) == 0:
            print("Queue is empty.")
            return

        song = music_queue.pop(0)

        title = song["title"]
        url = song["url"]

        # Loop current song
        if loop_enabled:
            music_queue.append(song)

        print(f"Playing: {title}")

        try:

            source = discord.FFmpegPCMAudio(
                url,
                executable=FFMPEG_PATH,
                **ffmpeg_options
            )

        except Exception as e:

            print(f"FFmpeg error: {e}")

            await ctx.send(
                f"❌ FFmpeg error while playing **{title}**"
            )

            return

        # Callback runs from another thread
        def after_playing(error):

            if error:
                print(f"Player error: {error}")

            # Schedule next song safely on Discord's event loop
            try:
                bot.loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(
                        play_next(ctx)
                    )
                )
            except Exception as e:
                print(f"Could not schedule next song: {e}")

        # Make sure voice client still exists
        if ctx.voice_client is None:
            return

        ctx.voice_client.play(
            source,
            after=after_playing
        )

        # Now Playing embed
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=title,
            color=discord.Color.green()
        )

        try:

            await ctx.send(
                embed=embed,
                view=MusicControls()
            )

        except discord.HTTPException as e:

            print(f"Could not send Now Playing message: {e}")

    except Exception as e:

        print(f"Playback error: {e}")

    finally:

        # Allow future play_next() calls
        playing_next = False


# ---------------- JOIN ----------------

@bot.command()
async def join(ctx):

    if ctx.author.voice is None:
        await ctx.send(
            "❌ Join a voice channel first!"
        )
        return

    channel = ctx.author.voice.channel

    try:

        if ctx.voice_client is None:

            await channel.connect()

        elif ctx.voice_client.channel != channel:

            await ctx.voice_client.move_to(channel)

        await ctx.send(
            f"🔊 Joined **{channel.name}**"
        )

    except asyncio.TimeoutError:

        await ctx.send(
            "❌ Discord voice connection timed out. Try `!join` again."
        )

    except Exception as e:

        print(f"Voice connection error: {e}")

        await ctx.send(
            f"❌ Could not connect to voice: `{e}`"
        )


# ---------------- PLAY ----------------

@bot.command()
async def play(ctx, *, search):

    if ctx.author.voice is None:
        await ctx.send(
            "❌ Join a voice channel first!"
        )
        return

    voice_channel = ctx.author.voice.channel

    # ---------------- CONNECT ----------------

    try:

        if ctx.voice_client is None:

            await voice_channel.connect()

        elif ctx.voice_client.channel != voice_channel:

            await ctx.voice_client.move_to(
                voice_channel
            )

    except asyncio.TimeoutError:

        await ctx.send(
            "❌ Voice connection timed out. Try `!play` again."
        )
        return

    except Exception as e:

        print(f"Voice connection error: {e}")

        await ctx.send(
            f"❌ Could not connect to voice: `{e}`"
        )

        return

    # ---------------- YOUTUBE ----------------

    try:

        print(f"Searching: {search}")

        info = await asyncio.to_thread(
            ytdl.extract_info,
            search,
            False
        )

        if info is None:

            await ctx.send(
                "❌ Could not find that song."
            )

            return

        if "entries" in info:

            entries = info.get("entries")

            if not entries:

                await ctx.send(
                    "❌ No results found."
                )

                return

            info = entries[0]

        title = info.get("title")
        url = info.get("url")

        if not title or not url:

            await ctx.send(
                "❌ Could not extract audio from this video."
            )

            return

        music_queue.append({
            "title": title,
            "url": url
        })

        await ctx.send(
            f"🎵 Added to queue: **{title}**"
        )

        # Start playback only if nothing is currently playing
        if (
            ctx.voice_client
            and ctx.voice_client.is_connected()
            and not ctx.voice_client.is_playing()
            and not ctx.voice_client.is_paused()
        ):

            await play_next(ctx)

    except Exception as e:

        print(f"YouTube extraction error: {e}")

        await ctx.send(
            f"❌ Could not load the song:\n`{e}`"
        )


# ---------------- SKIP ----------------

@bot.command()
async def skip(ctx):

    vc = ctx.voice_client

    if vc and vc.is_playing():

        vc.stop()

        await ctx.send(
            "⏭ Song skipped"
        )

    else:

        await ctx.send(
            "❌ Nothing is playing."
        )


# ---------------- QUEUE ----------------

@bot.command()
async def queue(ctx):

    if len(music_queue) == 0:

        await ctx.send(
            "🎵 Queue is empty"
        )

        return

    embed = discord.Embed(
        title="🎵 Music Queue",
        color=discord.Color.blue()
    )

    description = ""

    for i, song in enumerate(
        music_queue[:10]
    ):

        description += (
            f"**{i + 1}.** "
            f"{song['title']}\n"
        )

    embed.description = description

    embed.set_footer(
        text=f"{len(music_queue)} songs in queue"
    )

    await ctx.send(
        embed=embed
    )


# ---------------- REMOVE ----------------

@bot.command()
async def remove(ctx, index: int):

    if index <= 0 or index > len(music_queue):

        await ctx.send(
            "❌ Invalid queue index."
        )

        return

    removed = music_queue.pop(index - 1)

    await ctx.send(
        f"🗑 Removed **{removed['title']}**"
    )


# ---------------- SHUFFLE ----------------

@bot.command()
async def shuffle(ctx):

    if len(music_queue) < 2:

        await ctx.send(
            "❌ Not enough songs to shuffle."
        )

        return

    random.shuffle(music_queue)

    await ctx.send(
        "🔀 Queue shuffled"
    )


# ---------------- LOOP ----------------

@bot.command()
async def loop_cmd(ctx):

    global loop_enabled

    loop_enabled = not loop_enabled

    if loop_enabled:

        await ctx.send(
            "🔁 Loop enabled"
        )

    else:

        await ctx.send(
            "🔁 Loop disabled"
        )


# ---------------- DISCONNECT ----------------

@bot.command()
async def disconnect(ctx):

    global music_queue

    vc = ctx.voice_client

    if vc:

        if vc.is_playing() or vc.is_paused():
            vc.stop()

        await vc.disconnect()

        music_queue.clear()

        await ctx.send(
            "👋 Disconnected"
        )

    else:

        await ctx.send(
            "❌ Bot is not connected."
        )




# ============================================================
#                  DISCORD SLASH COMMANDS
# ============================================================

class InteractionContext:
    """Adapter that lets play_next() work with a slash command."""

    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction

    @property
    def voice_client(self):
        return self.interaction.guild.voice_client

    async def send(self, *args, **kwargs):
        return await self.interaction.followup.send(*args, **kwargs)


@bot.tree.command(name="join", description="Join your current voice channel")
async def slash_join(interaction: discord.Interaction):

    if interaction.user.voice is None:
        await interaction.response.send_message(
            "❌ Join a voice channel first!",
            ephemeral=True
        )
        return

    channel = interaction.user.voice.channel

    try:
        vc = interaction.guild.voice_client

        if vc is None:
            await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        await interaction.response.send_message(
            f"🔊 Joined **{channel.name}**"
        )

    except asyncio.TimeoutError:
        await interaction.response.send_message(
            "❌ Discord voice connection timed out. Try `/join` again.",
            ephemeral=True
        )

    except Exception as e:
        print(f"Voice connection error: {e}")
        await interaction.response.send_message(
            f"❌ Could not connect to voice: `{e}`",
            ephemeral=True
        )


@bot.tree.command(name="play", description="Play a song or YouTube search")
@app_commands.describe(search="Song name, YouTube URL, or search query")
async def slash_play(interaction: discord.Interaction, search: str):

    if interaction.user.voice is None:
        await interaction.response.send_message(
            "❌ Join a voice channel first!",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel

    try:
        vc = interaction.guild.voice_client

        if vc is None:
            await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

    except asyncio.TimeoutError:
        await interaction.followup.send(
            "❌ Voice connection timed out. Try `/play` again."
        )
        return

    except Exception as e:
        print(f"Voice connection error: {e}")
        await interaction.followup.send(
            f"❌ Could not connect to voice: `{e}`"
        )
        return

    try:
        print(f"Searching: {search}")

        info = await asyncio.to_thread(
            ytdl.extract_info,
            search,
            False
        )

        if info is None:
            await interaction.followup.send(
                "❌ Could not find that song."
            )
            return

        if "entries" in info:
            entries = info.get("entries")

            if not entries:
                await interaction.followup.send(
                    "❌ No results found."
                )
                return

            info = entries[0]

        title = info.get("title")
        url = info.get("url")

        if not title or not url:
            await interaction.followup.send(
                "❌ Could not extract audio from this video."
            )
            return

        music_queue.append({
            "title": title,
            "url": url
        })

        await interaction.followup.send(
            f"🎵 Added to queue: **{title}**"
        )

        if (
            interaction.guild.voice_client
            and interaction.guild.voice_client.is_connected()
            and not interaction.guild.voice_client.is_playing()
            and not interaction.guild.voice_client.is_paused()
        ):
            await play_next(InteractionContext(interaction))

    except Exception as e:
        print(f"YouTube extraction error: {e}")
        await interaction.followup.send(
            f"❌ Could not load the song:\n`{e}`"
        )


@bot.tree.command(name="skip", description="Skip the currently playing song")
async def slash_skip(interaction: discord.Interaction):

    vc = interaction.guild.voice_client

    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭ Song skipped")
    else:
        await interaction.response.send_message(
            "❌ Nothing is playing.",
            ephemeral=True
        )


@bot.tree.command(name="queue", description="Show the current music queue")
async def slash_queue(interaction: discord.Interaction):

    if len(music_queue) == 0:
        await interaction.response.send_message("🎵 Queue is empty")
        return

    embed = discord.Embed(
        title="🎵 Music Queue",
        color=discord.Color.blue()
    )

    description = ""

    for i, song in enumerate(music_queue[:10]):
        description += f"**{i + 1}.** {song['title']}\n"

    embed.description = description
    embed.set_footer(text=f"{len(music_queue)} songs in queue")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="remove", description="Remove a song from the queue")
@app_commands.describe(index="Queue number to remove")
async def slash_remove(interaction: discord.Interaction, index: int):

    if index <= 0 or index > len(music_queue):
        await interaction.response.send_message(
            "❌ Invalid queue index.",
            ephemeral=True
        )
        return

    removed = music_queue.pop(index - 1)

    await interaction.response.send_message(
        f"🗑 Removed **{removed['title']}**"
    )


@bot.tree.command(name="shuffle", description="Shuffle the music queue")
async def slash_shuffle(interaction: discord.Interaction):

    if len(music_queue) < 2:
        await interaction.response.send_message(
            "❌ Not enough songs to shuffle.",
            ephemeral=True
        )
        return

    random.shuffle(music_queue)
    await interaction.response.send_message("🔀 Queue shuffled")


@bot.tree.command(name="loop", description="Toggle music loop mode")
async def slash_loop(interaction: discord.Interaction):

    global loop_enabled

    loop_enabled = not loop_enabled

    if loop_enabled:
        await interaction.response.send_message("🔁 Loop enabled")
    else:
        await interaction.response.send_message("🔁 Loop disabled")


@bot.tree.command(name="disconnect", description="Disconnect the music bot")
async def slash_disconnect(interaction: discord.Interaction):

    global music_queue

    vc = interaction.guild.voice_client

    if vc:
        if vc.is_playing() or vc.is_paused():
            vc.stop()

        await vc.disconnect()
        music_queue.clear()

        await interaction.response.send_message("👋 Disconnected")
    else:
        await interaction.response.send_message(
            "❌ Bot is not connected.",
            ephemeral=True
        )


# ---------------- RUN BOT ----------------

# IMPORTANT:
# Put your NEW bot token here.
# Do not use the token that was previously exposed.

bot.run(os.getenv("DISCORD_TOKEN"))
