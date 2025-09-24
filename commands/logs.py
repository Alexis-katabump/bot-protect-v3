import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta, timezone

def load_logs_config():
    if os.path.exists("logs.json"):
        with open("logs.json", "r") as file:
            data = json.load(file)
            default_config = {
                "logs_category_id": 0,
                "logs_message_id": 0,
                "logs_ban_id": 0,
                "logs_unban_id": 0,
                "logs_voice_id": 0,
                "logs_role_id": 0
            }
            return {**default_config, **data}
    return {
        "logs_category_id": 0,
        "logs_message_id": 0,
        "logs_ban_id": 0,
        "logs_unban_id": 0,
        "logs_voice_id": 0,
        "logs_role_id": 0
    }




def save_logs_config(config):
    with open("logs.json", "w") as file:
        json.dump(config, file)


class Logs(commands.Cog):
    def __init__(self, client):
        self.client = client


    @app_commands.command(name="setup_logs", description="Configurer les canaux de logs")
    @app_commands.default_permissions(administrator=True)
    async def setup_logs(self, inter: discord.Interaction):
        guild = inter.guild
        config = load_logs_config()

        logs_category = discord.utils.get(guild.categories, id=config["logs_category_id"])
        if not logs_category:
            logs_category = await guild.create_category("📁・Espace logs")
            config["logs_category_id"] = logs_category.id

        logs_message = discord.utils.get(guild.text_channels, id=config["logs_message_id"])
        if not logs_message:
            logs_message = await guild.create_text_channel("📁・logs-message", category=logs_category)
            config["logs_message_id"] = logs_message.id

        logs_ban = discord.utils.get(guild.text_channels, id=config["logs_ban_id"])
        if not logs_ban:
            logs_ban = await guild.create_text_channel("📁・logs-ban", category=logs_category)
            config["logs_ban_id"] = logs_ban.id

        logs_unban = discord.utils.get(guild.text_channels, id=config["logs_unban_id"])
        if not logs_unban:
            logs_unban = await guild.create_text_channel("📁・logs-unban", category=logs_category)
            config["logs_unban_id"] = logs_unban.id

        logs_voice = discord.utils.get(guild.text_channels, id=config["logs_voice_id"])
        if not logs_voice:
            logs_voice = await guild.create_text_channel("📁・logs-vocal", category=logs_category)
            config["logs_voice_id"] = logs_voice.id

        logs_role = discord.utils.get(guild.text_channels, id=config["logs_role_id"])
        if not logs_role:
            logs_role = await guild.create_text_channel("📁・logs-role", category=logs_category)
            config["logs_role_id"] = logs_role.id

        save_logs_config(config)

        await logs_category.set_permissions(guild.default_role, read_messages=False)
        await logs_message.set_permissions(guild.default_role, read_messages=False)
        await logs_ban.set_permissions(guild.default_role, read_messages=False)
        await logs_unban.set_permissions(guild.default_role, read_messages=False)
        await logs_voice.set_permissions(guild.default_role, read_messages=False)
        await logs_role.set_permissions(guild.default_role, read_messages=False)

        await inter.response.send_message("Les canaux de logs ont été configurés !", ephemeral=True)











async def setup(client):
    await client.add_cog(Logs(client))
    