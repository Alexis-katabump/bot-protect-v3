import discord
from discord.ext import commands
from discord import app_commands
import sys
import os
from datetime import datetime, timezone
import asyncio

# Ajouter le dossier parent au path pour importer utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.stats_database import StatsDatabase
from utils.stats_visualizer import StatsVisualizer

class StatsView(discord.ui.View):
    def __init__(self, guild, stats_db, visualizer):
        super().__init__(timeout=300)
        self.guild = guild
        self.stats_db = stats_db
        self.visualizer = visualizer

    @discord.ui.button(label="📊 Vue d'ensemble", style=discord.ButtonStyle.primary)
    async def overview_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        try:
            # Récupérer toutes les données
            message_stats = self.stats_db.get_message_stats(self.guild.id, days=7)
            member_stats = self.stats_db.get_member_stats(self.guild.id, days=7)

            stats_data = {
                'message_stats': message_stats,
                'member_stats': member_stats
            }

            # Créer le graphique
            chart = self.visualizer.create_overview_chart(stats_data, self.guild)

            if chart:
                file = discord.File(chart, filename="overview.png")
                embed = discord.Embed(
                    title="📊 Dashboard des Statistiques",
                    description=f"Vue d'ensemble des 7 derniers jours pour **{self.guild.name}**",
                    color=discord.Color.blue(),
                    timestamp=datetime.now(timezone.utc)
                )
                embed.set_image(url="attachment://overview.png")
                embed.set_footer(text="Mise à jour automatique toutes les 5 minutes")

                await interaction.followup.send(embed=embed, file=file, view=self)
            else:
                await interaction.followup.send("❌ Pas assez de données pour générer la vue d'ensemble.")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la génération: {e}")

    @discord.ui.button(label="📈 Messages", style=discord.ButtonStyle.secondary)
    async def messages_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        try:
            message_stats = self.stats_db.get_message_stats(self.guild.id, days=7)

            # Graphique des messages quotidiens
            chart = self.visualizer.create_messages_chart(message_stats['daily_messages'], days=7)

            if chart:
                file = discord.File(chart, filename="messages.png")

                # Calculer les totaux
                total_messages = sum(message_stats['daily_messages'].values())
                avg_daily = total_messages / 7 if total_messages > 0 else 0

                embed = discord.Embed(
                    title="📈 Statistiques des Messages",
                    color=discord.Color.green(),
                    timestamp=datetime.now(timezone.utc)
                )
                embed.add_field(name="📊 Total (7j)", value=f"{total_messages:,}", inline=True)
                embed.add_field(name="📊 Moyenne/jour", value=f"{avg_daily:.1f}", inline=True)
                embed.add_field(name="👥 Utilisateurs actifs", value=f"{len(message_stats['top_users'])}", inline=True)

                embed.set_image(url="attachment://messages.png")

                await interaction.followup.send(embed=embed, file=file, view=self)
            else:
                await interaction.followup.send("❌ Pas de données de messages disponibles.")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {e}")

    @discord.ui.button(label="👑 Top Users", style=discord.ButtonStyle.secondary)
    async def top_users_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        try:
            message_stats = self.stats_db.get_message_stats(self.guild.id, days=7)

            if not message_stats['top_users']:
                await interaction.followup.send("❌ Pas de données d'utilisateurs disponibles.")
                return

            # Graphique des top utilisateurs
            chart = self.visualizer.create_top_users_chart(message_stats['top_users'], self.guild, days=7)

            if chart:
                file = discord.File(chart, filename="top_users.png")

                embed = discord.Embed(
                    title="👑 Utilisateurs les Plus Actifs",
                    description="Classement des membres les plus actifs (7 derniers jours)",
                    color=discord.Color.gold(),
                    timestamp=datetime.now(timezone.utc)
                )

                # Ajouter le top 5 en texte
                top_5_text = ""
                for i, (user_id, count) in enumerate(message_stats['top_users'][:5], 1):
                    user = self.guild.get_member(int(user_id))
                    name = user.display_name if user else f"Utilisateur {user_id}"
                    medal = ["🥇", "🥈", "🥉", "🏅", "🏅"][i-1]
                    top_5_text += f"{medal} **{name}** - {count} messages\n"

                if top_5_text:
                    embed.add_field(name="🏆 Top 5", value=top_5_text, inline=False)

                embed.set_image(url="attachment://top_users.png")

                await interaction.followup.send(embed=embed, file=file, view=self)
            else:
                await interaction.followup.send("❌ Erreur lors de la génération du graphique.")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {e}")

    @discord.ui.button(label="📊 Canaux", style=discord.ButtonStyle.secondary)
    async def channels_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        try:
            message_stats = self.stats_db.get_message_stats(self.guild.id, days=7)

            if not message_stats['channel_activity']:
                await interaction.followup.send("❌ Pas de données d'activité par canal.")
                return

            # Graphique d'activité par canal
            chart = self.visualizer.create_channel_activity_chart(message_stats['channel_activity'], self.guild)

            if chart:
                file = discord.File(chart, filename="channels.png")

                embed = discord.Embed(
                    title="📊 Activité par Canal",
                    description="Répartition des messages par canal (7 derniers jours)",
                    color=discord.Color.purple(),
                    timestamp=datetime.now(timezone.utc)
                )

                # Ajouter les stats texte
                total_messages = sum(count for _, count in message_stats['channel_activity'])
                most_active = message_stats['channel_activity'][0] if message_stats['channel_activity'] else None

                if most_active:
                    channel = self.guild.get_channel(int(most_active[0]))
                    channel_name = f"#{channel.name}" if channel else f"Canal {most_active[0]}"
                    percentage = (most_active[1] / total_messages * 100) if total_messages > 0 else 0
                    embed.add_field(
                        name="🔥 Canal le plus actif",
                        value=f"{channel_name}\n{most_active[1]} messages ({percentage:.1f}%)",
                        inline=True
                    )

                embed.add_field(name="📈 Total messages", value=f"{total_messages:,}", inline=True)
                embed.add_field(name="📊 Canaux actifs", value=f"{len(message_stats['channel_activity'])}", inline=True)

                embed.set_image(url="attachment://channels.png")

                await interaction.followup.send(embed=embed, file=file, view=self)
            else:
                await interaction.followup.send("❌ Erreur lors de la génération du graphique.")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {e}")

    @discord.ui.button(label="🕐 Activité Horaire", style=discord.ButtonStyle.secondary)
    async def hourly_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        try:
            message_stats = self.stats_db.get_message_stats(self.guild.id, days=7)

            # Graphique d'activité horaire
            chart = self.visualizer.create_hourly_activity_chart(message_stats['hourly_activity'])

            if chart:
                file = discord.File(chart, filename="hourly.png")

                # Trouver les heures de pointe
                hourly_data = message_stats['hourly_activity']
                if hourly_data:
                    peak_hour = max(hourly_data.items(), key=lambda x: x[1])
                    peak_time = f"{peak_hour[0]}:00"
                    peak_messages = peak_hour[1]
                else:
                    peak_time = "N/A"
                    peak_messages = 0

                embed = discord.Embed(
                    title="🕐 Activité par Heure",
                    description="Répartition des messages selon l'heure de la journée",
                    color=discord.Color.orange(),
                    timestamp=datetime.now(timezone.utc)
                )

                embed.add_field(name="🔥 Heure de pointe", value=f"{peak_time}", inline=True)
                embed.add_field(name="📊 Messages (pointe)", value=f"{peak_messages}", inline=True)

                # Analyser les tranches horaires
                total_messages = sum(hourly_data.values()) if hourly_data else 0
                if total_messages > 0:
                    morning = sum(hourly_data.get(f"{h:02d}", 0) for h in range(6, 12))  # 6h-12h
                    afternoon = sum(hourly_data.get(f"{h:02d}", 0) for h in range(12, 18))  # 12h-18h
                    evening = sum(hourly_data.get(f"{h:02d}", 0) for h in range(18, 24))  # 18h-24h
                    night = sum(hourly_data.get(f"{h:02d}", 0) for h in range(0, 6))  # 0h-6h

                    embed.add_field(
                        name="📊 Répartition",
                        value=f"🌅 Matin: {morning/total_messages*100:.1f}%\n"
                              f"☀️ Après-midi: {afternoon/total_messages*100:.1f}%\n"
                              f"🌆 Soirée: {evening/total_messages*100:.1f}%\n"
                              f"🌙 Nuit: {night/total_messages*100:.1f}%",
                        inline=False
                    )

                embed.set_image(url="attachment://hourly.png")

                await interaction.followup.send(embed=embed, file=file, view=self)
            else:
                await interaction.followup.send("❌ Pas de données d'activité horaire.")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {e}")

class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.stats_db = StatsDatabase()
        self.visualizer = StatsVisualizer()

    @app_commands.command(name="stats", description="🔢 Afficher les statistiques du serveur")
    @app_commands.describe(
        periode="Période d'analyse (7j, 30j, etc.)"
    )
    async def stats_command(self, interaction: discord.Interaction, periode: str = "7j"):
        # Convertir la période
        if periode == "7j":
            days = 7
        elif periode == "30j":
            days = 30
        elif periode == "3m":
            days = 90
        else:
            days = 7

        # Vérifier les permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Seuls les administrateurs peuvent voir les statistiques complètes.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # Créer la vue interactive
            view = StatsView(interaction.guild, self.stats_db, self.visualizer)

            embed = discord.Embed(
                title="📊 Statistiques du Serveur",
                description=f"Cliquez sur les boutons pour voir les différentes statistiques de **{interaction.guild.name}**",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )

            # Statistiques rapides
            message_stats = self.stats_db.get_message_stats(interaction.guild.id, days)
            member_stats = self.stats_db.get_member_stats(interaction.guild.id, days)

            total_messages = sum(message_stats['daily_messages'].values())
            total_joins = sum(member_stats['daily_joins'].values())
            total_leaves = sum(member_stats['daily_leaves'].values())
            net_growth = total_joins - total_leaves

            embed.add_field(name="📈 Messages", value=f"{total_messages:,}", inline=True)
            embed.add_field(name="📊 Nouveaux membres", value=f"+{total_joins}", inline=True)
            embed.add_field(name="📉 Membres partis", value=f"-{total_leaves}", inline=True)
            embed.add_field(name="⚖️ Croissance nette", value=f"{net_growth:+d}", inline=True)
            embed.add_field(name="👥 Membres actuels", value=f"{interaction.guild.member_count:,}", inline=True)
            embed.add_field(name="📊 Période", value=f"{periode}", inline=True)

            embed.set_footer(text="Utilisez les boutons pour voir les détails")

            await interaction.followup.send(embed=embed, view=view)

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la génération des statistiques: {e}")

    @app_commands.command(name="stats_cleanup", description="🧹 Nettoyer les anciennes données statistiques")
    @app_commands.describe(jours="Nombre de jours à conserver (défaut: 90)")
    async def stats_cleanup(self, interaction: discord.Interaction, jours: int = 90):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Seuls les administrateurs peuvent nettoyer les statistiques.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            self.stats_db.cleanup_old_data(jours)

            embed = discord.Embed(
                title="🧹 Nettoyage Terminé",
                description=f"Les données statistiques de plus de {jours} jours ont été supprimées.",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors du nettoyage: {e}")

    @app_commands.command(name="stats_export", description="📤 Exporter les statistiques en JSON")
    async def stats_export(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Seuls les administrateurs peuvent exporter les statistiques.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Récupérer les données
            message_stats = self.stats_db.get_message_stats(interaction.guild.id, 30)
            member_stats = self.stats_db.get_member_stats(interaction.guild.id, 30)

            export_data = {
                'guild_id': interaction.guild.id,
                'guild_name': interaction.guild.name,
                'export_date': datetime.now(timezone.utc).isoformat(),
                'period': '30 days',
                'message_stats': message_stats,
                'member_stats': member_stats
            }

            # Créer le fichier JSON
            import json
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)

            # Envoyer le fichier
            from io import StringIO
            json_file = StringIO(json_data)

            file = discord.File(
                fp=json_file,
                filename=f"stats_{interaction.guild.name}_{datetime.now().strftime('%Y%m%d')}.json"
            )

            embed = discord.Embed(
                title="📤 Export des Statistiques",
                description="Données des 30 derniers jours exportées avec succès.",
                color=discord.Color.green()
            )

            await interaction.followup.send(embed=embed, file=file, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de l'export: {e}", ephemeral=True)

async def setup(client):
    await client.add_cog(Stats(client))