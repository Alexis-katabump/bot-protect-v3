import discord
from discord.ext import commands
from discord import app_commands
import json
import os

def load_antijoins_state(guild_id):
    if os.path.exists("antijoins_state.json"):
        with open("antijoins_state.json", "r") as file:
            data = json.load(file)
            return data.get(str(guild_id), False)
    return False

def save_antijoins_state(guild_id, state):
    data = {}
    if os.path.exists("antijoins_state.json"):
        with open("antijoins_state.json", "r") as file:
            data = json.load(file)
    data[str(guild_id)] = state
    with open("antijoins_state.json", "w") as file:
        json.dump(data, file)

def load_antibot_state(guild_id):
    if os.path.exists("anti_bot.json"):
        with open("anti_bot.json", "r") as file:
            data = json.load(file)
            return data.get(str(guild_id), False)
    return False

def save_antibot_state(guild_id, state):
    data = {}
    if os.path.exists("anti_bot.json"):
        with open("anti_bot.json", "r") as file:
            data = json.load(file)
    data[str(guild_id)] = state
    with open("anti_bot.json", "w") as file:
        json.dump(data, file)

class Antijoins(commands.Cog):
    def __init__(self, client):
        self.client = client


    @app_commands.command(name="antijoins", description="Activer ou désactiver l'anti-joins.")
    @app_commands.default_permissions(administrator=True)
    async def toggle_antijoins(self, inter: discord.Interaction):
        guild_id = inter.guild.id
        current_state = load_antijoins_state(guild_id)
        new_state = not current_state
        save_antijoins_state(guild_id, new_state)
        status = "activé" if new_state else "désactivé"
        await inter.response.send_message(f"L'anti-joins est maintenant {status} pour ce serveur.", ephemeral=True)

    @app_commands.command(name="antibot", description="Activer ou désactiver l'anti-bot.")
    @app_commands.default_permissions(administrator=True)
    async def toggle_antibot(self, inter: discord.Interaction):
        guild_id = inter.guild.id
        current_state = load_antibot_state(guild_id)
        new_state = not current_state
        save_antibot_state(guild_id, new_state)
        status = "activé" if new_state else "désactivé"
        await inter.response.send_message(f"L'anti-bot est maintenant {status} pour ce serveur.", ephemeral=True)

async def setup(client):
    await client.add_cog(Antijoins(client))