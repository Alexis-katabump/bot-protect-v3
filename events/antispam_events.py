import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque

def load_antispam_config():
    if os.path.exists("antispam_config.json"):
        with open("antispam_config.json", "r") as file:
            data = json.load(file)
            default_config = {
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

def load_spam_warnings():
    if os.path.exists("spam_warnings.json"):
        with open("spam_warnings.json", "r") as file:
            return json.load(file)
    return {}

def save_spam_warnings(data):
    with open("spam_warnings.json", "w") as file:
        json.dump(data, file, indent=2)

class AntiSpamEvents(commands.Cog):
    def __init__(self, client):
        self.client = client
        # Stocker les messages récents par utilisateur
        self.user_messages = defaultdict(lambda: deque())

    def cleanup_old_messages(self, user_id, time_window):
        """Nettoyer les anciens messages au-delà de la fenêtre de temps"""
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(seconds=time_window)

        # Supprimer les messages trop anciens
        while (self.user_messages[user_id] and
               self.user_messages[user_id][0] < cutoff_time):
            self.user_messages[user_id].popleft()

    def is_user_immune(self, member, immune_role_ids):
        """Vérifier si l'utilisateur a un rôle immunisé"""
        if member.guild_permissions.administrator:
            return True

        user_role_ids = [role.id for role in member.roles]
        return any(role_id in immune_role_ids for role_id in user_role_ids)

    async def log_spam_detection(self, member, message_count, sanction, config):
        """Logger la détection de spam"""
        if config["log_channel_id"] == 0:
            return

        log_channel = member.guild.get_channel(config["log_channel_id"])
        if not log_channel:
            return

        embed = discord.Embed(
            title="🚫 Spam Détecté",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="👤 Utilisateur", value=f"{member.mention} ({member.id})", inline=True)
        embed.add_field(name="📨 Messages envoyés", value=f"{message_count} en {config['time_window']}s", inline=True)
        embed.add_field(name="⚖️ Sanction appliquée", value=sanction.title(), inline=True)

        if hasattr(member, 'joined_at') and member.joined_at:
            embed.add_field(name="📅 Membre depuis", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Serveur: {member.guild.name}")

        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            pass

    async def apply_sanction(self, member, messages_to_delete, config):
        """Appliquer la sanction selon la configuration"""
        sanction_type = config["sanction_type"]

        try:
            # Supprimer les messages de spam si configuré
            if config["delete_messages"] and messages_to_delete:
                for message in messages_to_delete:
                    try:
                        await message.delete()
                    except (discord.NotFound, discord.Forbidden):
                        continue

            # Appliquer la sanction
            if sanction_type == "timeout":
                timeout_until = datetime.now(timezone.utc) + timedelta(seconds=config["timeout_duration"])
                await member.timeout(timeout_until, reason="Spam détecté par l'anti-spam")
                await self.log_spam_detection(member, len(messages_to_delete), "Timeout", config)

            elif sanction_type == "kick":
                await member.kick(reason="Spam détecté par l'anti-spam")
                await self.log_spam_detection(member, len(messages_to_delete), "Kick", config)

            elif sanction_type == "ban":
                ban_duration = config.get("ban_duration", 0)
                if ban_duration > 0:
                    # Ban temporaire (nécessite une gestion externe pour débannir)
                    await member.ban(reason=f"Spam détecté par l'anti-spam - Ban de {ban_duration} jours", delete_message_days=1)
                else:
                    await member.ban(reason="Spam détecté par l'anti-spam", delete_message_days=1)
                await self.log_spam_detection(member, len(messages_to_delete), "Ban", config)

            elif sanction_type == "warn":
                # Système d'avertissements
                warnings = load_spam_warnings()
                user_id = str(member.id)

                if user_id not in warnings:
                    warnings[user_id] = {"count": 0, "timestamps": []}

                warnings[user_id]["count"] += 1
                warnings[user_id]["timestamps"].append(datetime.now(timezone.utc).isoformat())
                save_spam_warnings(warnings)

                # Vérifier si le seuil d'avertissements est atteint
                if warnings[user_id]["count"] >= config["warn_threshold"]:
                    # Appliquer un timeout après trop d'avertissements
                    timeout_until = datetime.now(timezone.utc) + timedelta(seconds=config["timeout_duration"])
                    await member.timeout(timeout_until, reason=f"Trop d'avertissements spam ({warnings[user_id]['count']})")
                    await self.log_spam_detection(member, len(messages_to_delete), f"Timeout (Avertissement {warnings[user_id]['count']})", config)
                else:
                    await self.log_spam_detection(member, len(messages_to_delete), f"Avertissement {warnings[user_id]['count']}", config)

        except discord.Forbidden:
            # Pas les permissions pour appliquer la sanction
            await self.log_spam_detection(member, len(messages_to_delete), "Échec - Permissions insuffisantes", config)
        except Exception as e:
            print(f"Erreur lors de l'application de la sanction: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignorer les bots
        if message.author.bot:
            return

        # Ignorer les messages privés
        if not message.guild:
            return

        config = load_antispam_config()

        # Vérifier si le système est activé
        if not config["enabled"]:
            return

        # Vérifier si le canal est ignoré
        if message.channel.id in config["ignored_channels"]:
            return

        # Vérifier si l'utilisateur a l'immunité
        if self.is_user_immune(message.author, config["immune_roles"]):
            return

        # Ajouter le timestamp du message actuel (utiliser UTC pour la cohérence)
        now = datetime.now(timezone.utc)
        user_id = message.author.id
        self.user_messages[user_id].append(now)

        # Nettoyer les anciens messages
        self.cleanup_old_messages(user_id, config["time_window"])

        # Vérifier si la limite est dépassée
        message_count = len(self.user_messages[user_id])

        if message_count >= config["message_limit"]:
            # SPAM DÉTECTÉ !

            # Récupérer les messages récents pour les supprimer
            messages_to_delete = []
            if config["delete_messages"]:
                try:
                    # Récupérer les messages récents de cet utilisateur dans ce canal
                    cutoff_time = now - timedelta(seconds=config["time_window"])
                    async for msg in message.channel.history(limit=50):
                        if (msg.author.id == user_id and
                            msg.created_at >= cutoff_time and
                            len(messages_to_delete) < config["message_limit"]):
                            messages_to_delete.append(msg)
                except discord.Forbidden:
                    pass

            # Appliquer la sanction
            await self.apply_sanction(message.author, messages_to_delete, config)

            # Réinitialiser le compteur pour cet utilisateur
            self.user_messages[user_id].clear()

            # Envoyer un message d'avertissement dans le canal (optionnel)
            try:
                warning_embed = discord.Embed(
                    title="🚫 Spam Détecté",
                    description=f"⚠️ {message.author.mention} a été sanctionné pour spam.",
                    color=discord.Color.red()
                )
                warning_embed.add_field(
                    name="📊 Détails",
                    value=f"**Messages:** {message_count} en {config['time_window']}s\n**Limite:** {config['message_limit']} messages\n**Sanction:** {config['sanction_type'].title()}",
                    inline=False
                )

                warning_msg = await message.channel.send(embed=warning_embed)

                # Supprimer le message d'avertissement après 10 secondes
                await warning_msg.delete(delay=10)

            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Nettoyer le cache quand un message est supprimé"""
        if message.author.bot or not message.guild:
            return

        # Supprimer le message du cache s'il existe
        user_id = message.author.id
        if user_id in self.user_messages:
            # Rechercher et supprimer le timestamp correspondant (approximatif)
            message_time = message.created_at
            messages_deque = self.user_messages[user_id]

            # Convertir en liste pour la manipulation
            messages_list = list(messages_deque)

            # Chercher le timestamp le plus proche
            for i, timestamp in enumerate(messages_list):
                if abs((timestamp - message_time).total_seconds()) < 1:  # Tolérance de 1 seconde
                    messages_list.pop(i)
                    break

            # Reconvertir en deque
            self.user_messages[user_id] = deque(messages_list)

async def setup(client):
    await client.add_cog(AntiSpamEvents(client))