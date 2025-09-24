import discord
from discord.ext import commands
import sys
import os
from datetime import datetime, timezone, timedelta  # Added timedelta import

# Ajouter le dossier parent au path pour importer utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.stats_database import StatsDatabase

class StatsEvents(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.stats_db = StatsDatabase()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Enregistrer chaque message pour les statistiques"""
        # Ignorer les bots
        if message.author.bot:
            return

        # Ignorer les messages privés
        if not message.guild:
            return

        # Enregistrer le message
        message_length = len(message.content)
        self.stats_db.log_message(
            user_id=message.author.id,
            channel_id=message.channel.id,
            guild_id=message.guild.id,
            message_length=message_length
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Enregistrer les arrivées de membres"""
        self.stats_db.log_member_event(
            user_id=member.id,
            guild_id=member.guild.id,
            event_type='join'
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Enregistrer les départs de membres"""
        self.stats_db.log_member_event(
            user_id=member.id,
            guild_id=member.guild.id,
            event_type='leave'
        )

    @commands.Cog.listener()
    async def on_ready(self):
        """Calculer les statistiques quotidiennes au démarrage"""
        print("📊 Système de statistiques initialisé")

        # Calculer les statistiques pour hier si pas encore fait
        yesterday = (datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) -
                    timedelta(days=1)).strftime('%Y-%m-%d')

        for guild in self.client.guilds:
            try:
                self.stats_db.calculate_daily_stats(guild.id, yesterday)
                print(f"✅ Statistiques calculées pour {guild.name}")
            except Exception as e:
                print(f"❌ Erreur calcul stats pour {guild.name}: {e}")

async def setup(client):
    await client.add_cog(StatsEvents(client))