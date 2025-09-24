import discord
from discord.ext import commands
from discord import app_commands
import json

def save_blacklist(blacklist):
    with open("bl.json", "w") as file:
        json.dump(blacklist, file)

def load_blacklist():
    try:
        with open("bl.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

blacklist = load_blacklist()

class Blacklist(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="bl", description="Ajouter ou retirer un utilisateur de la liste blacklist.")
    async def blacklist(self, inter: discord.Interaction, user: discord.User):
        guild_owner_id = inter.guild.owner_id
        if inter.user.id != guild_owner_id:
            await inter.response.send_message("Vous n'êtes pas autorisé à utiliser cette commande.", ephemeral=True)
            return

        user_id = str(user.id)
        blacklist = load_blacklist()  

        if user_id not in blacklist:
            blacklist.append(user_id)
            save_blacklist(blacklist) 
            await inter.response.send_message(f"L'utilisateur {user.mention} a été ajouté à la liste blacklist.", ephemeral=True)
        else:
            blacklist.remove(user_id)
            save_blacklist(blacklist)
            await inter.response.send_message(f"L'utilisateur {user.mention} a été retiré de la liste blacklist.", ephemeral=True)

    @app_commands.command(name="unbl", description="Retirer un utilisateur de la liste blacklist.")
    async def unblacklist(self, inter: discord.Interaction, user: discord.User):
        guild_owner_id = inter.guild.owner_id
        if inter.user.id != guild_owner_id:
            await inter.response.send_message("Vous n'êtes pas autorisé à utiliser cette commande.", ephemeral=True)
            return
    
        user_id = str(user.id)
        blacklist = load_blacklist()
    
        if user_id in blacklist:
            blacklist.remove(user_id)
            save_blacklist(blacklist)
            await inter.response.send_message(f"L'utilisateur {user.mention} a été retiré de la liste blacklist.", ephemeral=True)
        else:
            await inter.response.send_message(f"L'utilisateur {user.mention} n'est pas dans la liste blacklist.", ephemeral=True)
    

async def setup(client):
    await client.add_cog(Blacklist(client))