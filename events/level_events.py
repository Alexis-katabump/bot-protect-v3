import discord
from discord.ext import commands
import json
import os

class LevelEvents(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if os.path.exists("level.json"):
            with open("level.json", "r") as file:
                data = json.load(file)
        else:
            data = {}

        user_id = str(message.author.id)
        if user_id not in data:
            data[user_id] = {
                "level": 0,
                "xp": 0
            }

        data[user_id]["xp"] += 1

        xp_needed = data[user_id]["level"] * 10 + 10
        if data[user_id]["xp"] >= xp_needed:
            data[user_id]["level"] += 1
            data[user_id]["xp"] = 0

            level_up_message = f"{message.author.mention} a atteint le niveau {data[user_id]['level']} !"
            await message.channel.send(level_up_message)

        with open("level.json", "w") as file:
            json.dump(data, file)

        await self.client.process_commands(message)

async def setup(client):
    await client.add_cog(LevelEvents(client))