import asyncio
import discord
from discord.ext import tasks, commands
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tracked = {}

def get_latest_video(handle):
    ydl_opts = {'playlist_items': '1', 'extract_flat': 'in_playlist', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"https://www.youtube.com/{handle}/videos", download=False)
            if 'entries' in info and info['entries']:
                return info['entries'][0].get('id')
        except Exception:
            pass
    return None

@bot.command()
@commands.has_permissions(administrator=True)
async def track(ctx, handle: str):
    if not handle.startswith("@"):
        handle = "@" + handle

    latest_id = await asyncio.to_thread(get_latest_video, handle)
    if not latest_id:
        return await ctx.send("Channel not found!")

    tracked[ctx.channel.id] = {"handle": handle, "last_id": latest_id}
    await ctx.send(f"✅ Tracking **{handle}** in this channel!")

    if not check_videos.is_running():
        check_videos.start()

@track.error
async def track_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permissions to use this command.")

@tasks.loop(minutes=10)
async def check_videos():
    for channel_id, data in tracked.items():
        channel = bot.get_channel(channel_id)
        if not channel:
            continue

        latest_id = await asyncio.to_thread(get_latest_video, data["handle"])
        if latest_id and latest_id != data["last_id"]:
            data["last_id"] = latest_id
            await channel.send(f"🚨 **New Video!** https://www.youtube.com/watch?v={latest_id}")

bot.run("YOUR_BOT_TOKEN")