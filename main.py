import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import io
from datetime import datetime, timedelta
from fear_and_greed_scraper import capture_fear_greed_gauge

# Load environment variables from .env file
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting Discord bot...")

# handler = logging.FileHandler(filename='discord_bot.log', encoding='utf-8', mode='w')
# handler.addHandler(handler)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

async def fear_greed_loop():
    while True:
        now = datetime.now()
        # For debugging, send every 30 seconds
        next_time = now + timedelta(seconds=30)
        sleep_seconds = (next_time - now).total_seconds()
        await asyncio.sleep(sleep_seconds)
        
        if hasattr(bot, 'fear_greed_channel') and bot.fear_greed_channel:
            print(f"Sending Fear & Greed image at {datetime.now()}", flush=True)
            image_bytes = await asyncio.to_thread(capture_fear_greed_gauge)
            if image_bytes:
                await bot.fear_greed_channel.send(file=discord.File(fp=io.BytesIO(image_bytes), filename="fear_greed_gauge.png"))
            else:
                await bot.fear_greed_channel.send("Failed to capture screenshot.")

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    bot.fear_greed_channel = None
    bot.fear_greed_interval = 30  # default 30 minutes

@bot.command(name='ping')
async def ping(ctx):
    try:
        await ctx.send('Pong!')
    except Exception as e:
        logger.error(f"Error in ping command: {e}")


@bot.command(name='echo')
async def echo(ctx, *, message: str):
    try:
        await ctx.send(message)
    except Exception as e:
        logger.error(f"Error in echo command: {e}")

@bot.command(name='set_fear_greed_channel')
async def set_fear_greed_channel(ctx, channel: discord.TextChannel):
    try:
        bot.fear_greed_channel = channel
        await ctx.send(f"Set Fear & Greed channel to {channel.mention}")
    except Exception as e:
        if isinstance(e, discord.ext.commands.ChannelNotFound):
            await ctx.send("Channel not found. Please provide a valid text channel, e.g., `/set_fear_greed_channel #general`")
        else:
            await ctx.send("An error occurred while setting the channel.")
            logger.error(f"Error in set_fear_greed_channel command: {e}")

@bot.command(name='set_fear_greed_interval')
async def set_fear_greed_interval(ctx, minutes: int):
    try:
        if minutes <= 0 or 60 % minutes != 0:
            await ctx.send("Interval must be a positive divisor of 60 (e.g., 15, 20, 30, 60).")
            return
        bot.fear_greed_interval = minutes
        await ctx.send(f"Set Fear & Greed interval to every {minutes} minutes, aligned to the hour.")
    except Exception as e:
        logger.error(f"Error in set_fear_greed_interval command: {e}")

@bot.command(name='start_fear_greed')
async def start_fear_greed(ctx):
    try:
        if not hasattr(bot, 'fear_greed_channel') or not bot.fear_greed_channel:
            await ctx.send("Please set the Fear & Greed channel first using /set_fear_greed_channel #channel")
            return
        if not hasattr(bot, 'fear_greed_task') or bot.fear_greed_task.done():
            bot.fear_greed_task = asyncio.create_task(fear_greed_loop())
        interval = getattr(bot, 'fear_greed_interval', 30)
        await ctx.send(f"Started sending Fear & Greed gauge every {interval} minutes, aligned to the hour.")
    except Exception as e:
        logger.error(f"Error in start_fear_greed command: {e}")

@bot.command(name='stop_fear_greed')
async def stop_fear_greed(ctx):
    try:
        if hasattr(bot, 'fear_greed_task') and not bot.fear_greed_task.done():
            bot.fear_greed_task.cancel()
        bot.fear_greed_channel = None
        await ctx.send("Stopped sending Fear & Greed gauge.")
    except Exception as e:
        logger.error(f"Error in stop_fear_greed command: {e}")

bot.run(token)