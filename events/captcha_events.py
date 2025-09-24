import discord
from discord.ext import commands
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

class CaptchaEvents(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.verification_tasks = {}

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Quand un membre rejoint le serveur, lui assigner le rôle non vérifié et envoyer le captcha"""
        if member.bot:
            return

        config = load_captcha_config()
        if not config["enabled"]:
            return

        guild = member.guild
        unverified_role = discord.utils.get(guild.roles, id=config["unverified_role_id"])
        verification_channel = guild.get_channel(config["verification_channel_id"])

        if not unverified_role or not verification_channel:
            return

        # Assigner le rôle non vérifié (le rôle gère déjà les permissions du canal)
        try:
            await member.add_roles(unverified_role, reason="Nouveau membre - en attente de vérification")
        except discord.Forbidden:
            return

        # Générer un captcha
        captcha_code = generate_captcha()

        # Enregistrer dans les vérifications en attente avec plus d'informations
        pending = load_pending_verifications()
        pending[str(member.id)] = {
            "captcha_code": captcha_code,
            "attempts": config["max_attempts"],
            "max_attempts": config["max_attempts"],
            "timestamp": datetime.now().isoformat(),
            "guild_id": guild.id,
            "guild_name": guild.name,
            "user_name": f"{member.name}#{member.discriminator}",
            "user_id": member.id,
            "timeout_minutes": config["timeout_minutes"],
            "kick_on_fail": config["kick_on_fail"],
            "status": "pending"
        }
        save_pending_verifications(pending)

        # Créer l'embed de captcha
        embed = create_captcha_embed(captcha_code, config["max_attempts"], config["timeout_minutes"])

        try:
            # Envoyer le captcha dans le canal de vérification
            message = await verification_channel.send(
                f"👋 {member.mention} Bienvenue sur **{guild.name}** !",
                embed=embed
            )

            # Démarrer le timer de vérification
            task = asyncio.create_task(self.verification_timeout(member, config["timeout_minutes"]))
            self.verification_tasks[member.id] = task

        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        """Gérer les tentatives de vérification captcha"""
        if message.author.bot:
            return

        config = load_captcha_config()
        if not config["enabled"]:
            return

        # Vérifier si le message est dans le canal de vérification
        if message.channel.id != config["verification_channel_id"]:
            return

        pending = load_pending_verifications()
        user_id = str(message.author.id)

        if user_id not in pending:
            return

        user_data = pending[user_id]
        expected_code = user_data["captcha_code"]

        # Supprimer le message de l'utilisateur pour garder le canal propre
        try:
            await message.delete()
        except discord.Forbidden:
            pass

        # Vérifier le code
        if message.content.strip() == expected_code:
            # Captcha réussi !
            await self.verify_member_success(message.author, message.guild)
        else:
            # Captcha échoué
            user_data["attempts"] -= 1

            if user_data["attempts"] <= 0:
                # Plus d'tentatives
                await self.verify_member_failed(message.author, message.guild, config["kick_on_fail"])
            else:
                # Envoyer un nouveau captcha
                await self.send_new_captcha(message.author, message.guild, user_data["attempts"])
                pending[user_id] = user_data
                save_pending_verifications(pending)

    async def verify_member_success(self, member, guild):
        """Vérification réussie - donner accès au serveur"""
        config = load_captcha_config()

        verified_role = discord.utils.get(guild.roles, id=config["verification_role_id"])
        unverified_role = discord.utils.get(guild.roles, id=config["unverified_role_id"])
        verification_channel = guild.get_channel(config["verification_channel_id"])

        try:
            # Ajouter le rôle vérifié et supprimer le rôle non vérifié
            if verified_role:
                await member.add_roles(verified_role, reason="Captcha vérifié avec succès")
            if unverified_role and unverified_role in member.roles:
                await member.remove_roles(unverified_role, reason="Captcha vérifié avec succès")


            # Mettre à jour le statut dans les vérifications et supprimer
            pending = load_pending_verifications()
            if str(member.id) in pending:
                # Marquer comme réussi avant de supprimer (pour les logs)
                pending[str(member.id)]["status"] = "verified_success"
                pending[str(member.id)]["completion_time"] = datetime.now().isoformat()
                save_pending_verifications(pending)

                # Supprimer après un court délai (pour permettre la sauvegarde des logs)
                del pending[str(member.id)]
                save_pending_verifications(pending)

            # Annuler le timer
            if member.id in self.verification_tasks:
                self.verification_tasks[member.id].cancel()
                del self.verification_tasks[member.id]

            # Message de succès
            if verification_channel:
                embed = discord.Embed(
                    title="✅ Vérification réussie !",
                    description=f"{member.mention} a été vérifié avec succès ! Bienvenue sur le serveur ! 🎉",
                    color=discord.Color.green()
                )
                await verification_channel.send(embed=embed)

                # Supprimer le message après 10 secondes
                await asyncio.sleep(10)
                try:
                    async for msg in verification_channel.history(limit=50):
                        if msg.embeds and msg.embeds[0].title == "✅ Vérification réussie !":
                            if f"{member.mention}" in msg.embeds[0].description:
                                await msg.delete()
                                break
                except:
                    pass

        except discord.Forbidden:
            pass

    async def verify_member_failed(self, member, guild, kick_on_fail):
        """Vérification échouée - gérer l'échec"""
        verification_channel = guild.get_channel(load_captcha_config()["verification_channel_id"])

        # Mettre à jour le statut dans les vérifications
        pending = load_pending_verifications()
        if str(member.id) in pending:
            pending[str(member.id)]["status"] = "failed_kicked" if kick_on_fail else "failed_no_kick"
            pending[str(member.id)]["completion_time"] = datetime.now().isoformat()
            save_pending_verifications(pending)

            # Supprimer après marquage
            del pending[str(member.id)]
            save_pending_verifications(pending)

        # Annuler le timer
        if member.id in self.verification_tasks:
            self.verification_tasks[member.id].cancel()
            del self.verification_tasks[member.id]


        if verification_channel:
            if kick_on_fail:
                embed = discord.Embed(
                    title="❌ Vérification échouée",
                    description=f"{member.mention} a échoué à la vérification et va être expulsé.",
                    color=discord.Color.red()
                )
                await verification_channel.send(embed=embed)

                # Expulser le membre
                try:
                    await member.kick(reason="Échec de la vérification captcha")
                except discord.Forbidden:
                    pass
            else:
                embed = discord.Embed(
                    title="❌ Vérification échouée",
                    description=f"{member.mention} a échoué à la vérification. Contactez un administrateur.",
                    color=discord.Color.red()
                )
                await verification_channel.send(embed=embed)

    async def send_new_captcha(self, member, guild, attempts_left):
        """Envoyer un nouveau captcha après un échec"""
        config = load_captcha_config()
        verification_channel = guild.get_channel(config["verification_channel_id"])

        if not verification_channel:
            return

        # Générer un nouveau captcha
        new_captcha = generate_captcha()

        # Mettre à jour les données en attente
        pending = load_pending_verifications()
        pending[str(member.id)]["captcha_code"] = new_captcha
        save_pending_verifications(pending)

        # Créer l'embed d'erreur
        error_embed = discord.Embed(
            title="❌ Code incorrect",
            description=f"{member.mention} Code incorrect ! Il vous reste **{attempts_left}** tentative(s).",
            color=discord.Color.red()
        )
        await verification_channel.send(embed=error_embed)

        # Envoyer le nouveau captcha
        embed = create_captcha_embed(new_captcha, attempts_left, config["timeout_minutes"])
        await verification_channel.send(embed=embed)

    async def verification_timeout(self, member, timeout_minutes):
        """Gérer le timeout de vérification"""
        try:
            await asyncio.sleep(timeout_minutes * 60)  # Convertir en secondes

            # Vérifier si le membre est toujours en attente
            pending = load_pending_verifications()
            if str(member.id) in pending:
                config = load_captcha_config()
                await self.verify_member_failed(member, member.guild, config["kick_on_fail"])

                verification_channel = member.guild.get_channel(config["verification_channel_id"])
                if verification_channel:
                    embed = discord.Embed(
                        title="⏰ Temps écoulé",
                        description=f"{member.mention} n'a pas réussi à se vérifier dans les temps.",
                        color=discord.Color.orange()
                    )
                    await verification_channel.send(embed=embed)

        except asyncio.CancelledError:
            # Timer annulé (vérification réussie)
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Nettoyer les données quand un membre quitte"""
        # Supprimer des vérifications en attente
        pending = load_pending_verifications()
        if str(member.id) in pending:
            del pending[str(member.id)]
            save_pending_verifications(pending)

        # Annuler le timer si il existe
        if member.id in self.verification_tasks:
            self.verification_tasks[member.id].cancel()
            del self.verification_tasks[member.id]

async def setup(client):
    await client.add_cog(CaptchaEvents(client))