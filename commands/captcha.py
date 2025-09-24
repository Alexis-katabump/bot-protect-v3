import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import string
import asyncio
from datetime import datetime, timedelta

def load_captcha_config():
    if os.path.exists("captcha_config.json"):
        with open("captcha_config.json", "r") as file:
            data = json.load(file)
            default_config = {
                "enabled": False,
                "verification_channel_id": 0,
                "verification_role_id": 0,
                "unverified_role_id": 0,
                "timeout_minutes": 5,
                "kick_on_fail": True,
                "max_attempts": 3
            }
            return {**default_config, **data}
    return {
        "enabled": False,
        "verification_channel_id": 0,
        "verification_role_id": 0,
        "unverified_role_id": 0,
        "timeout_minutes": 5,
        "kick_on_fail": True,
        "max_attempts": 3
    }

def save_captcha_config(config):
    with open("captcha_config.json", "w") as file:
        json.dump(config, file)

def load_pending_verifications():
    if os.path.exists("pending_verifications.json"):
        with open("pending_verifications.json", "r") as file:
            return json.load(file)
    return {}

def save_pending_verifications(data):
    with open("pending_verifications.json", "w") as file:
        json.dump(data, file)

def generate_captcha():
    """Génère un captcha simple avec des lettres et chiffres"""
    characters = string.ascii_uppercase + string.digits
    # Éviter les caractères confus comme 0, O, 1, I
    characters = characters.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    return ''.join(random.choices(characters, k=5))

def create_captcha_embed(captcha_code, attempts_left, timeout_minutes):
    """Crée l'embed pour le captcha"""
    embed = discord.Embed(
        title="🔒 Vérification Captcha",
        description=f"Bienvenue ! Pour accéder au serveur, veuillez taper le code suivant :",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📋 Code à taper:",
        value=f"```{captcha_code}```",
        inline=False
    )
    embed.add_field(
        name="⏰ Temps restant:",
        value=f"{timeout_minutes} minutes",
        inline=True
    )
    embed.add_field(
        name="🔄 Tentatives restantes:",
        value=f"{attempts_left}",
        inline=True
    )
    embed.add_field(
        name="ℹ️ Instructions:",
        value="Tapez exactement le code affiché ci-dessus (sensible à la casse)",
        inline=False
    )
    embed.set_footer(text="⚠️ Attention : Vous serez expulsé si vous échouez ou si le temps expire")
    return embed

class Captcha(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="setup_captcha", description="Configurer le système de captcha")
    @app_commands.default_permissions(administrator=True)
    async def setup_captcha(self, inter: discord.Interaction):
        # Répondre immédiatement pour éviter le timeout
        await inter.response.send_message("🔄 Configuration du captcha en cours...", ephemeral=True)

        guild = inter.guild
        config = load_captcha_config()

        try:
            # Créer le rôle "Non Vérifié" si il n'existe pas
            unverified_role = discord.utils.get(guild.roles, id=config["unverified_role_id"])
            if not unverified_role:
                unverified_role = await guild.create_role(
                    name="Non Vérifié",
                    color=discord.Color.red(),
                    reason="Rôle pour les membres non vérifiés"
                )
                config["unverified_role_id"] = unverified_role.id


            # Créer le rôle "Vérifié" si il n'existe pas
            verified_role = discord.utils.get(guild.roles, id=config["verification_role_id"])
            if not verified_role:
                verified_role = await guild.create_role(
                    name="Vérifié",
                    color=discord.Color.green(),
                    reason="Rôle pour les membres vérifiés"
                )
                config["verification_role_id"] = verified_role.id

            # Créer le canal de vérification si il n'existe pas
            verification_channel = discord.utils.get(guild.text_channels, id=config["verification_channel_id"])
            if not verification_channel:
                # Créer une catégorie pour la vérification
                verification_category = await guild.create_category("🔒 Vérification")

                verification_channel = await guild.create_text_channel(
                    "verification",
                    category=verification_category,
                    reason="Canal de vérification captcha"
                )
                config["verification_channel_id"] = verification_channel.id

            # Toujours reconfigurer les permissions du canal de vérification (même s'il existe déjà)
            await verification_channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
            await verification_channel.set_permissions(unverified_role, read_messages=True, send_messages=True, view_channel=True)
            await verification_channel.set_permissions(verified_role, read_messages=False, view_channel=False)

            # S'assurer que le bot peut toujours accéder au canal
            await verification_channel.set_permissions(guild.me, read_messages=True, send_messages=True, manage_messages=True, view_channel=True)

            # Maintenant supprimer les permissions de voir les AUTRES canaux pour le rôle non vérifié
            if unverified_role:
                for channel in guild.channels:
                    if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                        try:
                            # Ne pas bloquer l'accès au canal de vérification et sa catégorie
                            if channel.id != verification_channel.id and channel.id != verification_channel.category.id:
                                await channel.set_permissions(unverified_role, read_messages=False, connect=False)
                        except discord.Forbidden:
                            continue  # Ignorer si pas de permissions

            save_captcha_config(config)

            # Mettre à jour la réponse avec les résultats
            embed = discord.Embed(
                title="✅ Configuration du Captcha terminée",
                description="Le système de captcha a été configuré avec succès !",
                color=discord.Color.green()
            )
            embed.add_field(name="Canal de vérification", value=verification_channel.mention, inline=False)
            embed.add_field(name="Rôle vérifié", value=verified_role.mention, inline=True)
            embed.add_field(name="Rôle non vérifié", value=unverified_role.mention, inline=True)
            embed.add_field(name="Statut", value="❌ Désactivé" if not config["enabled"] else "✅ Activé", inline=False)

            await inter.edit_original_response(content=None, embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur de configuration",
                description=f"Une erreur s'est produite : {str(e)}",
                color=discord.Color.red()
            )
            await inter.edit_original_response(content=None, embed=error_embed)

    @app_commands.command(name="toggle_captcha", description="Activer ou désactiver le système de captcha")
    @app_commands.default_permissions(administrator=True)
    async def toggle_captcha(self, inter: discord.Interaction):
        config = load_captcha_config()
        config["enabled"] = not config["enabled"]
        save_captcha_config(config)

        status = "✅ activé" if config["enabled"] else "❌ désactivé"
        embed = discord.Embed(
            title="🔄 Captcha mis à jour",
            description=f"Le système de captcha est maintenant {status}",
            color=discord.Color.green() if config["enabled"] else discord.Color.red()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="captcha_config", description="Configurer les paramètres du captcha")
    @app_commands.default_permissions(administrator=True)
    async def captcha_config(self, inter: discord.Interaction,
                           timeout_minutes: int = 5,
                           max_attempts: int = 3,
                           kick_on_fail: bool = True):
        config = load_captcha_config()
        config["timeout_minutes"] = max(1, min(timeout_minutes, 30))  # Entre 1 et 30 minutes
        config["max_attempts"] = max(1, min(max_attempts, 10))  # Entre 1 et 10 tentatives
        config["kick_on_fail"] = kick_on_fail
        save_captcha_config(config)

        embed = discord.Embed(
            title="⚙️ Configuration du Captcha mise à jour",
            color=discord.Color.blue()
        )
        embed.add_field(name="⏰ Temps limite", value=f"{config['timeout_minutes']} minutes", inline=True)
        embed.add_field(name="🔄 Tentatives max", value=f"{config['max_attempts']}", inline=True)
        embed.add_field(name="👢 Kick en cas d'échec", value="✅ Oui" if config['kick_on_fail'] else "❌ Non", inline=True)

        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="verify_user", description="Forcer la vérification d'un utilisateur")
    @app_commands.default_permissions(administrator=True)
    async def verify_user(self, inter: discord.Interaction, member: discord.Member):
        config = load_captcha_config()

        if config["verification_role_id"] == 0:
            await inter.response.send_message("❌ Le système de captcha n'est pas configuré. Utilisez `/setup_captcha` d'abord.", ephemeral=True)
            return

        verified_role = discord.utils.get(inter.guild.roles, id=config["verification_role_id"])
        unverified_role = discord.utils.get(inter.guild.roles, id=config["unverified_role_id"])

        if verified_role:
            await member.add_roles(verified_role, reason="Vérification manuelle par un administrateur")
        if unverified_role and unverified_role in member.roles:
            await member.remove_roles(unverified_role, reason="Vérification manuelle par un administrateur")

        # Supprimer de la liste des vérifications en attente
        pending = load_pending_verifications()
        if str(member.id) in pending:
            del pending[str(member.id)]
            save_pending_verifications(pending)

        embed = discord.Embed(
            title="✅ Utilisateur vérifié",
            description=f"{member.mention} a été vérifié manuellement.",
            color=discord.Color.green()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="captcha_status", description="Afficher le statut du système de captcha")
    @app_commands.default_permissions(administrator=True)
    async def captcha_status(self, inter: discord.Interaction):
        config = load_captcha_config()
        guild = inter.guild

        # Obtenir les informations sur les rôles et canaux
        verified_role = discord.utils.get(guild.roles, id=config["verification_role_id"])
        unverified_role = discord.utils.get(guild.roles, id=config["unverified_role_id"])
        verification_channel = guild.get_channel(config["verification_channel_id"])

        # Compter les membres en attente
        pending = load_pending_verifications()
        pending_count = len([p for p in pending.values() if p.get("guild_id") == guild.id])

        # Créer l'embed de statut
        embed = discord.Embed(
            title="🔒 Statut du Système Captcha",
            color=discord.Color.blue() if config["enabled"] else discord.Color.greyple()
        )

        # Statut général
        status_value = "✅ Activé" if config["enabled"] else "❌ Désactivé"
        embed.add_field(name="📊 Statut", value=status_value, inline=True)
        embed.add_field(name="👥 En attente", value=f"{pending_count} membre(s)", inline=True)
        embed.add_field(name="⏰ Timeout", value=f"{config['timeout_minutes']} min", inline=True)

        # Configuration
        embed.add_field(name="🔄 Tentatives max", value=f"{config['max_attempts']}", inline=True)
        embed.add_field(name="👢 Kick si échec", value="✅ Oui" if config['kick_on_fail'] else "❌ Non", inline=True)
        embed.add_field(name="🆔 Guild ID", value=f"{guild.id}", inline=True)

        # Rôles et canaux
        verification_text = verification_channel.mention if verification_channel else "❌ Non configuré"
        verified_text = verified_role.mention if verified_role else "❌ Non configuré"
        unverified_text = unverified_role.mention if unverified_role else "❌ Non configuré"

        embed.add_field(name="📝 Canal vérification", value=verification_text, inline=False)
        embed.add_field(name="✅ Rôle vérifié", value=verified_text, inline=True)
        embed.add_field(name="❌ Rôle non vérifié", value=unverified_text, inline=True)

        # Statistiques des membres
        if verified_role:
            verified_members = len(verified_role.members)
            embed.add_field(name="👤 Membres vérifiés", value=f"{verified_members}", inline=True)

        if unverified_role:
            unverified_members = len(unverified_role.members)
            embed.add_field(name="❓ Membres non vérifiés", value=f"{unverified_members}", inline=True)

        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clear_pending", description="Effacer toutes les vérifications en attente")
    @app_commands.default_permissions(administrator=True)
    async def clear_pending(self, inter: discord.Interaction):
        pending = load_pending_verifications()
        guild_pending = {k: v for k, v in pending.items() if v.get("guild_id") == inter.guild.id}

        # Supprimer les vérifications pour ce serveur
        for user_id in guild_pending.keys():
            if user_id in pending:
                del pending[user_id]

        save_pending_verifications(pending)

        embed = discord.Embed(
            title="🧹 Vérifications effacées",
            description=f"{len(guild_pending)} vérification(s) en attente ont été supprimées.",
            color=discord.Color.orange()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="send_welcome_message", description="Envoyer un message d'accueil dans le salon de vérification")
    @app_commands.default_permissions(administrator=True)
    async def send_welcome_message(self, inter: discord.Interaction):
        config = load_captcha_config()

        if config["verification_channel_id"] == 0:
            await inter.response.send_message("❌ Le système de captcha n'est pas configuré. Utilisez `/setup_captcha` d'abord.", ephemeral=True)
            return

        verification_channel = inter.guild.get_channel(config["verification_channel_id"])
        if not verification_channel:
            await inter.response.send_message("❌ Canal de vérification non trouvé.", ephemeral=True)
            return

        # Message d'accueil permanent
        welcome_embed = discord.Embed(
            title="🔒 Bienvenue sur le serveur !",
            description="**Pour accéder au serveur, vous devez passer la vérification captcha.**",
            color=discord.Color.blue()
        )
        welcome_embed.add_field(
            name="📋 Instructions:",
            value="• Quand vous rejoignez le serveur, un captcha sera automatiquement généré\n• Tapez exactement le code affiché (sensible à la casse)\n• Vous avez plusieurs tentatives et un temps limité",
            inline=False
        )
        welcome_embed.add_field(
            name="⚠️ Important:",
            value="• Ne partagez pas vos codes\n• En cas de problème, contactez un modérateur\n• Les messages sont automatiquement supprimés pour garder le canal propre",
            inline=False
        )
        welcome_embed.add_field(
            name="🎯 Objectif:",
            value="Cette vérification permet de protéger notre communauté contre les bots et les utilisateurs malveillants.",
            inline=False
        )
        welcome_embed.set_footer(text="Merci de votre compréhension et bienvenue ! 🎉")

        try:
            await verification_channel.send(embed=welcome_embed)
            await inter.response.send_message("✅ Message d'accueil envoyé dans le salon de vérification.", ephemeral=True)
        except discord.Forbidden:
            await inter.response.send_message("❌ Impossible d'envoyer le message. Vérifiez les permissions du bot.", ephemeral=True)

    @app_commands.command(name="test_captcha", description="Tester le système de captcha en simulant un nouveau membre")
    @app_commands.default_permissions(administrator=True)
    async def test_captcha(self, inter: discord.Interaction, member: discord.Member):
        config = load_captcha_config()

        if not config["enabled"]:
            await inter.response.send_message("❌ Le système de captcha est désactivé. Utilisez `/toggle_captcha` pour l'activer.", ephemeral=True)
            return

        guild = inter.guild
        unverified_role = discord.utils.get(guild.roles, id=config["unverified_role_id"])
        verification_channel = guild.get_channel(config["verification_channel_id"])

        if not unverified_role or not verification_channel:
            await inter.response.send_message("❌ Le système de captcha n'est pas correctement configuré. Utilisez `/setup_captcha`.", ephemeral=True)
            return

        # Simuler l'événement on_member_join
        try:
            await member.add_roles(unverified_role, reason="Test captcha - simulation nouveau membre")

            # Générer un captcha de test
            captcha_code = generate_captcha()

            # Créer l'embed de test
            embed = create_captcha_embed(captcha_code, config["max_attempts"], config["timeout_minutes"])

            # Envoyer dans le canal de vérification
            await verification_channel.send(f"🧪 **TEST CAPTCHA** pour {member.mention}", embed=embed)

            await inter.response.send_message(f"✅ Test captcha lancé pour {member.mention}. Code: `{captcha_code}`", ephemeral=True)

        except discord.Forbidden:
            await inter.response.send_message("❌ Permissions insuffisantes pour effectuer le test.", ephemeral=True)

async def setup(client):
    await client.add_cog(Captcha(client))