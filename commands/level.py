import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta, timezone



class Level(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="level", description="Afficher le niveau d'un utilisateur")
    async def level(self, inter: discord.Interaction, member: discord.User = None):
        if member is None:
            member = inter.user

        if os.path.exists("level.json"):
            with open("level.json", "r") as file:
                data = json.load(file)
        else:
            data = {}

        if str(member.id) in data:
            level = data[str(member.id)]["level"]
            xp = data[str(member.id)]["xp"]
        else:
            level = 0
            xp = 0

        embed = discord.Embed(title="Niveau", color=discord.Color.red())
        embed.add_field(name="Utilisateur", value=member.mention)
        embed.add_field(name="Niveau", value=level)
        embed.add_field(name="XP", value=xp)

        await inter.response.send_message(embed=embed, ephemeral=False)


async def setup(client):
    await client.add_cog(Level(client))
