import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import io
from datetime import datetime, timedelta
from fear_and_greed_scraper import capture_fear_greed_gauge
from flask import Flask

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
        interval = getattr(bot, 'fear_greed_interval', 30)
        current_minute = now.minute
        remainder = current_minute % interval
        if remainder == 0:
            # Send immediately if at the exact interval
            print(f"Sending Fear & Greed image at {datetime.now()}", flush=True)
            image_bytes = await capture_fear_greed_gauge()
            if image_bytes:
                await bot.fear_greed_channel.send(file=discord.File(fp=io.BytesIO(image_bytes), filename="fear_greed_gauge.png"))
            else:
                await bot.fear_greed_channel.send("Failed to capture screenshot.")
        
        # Calculate next send time
        next_minute = ((current_minute // interval) + 1) * interval
        if next_minute >= 60:
            next_minute = 0
            next_time = now.replace(hour=now.hour + 1, minute=next_minute, second=0, microsecond=0)
        else:
            next_time = now.replace(minute=next_minute, second=0, microsecond=0)
        
        sleep_seconds = (next_time - now).total_seconds()
        await asyncio.sleep(sleep_seconds)

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

if __name__ == '__main__':
    app = Flask(__name__)

    @app.route('/')
    def home():
        return 'Bot is running!'

    import threading
    def run_bot():
        bot.run(token)
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)