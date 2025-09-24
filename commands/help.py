import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="help", description="Affiche la liste des commandes du bot.")
    async def help(self, inter: discord.Interaction):
        categories_and_commands = {}

        for command in self.client.tree.walk_commands():
            category = command.module.split('.')[-1]
            if category not in categories_and_commands:
                categories_and_commands[category] = []
            categories_and_commands[category].append(command.name)

        options = [
            discord.SelectOption(label=category.capitalize(), description=f"Voir les commandes de {category.capitalize()}")
            for category in categories_and_commands.keys()
        ]

        select = discord.ui.Select(placeholder="Choisissez une catégorie", options=options)

        async def select_callback(interaction: discord.Interaction):
            selected_category = interaction.data['values'][0].lower()
            commands_list = categories_and_commands[selected_category]
            commands_text = " ".join([f"`{command}`" for command in commands_list])

            embed = discord.Embed(
                title=f"Commandes de {selected_category.capitalize()}",
                description=commands_text,
                color=discord.Color.purple()
            )

            await interaction.response.edit_message(embed=embed, view=view)

        select.callback = select_callback

        view = discord.ui.View()
        view.add_item(select)

        embed = discord.Embed(
            title="Liste des commandes de KataBump Protect",
            description="Utilisez le menu déroulant ci-dessous pour sélectionner une catégorie de commandes.",
            color=discord.Color.purple()
        )

        await inter.response.send_message(embed=embed, view=view, ephemeral=False)

async def setup(client):
    await client.add_cog(Help(client))