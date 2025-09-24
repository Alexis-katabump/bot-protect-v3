import discord
from discord.ext import commands
import json

def load_blacklist():
    try:
        with open("bl.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

class BlacklistEvents(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        blacklist = load_blacklist()

        if str(member.id) in blacklist:
            try:
                await member.send("Vous avez été banni du serveur car vous étiez sur la liste noire.")
            except discord.Forbidden:
                print(f"Impossible d'envoyer un DM à {member.name}.")

            try:
                await member.ban(reason="Membre sur la liste noire.")
                print(f"{member.name}#{member.discriminator} a été banni car il était sur la liste noire.")
            except discord.Forbidden:
                print(f"Impossible de bannir {member.name}.")

async def setup(client):
    await client.add_cog(BlacklistEvents(client))