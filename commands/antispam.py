import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta

def load_antispam_config():
    if os.path.exists("antispam_config.json"):
        with open("antispam_config.json", "r") as file:
            data = json.load(file)
            default_config = {
                "enabled": False,
                "message_limit": 5,
                "time_window": 3,
                "sanction_type": "timeout",  # timeout, kick, ban, warn
                "timeout_duration": 300,  # 5 minutes en secondes
                "delete_messages": True,
                "immune_roles": [],
                "ignored_channels": [],
                "warn_threshold": 3,  # Nombre d'avertissements avant sanction
                "ban_duration": 0,  # 0 = permanent
                "log_channel_id": 0
            }
            return {**default_config, **data}
    return {
        "enabled": False,
        "message_limit": 5,
        "time_window": 3,
        "sanction_type": "timeout",
        "timeout_duration": 300,
        "delete_messages": True,
        "immune_roles": [],
        "ignored_channels": [],
        "warn_threshold": 3,
        "ban_duration": 0,
        "log_channel_id": 0
    }

def save_antispam_config(config):
    with open("antispam_config.json", "w") as file:
        json.dump(config, file, indent=2)

def load_spam_warnings():
    if os.path.exists("spam_warnings.json"):
        with open("spam_warnings.json", "r") as file:
            return json.load(file)
    return {}

def save_spam_warnings(data):
    with open("spam_warnings.json", "w") as file:
        json.dump(data, file, indent=2)

class AntiSpam(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="setup_antispam", description="Configurer le système anti-spam")
    @app_commands.default_permissions(administrator=True)
    async def setup_antispam(self, inter: discord.Interaction):
        await inter.response.send_message("⚙️ Configuration de l'anti-spam en cours...", ephemeral=True)

        config = load_antispam_config()
        guild = inter.guild

        try:
            # Créer un salon de logs si nécessaire
            if config["log_channel_id"] == 0:
                # Chercher une catégorie logs ou en créer une
                logs_category = discord.utils.get(guild.categories, name="📁・Espace logs")
                if not logs_category:
                    logs_category = await guild.create_category("📁・Espace logs")

                # Créer le salon de logs anti-spam
                antispam_log_channel = await guild.create_text_channel(
                    "📁・logs-antispam",
                    category=logs_category,
                    reason="Canal de logs pour l'anti-spam"
                )
                config["log_channel_id"] = antispam_log_channel.id

                # Configurer les permissions
                await antispam_log_channel.set_permissions(guild.default_role, read_messages=False)

            save_antispam_config(config)

            # Réponse de succès
            log_channel = guild.get_channel(config["log_channel_id"])
            embed = discord.Embed(
                title="✅ Anti-Spam Configuré",
                description="Le système anti-spam a été configuré avec succès !",
                color=discord.Color.green()
            )
            embed.add_field(name="📊 Statut", value="❌ Désactivé" if not config["enabled"] else "✅ Activé", inline=True)
            embed.add_field(name="📨 Limite messages", value=f"{config['message_limit']}", inline=True)
            embed.add_field(name="⏱️ Fenêtre temps", value=f"{config['time_window']}s", inline=True)
            embed.add_field(name="⚖️ Sanction", value=config["sanction_type"].title(), inline=True)
            embed.add_field(name="📝 Canal logs", value=log_channel.mention if log_channel else "❌ Erreur", inline=True)
            embed.add_field(name="🗑️ Supprimer messages", value="✅ Oui" if config["delete_messages"] else "❌ Non", inline=True)

            await inter.edit_original_response(content=None, embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur de Configuration",
                description=f"Erreur lors de la configuration : {str(e)}",
                color=discord.Color.red()
            )
            await inter.edit_original_response(content=None, embed=error_embed)

    @app_commands.command(name="toggle_antispam", description="Activer ou désactiver le système anti-spam")
    @app_commands.default_permissions(administrator=True)
    async def toggle_antispam(self, inter: discord.Interaction):
        config = load_antispam_config()
        config["enabled"] = not config["enabled"]
        save_antispam_config(config)

        status = "✅ activé" if config["enabled"] else "❌ désactivé"
        embed = discord.Embed(
            title="🔄 Anti-Spam mis à jour",
            description=f"Le système anti-spam est maintenant {status}",
            color=discord.Color.green() if config["enabled"] else discord.Color.red()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="antispam_config", description="Configurer les paramètres de l'anti-spam")
    @app_commands.default_permissions(administrator=True)
    async def antispam_config(self, inter: discord.Interaction,
                             message_limit: int = 5,
                             time_window: int = 3,
                             sanction_type: str = "timeout",
                             timeout_duration: int = 300,
                             delete_messages: bool = True):

        # Validation des paramètres
        if message_limit < 2 or message_limit > 50:
            await inter.response.send_message("❌ La limite de messages doit être entre 2 et 50.", ephemeral=True)
            return

        if time_window < 1 or time_window > 60:
            await inter.response.send_message("❌ La fenêtre de temps doit être entre 1 et 60 secondes.", ephemeral=True)
            return

        valid_sanctions = ["timeout", "kick", "ban", "warn"]
        if sanction_type.lower() not in valid_sanctions:
            await inter.response.send_message(f"❌ Type de sanction invalide. Utilisez: {', '.join(valid_sanctions)}", ephemeral=True)
            return

        if timeout_duration < 60 or timeout_duration > 2419200:  # Max 28 jours
            await inter.response.send_message("❌ La durée de timeout doit être entre 60 secondes et 28 jours.", ephemeral=True)
            return

        # Sauvegarder la configuration
        config = load_antispam_config()
        config["message_limit"] = message_limit
        config["time_window"] = time_window
        config["sanction_type"] = sanction_type.lower()
        config["timeout_duration"] = timeout_duration
        config["delete_messages"] = delete_messages
        save_antispam_config(config)

        # Réponse
        embed = discord.Embed(
            title="⚙️ Configuration Anti-Spam mise à jour",
            color=discord.Color.blue()
        )
        embed.add_field(name="📨 Limite messages", value=f"{message_limit}", inline=True)
        embed.add_field(name="⏱️ Fenêtre temps", value=f"{time_window} secondes", inline=True)
        embed.add_field(name="⚖️ Sanction", value=sanction_type.title(), inline=True)

        if sanction_type.lower() == "timeout":
            embed.add_field(name="⏰ Durée timeout", value=f"{timeout_duration // 60} minutes", inline=True)

        embed.add_field(name="🗑️ Supprimer messages", value="✅ Oui" if delete_messages else "❌ Non", inline=True)

        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="antispam_immunity", description="Ajouter ou retirer l'immunité anti-spam à un rôle")
    @app_commands.default_permissions(administrator=True)
    async def antispam_immunity(self, inter: discord.Interaction, role: discord.Role):
        config = load_antispam_config()

        if role.id in config["immune_roles"]:
            config["immune_roles"].remove(role.id)
            action = "retiré"
            color = discord.Color.orange()
        else:
            config["immune_roles"].append(role.id)
            action = "ajouté"
            color = discord.Color.green()

        save_antispam_config(config)

        embed = discord.Embed(
            title=f"🛡️ Immunité {action}",
            description=f"Le rôle {role.mention} a été {action} de la liste d'immunité anti-spam.",
            color=color
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="antispam_ignore", description="Ajouter ou retirer un salon des canaux ignorés")
    @app_commands.default_permissions(administrator=True)
    async def antispam_ignore(self, inter: discord.Interaction, channel: discord.TextChannel):
        config = load_antispam_config()

        if channel.id in config["ignored_channels"]:
            config["ignored_channels"].remove(channel.id)
            action = "retiré"
            color = discord.Color.orange()
        else:
            config["ignored_channels"].append(channel.id)
            action = "ajouté"
            color = discord.Color.green()

        save_antispam_config(config)

        embed = discord.Embed(
            title=f"🚫 Canal {action}",
            description=f"Le canal {channel.mention} a été {action} de la liste des canaux ignorés.",
            color=color
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="antispam_status", description="Afficher le statut du système anti-spam")
    @app_commands.default_permissions(administrator=True)
    async def antispam_status(self, inter: discord.Interaction):
        config = load_antispam_config()
        guild = inter.guild

        # Obtenir les informations
        log_channel = guild.get_channel(config["log_channel_id"])
        immune_roles = [guild.get_role(r_id) for r_id in config["immune_roles"] if guild.get_role(r_id)]
        ignored_channels = [guild.get_channel(c_id) for c_id in config["ignored_channels"] if guild.get_channel(c_id)]

        # Créer l'embed
        embed = discord.Embed(
            title="🚫 Statut du Système Anti-Spam",
            color=discord.Color.blue() if config["enabled"] else discord.Color.greyple()
        )

        # Statut général
        status_value = "✅ Activé" if config["enabled"] else "❌ Désactivé"
        embed.add_field(name="📊 Statut", value=status_value, inline=True)
        embed.add_field(name="📨 Limite messages", value=f"{config['message_limit']}", inline=True)
        embed.add_field(name="⏱️ Fenêtre temps", value=f"{config['time_window']}s", inline=True)

        # Configuration
        embed.add_field(name="⚖️ Sanction", value=config["sanction_type"].title(), inline=True)
        if config["sanction_type"] == "timeout":
            embed.add_field(name="⏰ Durée timeout", value=f"{config['timeout_duration'] // 60} min", inline=True)
        embed.add_field(name="🗑️ Supprimer messages", value="✅ Oui" if config["delete_messages"] else "❌ Non", inline=True)

        # Canal de logs
        log_text = log_channel.mention if log_channel else "❌ Non configuré"
        embed.add_field(name="📝 Canal logs", value=log_text, inline=False)

        # Rôles immunisés
        if immune_roles:
            roles_text = ", ".join([role.mention for role in immune_roles])
            embed.add_field(name="🛡️ Rôles immunisés", value=roles_text, inline=False)

        # Canaux ignorés
        if ignored_channels:
            channels_text = ", ".join([channel.mention for channel in ignored_channels])
            embed.add_field(name="🚫 Canaux ignorés", value=channels_text, inline=False)

        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clear_spam_warnings", description="Effacer les avertissements anti-spam d'un utilisateur")
    @app_commands.default_permissions(administrator=True)
    async def clear_spam_warnings(self, inter: discord.Interaction, user: discord.User):
        warnings = load_spam_warnings()
        user_id = str(user.id)

        if user_id in warnings:
            del warnings[user_id]
            save_spam_warnings(warnings)

            embed = discord.Embed(
                title="🧹 Avertissements effacés",
                description=f"Les avertissements anti-spam de {user.mention} ont été supprimés.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="ℹ️ Aucun avertissement",
                description=f"{user.mention} n'a aucun avertissement anti-spam.",
                color=discord.Color.blue()
            )

        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="test_antispam", description="Tester le système anti-spam (ATTENTION: peut vous sanctionner)")
    @app_commands.default_permissions(administrator=True)
    async def test_antispam(self, inter: discord.Interaction):
        config = load_antispam_config()

        if not config["enabled"]:
            await inter.response.send_message("❌ Le système anti-spam est désactivé. Activez-le avec `/toggle_antispam`.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⚠️ Test Anti-Spam",
            description="**ATTENTION:** Ce test enverra plusieurs messages rapidement et pourrait déclencher une sanction !",
            color=discord.Color.orange()
        )
        embed.add_field(name="📊 Configuration actuelle", value=f"**Limite:** {config['message_limit']} messages\n**Fenêtre:** {config['time_window']} secondes\n**Sanction:** {config['sanction_type'].title()}", inline=False)
        embed.add_field(name="🛡️ Protection", value="Assurez-vous d'avoir l'immunité ou testez dans un canal ignoré !", inline=False)
        embed.add_field(name="🎯 Instructions", value="Après avoir cliqué OK, envoyez rapidement plusieurs messages dans ce canal pour déclencher l'anti-spam.", inline=False)

        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="antispam_stats", description="Afficher les statistiques des avertissements anti-spam")
    @app_commands.default_permissions(administrator=True)
    async def antispam_stats(self, inter: discord.Interaction, user: discord.User = None):
        warnings = load_spam_warnings()

        if user:
            # Statistiques pour un utilisateur spécifique
            user_id = str(user.id)
            if user_id in warnings:
                user_data = warnings[user_id]
                embed = discord.Embed(
                    title=f"📊 Statistiques Anti-Spam - {user.display_name}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="⚠️ Avertissements", value=f"{user_data['count']}", inline=True)

                if user_data["timestamps"]:
                    last_warning = datetime.fromisoformat(user_data["timestamps"][-1])
                    embed.add_field(name="📅 Dernier avertissement", value=f"<t:{int(last_warning.timestamp())}:R>", inline=True)

                embed.set_thumbnail(url=user.display_avatar.url)
            else:
                embed = discord.Embed(
                    title=f"📊 Statistiques Anti-Spam - {user.display_name}",
                    description="Aucun avertissement enregistré.",
                    color=discord.Color.green()
                )
        else:
            # Statistiques globales
            total_users = len(warnings)
            total_warnings = sum(data["count"] for data in warnings.values())

            embed = discord.Embed(
                title="📊 Statistiques Anti-Spam Globales",
                color=discord.Color.blue()
            )
            embed.add_field(name="👥 Utilisateurs avec avertissements", value=f"{total_users}", inline=True)
            embed.add_field(name="⚠️ Total avertissements", value=f"{total_warnings}", inline=True)

            if warnings:
                # Top 5 des utilisateurs avec le plus d'avertissements
                sorted_users = sorted(warnings.items(), key=lambda x: x[1]["count"], reverse=True)
                top_users = sorted_users[:5]

                top_text = []
                for user_id, data in top_users:
                    user = inter.client.get_user(int(user_id))
                    user_name = user.display_name if user else f"ID: {user_id}"
                    top_text.append(f"**{user_name}:** {data['count']} avertissements")

                embed.add_field(name="🏆 Top Spammers", value="\n".join(top_text) if top_text else "Aucun", inline=False)

        await inter.response.send_message(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(AntiSpam(client))