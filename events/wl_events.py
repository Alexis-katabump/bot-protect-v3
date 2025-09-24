import discord
from discord.ext import commands
import json
import re

allowed_domains = ["cdn.discordapp.com", "media.discordapp.net", "tenor.com"]

def load_whitelist():
    try:
        with open("wl.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

class WlEvents(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bot_owner_id = None

    @commands.Cog.listener()
    async def on_ready(self):
        app_info = await self.client.application_info()
        self.bot_owner_id = app_info.owner.id

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        whitelist = load_whitelist()
        async for entry in channel.guild.audit_logs(limit=10):
            if entry.action == discord.AuditLogAction.channel_delete and entry.target.id == channel.id:
                deleter = entry.user
                if str(deleter.id) not in whitelist and deleter.id != self.client.user.id and deleter.id != self.bot_owner_id:
                    try:
                        await deleter.kick(reason="Suppression de salon sans autorisation.")
                    except discord.Forbidden:
                        print(f"Impossible de kicker l'utilisateur {deleter.name}.")
                    else:
                        print(f"L'utilisateur {deleter.name} a été kick car il a supprimé un salon sans autorisation.")

                    if isinstance(channel, discord.CategoryChannel):
                        try:
                            recreated_channel = await channel.guild.create_category(
                                name=channel.name
                            )
                        except discord.Forbidden:
                            print(f"Impossible de recréer la catégorie {channel.name}.")
                        else:
                            print(f"Catégorie {channel.name} recréée avec succès.")
                    else:
                        overwrites = channel.overwrites
                        try:
                            recreated_channel = await channel.guild.create_text_channel(
                                name=channel.name,
                                overwrites=overwrites
                            )
                        except discord.Forbidden:
                            print(f"Impossible de recréer le salon {channel.name}.")
                        else:
                            print(f"Salon {channel.name} recréé avec succès avec les mêmes autorisations.")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        whitelist = load_whitelist()
        async for entry in channel.guild.audit_logs(limit=10):
            if entry.action == discord.AuditLogAction.channel_create and entry.target.id == channel.id:
                creator = entry.user
                if str(creator.id) not in whitelist and creator.id != self.client.user.id and creator.id != self.bot_owner_id:
                    try:
                        await creator.kick(reason="Création de salon sans autorisation.")
                    except discord.Forbidden:
                        print(f"Impossible de kicker l'utilisateur {creator.name}.")
                    else:
                        print(f"L'utilisateur {creator.name} a été kick car il a créé un salon sans autorisation.")

                    try:
                        await channel.delete(reason="Suppression de salon créé sans autorisation.")
                    except discord.Forbidden:
                        print(f"Impossible de supprimer le salon {channel.name} créé par {creator.name}.")
                    else:
                        print(f"Salon {channel.name} créé par {creator.name} supprimé avec succès.")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        whitelist = load_whitelist()
        async for entry in before.guild.audit_logs(limit=10):
            if entry.action == discord.AuditLogAction.channel_update and entry.target.id == before.id:
                creator = entry.user
                if str(creator.id) not in whitelist and creator.id != self.client.user.id and creator.id != self.bot_owner_id:
                    try:
                        await creator.kick(reason="Modification de salon sans autorisation.")
                    except discord.Forbidden:
                        print(f"Impossible de kicker l'utilisateur {creator.name}.")
                    else:
                        print(f"L'utilisateur {creator.name} a été kick car il a modifié un salon sans autorisation.")

                    try:
                        await before.edit(name=before.name)
                    except discord.Forbidden:
                        print(f"Impossible de rétablir l'ancien nom du salon {before.name}.")
                    else:
                        print(f"Ancien nom du salon {before.name} restauré avec succès.")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user: discord.Member):
        whitelist = load_whitelist()
        async for entry in guild.audit_logs(limit=10):
            if entry.action == discord.AuditLogAction.ban and entry.target.id == user.id:
                creator = entry.user
                if str(creator.id) not in whitelist and creator.id != self.client.user.id and creator.id != self.bot_owner_id:
                    await guild.unban(user)
                    try:
                        await creator.edit(roles=[])
                    except discord.Forbidden:
                        print(f"Impossible de kick l'utilisateur {creator.name}.")
                    else:
                        print(f"L'utilisateur {creator.name} a été kick car il a banni un membre.")

    @commands.Cog.listener()
    @staticmethod
    async def on_member_remove(member):
        whitelist = load_whitelist()
        async for entry in member.guild.audit_logs(limit=10):
            if entry.action == discord.AuditLogAction.kick and entry.target.id == member.id:
                creator = entry.user
                if str(creator.id) not in str(whitelist) and creator.id != member.guild.me.id and creator.id != member.guild.owner_id:
                    try:
                        await creator.edit(roles=[])
                    except discord.Forbidden:
                        print(f"Impossible de kick l'utilisateur {creator.name}.")
                    else:
                        print(f"L'utilisateur {creator.name} a été kick car il a kick.")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        whitelist = load_whitelist()
        async for entry in role.guild.audit_logs(limit=10):
            if entry.action == discord.AuditLogAction.role_create and entry.target.id == role.id:
                creator = entry.user
                if str(creator.id) not in whitelist and creator.id != self.client.user.id and creator.id != self.bot_owner_id:
                    try:
                        await creator.kick(reason="Création de rôle sans autorisation.")
                    except discord.Forbidden:
                        print(f"Impossible de kicker l'utilisateur {creator.name}.")
                    else:
                        print(f"L'utilisateur {creator.name} a été kick car il a créé un rôle sans autorisation.")

                    try:
                        await role.delete()
                    except discord.Forbidden:
                        print(f"Impossible de supprimer le rôle {role.name}.")
                    else:
                        print(f"Rôle {role.name} supprimé avec succès.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        whitelist = load_whitelist()
        if str(message.author.id) in whitelist:
            return

        urls = re.findall(r'discord.gg/\S+', message.content)
        caca = re.findall(r'https?://\S+', message.content)

        for url in urls:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, les liens `discord.gg/` ne sont pas autorisés.")
            return

        for url in caca:
            if not any(domain in url for domain in allowed_domains):
                await message.delete()
                await message.channel.send(f"{message.author.mention}, les liens externes ne sont pas autorisés.")
                return

async def setup(client):
    await client.add_cog(WlEvents(client))