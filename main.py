import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import asyncio

client = commands.Bot(
  command_prefix='+', 
  case_insensitive=False,
  description=None,
  intents=discord.Intents.all(),
)

@client.event
async def on_ready():
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

async def load_extensions():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'commands.{filename[:-3]}')
                print(f'Loaded extension: {filename}')
            except Exception as e:
                print(f'Failed to load extension {filename}: {e}')

async def load_events():
    for filename in os.listdir('./events'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'events.{filename[:-3]}')
                print(f'Loaded event: {filename}')
            except Exception as e:
                print(f'Failed to load event {filename}: {e}')

async def main():
    try:
        await load_extensions()
        await load_events()
        await client.start("token")
    except Exception as e:
        print(e)

discord.utils.setup_logging()
asyncio.run(main())