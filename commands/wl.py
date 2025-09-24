import discord
from discord.ext import commands
from discord import app_commands
import json
import re

allowed_domains = ["cdn.discordapp.com", "media.discordapp.net", "tenor.com"]

def load_whitelist():
    try:
        with open("wl.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_whitelist(data):
    with open("wl.json", "w") as file:
        json.dump(data, file)

class Wl(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.bot_owner_id = None

    async def get_bot_owner_id(self):
        if self.bot_owner_id is None:
            app_info = await self.client.application_info()
            self.bot_owner_id = app_info.owner.id
        return self.bot_owner_id


    @app_commands.command(name="wl", description="Ajouter ou retirer un utilisateur de la liste whitelist.")
    async def whitelist(self, inter: discord.Interaction, user: discord.User):
        bot_owner_id = await self.get_bot_owner_id()
        if inter.user.id != bot_owner_id:
            await inter.response.send_message("Vous n'êtes pas autorisé à utiliser cette commande.", ephemeral=True)
            return

        user_id = str(user.id)
        whitelist = load_whitelist()

        if user_id not in whitelist:
            whitelist.append(user_id)
            save_whitelist(whitelist)
            await inter.response.send_message(f"L'utilisateur {user.mention} a été ajouté à la liste whitelist.", ephemeral=True)
        else:
            whitelist.remove(user_id)
            save_whitelist(whitelist)
            await inter.response.send_message(f"L'utilisateur {user.mention} a été retiré de la liste whitelist.", ephemeral=True)

    @app_commands.command(name="whitelist", description="Afficher la liste des utilisateurs whitelistés.")
    @app_commands.default_permissions(administrator=True)
    async def show_whitelist(self, inter: discord.Interaction):
        whitelist = load_whitelist()
        users = [f"<@{user_id}>" for user_id in whitelist]

        embed = discord.Embed(title="Liste des utilisateurs whitelistés", color=discord.Color.red())

        if users:
            embed.add_field(name="Utilisateurs whitelistés", value="\n".join(users), inline=False)
        else:
            embed.add_field(name="Aucun utilisateur whitelisté", value="Il n'y a actuellement aucun utilisateur whitelisté.", inline=False)

        await inter.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="unwl", description="Retirer un utilisateur de la liste whitelist.")
    async def remove_whitelist(self, inter: discord.Interaction, user: discord.User):
        bot_owner_id = await self.get_bot_owner_id()
        if inter.user.id != bot_owner_id:
            await inter.response.send_message("Vous n'êtes pas autorisé à utiliser cette commande.", ephemeral=True)
            return
        user_id = str(user.id)
        whitelist = load_whitelist()

        if user_id in whitelist:
            whitelist.remove(user_id)
            save_whitelist(whitelist)
            await inter.response.send_message(f"L'utilisateur {user.mention} a été retiré de la liste whitelist.", ephemeral=True)
        else:
            await inter.response.send_message(f"L'utilisateur {user.mention} n'est pas dans la liste whitelist.", ephemeral=True)










async def setup(client):
    await client.add_cog(Wl(client))