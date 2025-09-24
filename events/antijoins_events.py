import discord
from discord.ext import commands
import json
import os

def load_antijoins_state(guild_id):
    if os.path.exists("antijoins_state.json"):
        with open("antijoins_state.json", "r") as file:
            data = json.load(file)
            return data.get(str(guild_id), False)
    return False

def load_antibot_state(guild_id):
    if os.path.exists("anti_bot.json"):
        with open("anti_bot.json", "r") as file:
            data = json.load(file)
            return data.get(str(guild_id), False)
    return False

class AntijoinsEvents(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if load_antijoins_state(member.guild.id):
            try:
                await member.send("Vous avez été kické du serveur car l'anti-joins est activé.")
            except discord.Forbidden:
                print(f"Impossible d'envoyer un DM à {member.name}.")

            try:
                await member.kick(reason="Anti-joins activé")
                print(f"{member.name} a été kické car l'anti-joins est activé.")
            except discord.Forbidden:
                print(f"Impossible de kicker {member.name}.")

        if member.bot and load_antibot_state(member.guild.id):
            try:
                await member.kick(reason="Anti-bot activé")
                print(f"{member.name} a été kické car l'anti-bot est activé.")
            except discord.Forbidden:
                print(f"Impossible de kicker {member.name}.")

async def setup(client):
    await client.add_cog(AntijoinsEvents(client))