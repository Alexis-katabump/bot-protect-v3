import discord
from discord.ext import commands
import json
import os

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

class LogsEvents(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        config = load_logs_config()
        logs_channel_id = config.get("logs_message_id", 0)

        if logs_channel_id != 0 and before.content != after.content:
            logs_channel = self.client.get_channel(logs_channel_id)
            if logs_channel:
                embed = discord.Embed(title="Message édité", color=discord.Color.blue())
                embed.add_field(name="Auteur", value=before.author.mention, inline=False)
                embed.add_field(name="Avant", value=before.content, inline=False)
                embed.add_field(name="Après", value=after.content, inline=False)
                await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        config = load_logs_config()
        logs_channel_id = config.get("logs_message_id", 0)

        if logs_channel_id != 0:
            logs_channel = self.client.get_channel(logs_channel_id)
            if logs_channel:
                embed = discord.Embed(title="Message supprimé", color=discord.Color.blue())
                embed.add_field(name="Auteur", value=message.author.mention, inline=False)
                embed.add_field(name="Contenu", value=message.content, inline=False)
                await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        config = load_logs_config()
        logs_channel_id = config.get("logs_ban_id", 0)

        if logs_channel_id != 0:
            logs_channel = self.client.get_channel(logs_channel_id)
            if logs_channel:
                entry = None
                async for e in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                    if e.target == user:
                        entry = e
                        break

                embed = discord.Embed(title="Membre banni", color=discord.Color.blue())
                embed.add_field(name="Membre", value=user.mention, inline=False)
                if entry:
                    embed.add_field(name="Banni par", value=entry.user.mention, inline=False)
                await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        config = load_logs_config()
        logs_channel_id = config.get("logs_unban_id", 0)

        if logs_channel_id != 0:
            logs_channel = self.client.get_channel(logs_channel_id)
            if logs_channel:
                entry = None
                async for e in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                    if e.target == user:
                        entry = e
                        break

                embed = discord.Embed(title="Membre débanni", color=discord.Color.blue())
                embed.add_field(name="Membre", value=user.mention, inline=False)
                if entry:
                    embed.add_field(name="Débanni par", value=entry.user.mention, inline=False)
                await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        config = load_logs_config()
        logs_channel_id = config.get("logs_voice_id", 0)

        if logs_channel_id != 0 and before.channel != after.channel:
            logs_channel = self.client.get_channel(logs_channel_id)
            if logs_channel:
                if before.channel:
                    embed = discord.Embed(title="Membre a quitté un salon vocal", color=discord.Color.blue())
                    embed.add_field(name="Membre", value=member.mention, inline=False)
                    embed.add_field(name="Salon avant", value=before.channel.name, inline=False)
                    await logs_channel.send(embed=embed)

                if after.channel:
                    embed = discord.Embed(title="Membre a rejoint un salon vocal", color=discord.Color.green())
                    embed.add_field(name="Membre", value=member.mention, inline=False)
                    embed.add_field(name="Salon après", value=after.channel.name, inline=False)
                    await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        config = load_logs_config()
        logs_channel_id = config.get("logs_role_id", 0)

        if logs_channel_id != 0:
            logs_channel = self.client.get_channel(logs_channel_id)
            if logs_channel:
                embed = discord.Embed(title="Rôle créé", color=discord.Color.green())
                embed.add_field(name="Nom du rôle", value=role.name, inline=False)
                embed.add_field(name="ID du rôle", value=role.id, inline=False)
                await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        config = load_logs_config()
        logs_channel_id = config.get("logs_role_id", 0)

        if logs_channel_id != 0:
            logs_channel = self.client.get_channel(logs_channel_id)
            if logs_channel:
                embed = discord.Embed(title="Rôle supprimé", color=discord.Color.red())
                embed.add_field(name="Nom du rôle", value=role.name, inline=False)
                embed.add_field(name="ID du rôle", value=role.id, inline=False)
                await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        config = load_logs_config()
        logs_channel_id = config.get("logs_role_id", 0)

        if logs_channel_id != 0:
            logs_channel = self.client.get_channel(logs_channel_id)
            if logs_channel:
                embed = discord.Embed(title="Rôle mis à jour", color=discord.Color.blue())
                embed.add_field(name="Nom du rôle", value=before.name, inline=False)
                if before.name != after.name:
                    embed.add_field(name="Ancien nom", value=before.name, inline=False)
                    embed.add_field(name="Nouveau nom", value=after.name, inline=False)
                if before.permissions != after.permissions:
                    embed.add_field(name="Anciennes permissions", value=before.permissions, inline=False)
                    embed.add_field(name="Nouvelles permissions", value=after.permissions, inline=False)
                await logs_channel.send(embed=embed)

async def setup(client):
    await client.add_cog(LogsEvents(client))