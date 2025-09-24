import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta, timezone
import io
import numpy as np
from collections import defaultdict

# Configuration matplotlib pour Discord
plt.style.use('dark_background')
sns.set_palette("husl")

class StatsVisualizer:
    def __init__(self):
        self.colors = {
            'primary': '#5865F2',
            'success': '#57F287',
            'warning': '#FEE75C',
            'danger': '#ED4245',
            'info': '#EB459E'
        }

    def create_messages_chart(self, daily_messages, days=7):
        """Créer un graphique des messages par jour"""
        # Préparer les données
        end_date = datetime.now(timezone.utc)
        dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days-1, -1, -1)]

        message_counts = [daily_messages.get(date, 0) for date in dates]
        date_labels = [(end_date - timedelta(days=i)).strftime('%d/%m') for i in range(days-1, -1, -1)]

        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(date_labels, message_counts, marker='o', linewidth=3, markersize=8, color=self.colors['primary'])
        ax.fill_between(date_labels, message_counts, alpha=0.3, color=self.colors['primary'])

        ax.set_title(f'📈 Messages des {days} derniers jours', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Nombre de messages', fontsize=12)

        # Style
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.xticks(rotation=45)
        plt.tight_layout()

        # Convertir en BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='#2F3136')
        buffer.seek(0)
        plt.close()

        return buffer

    def create_top_users_chart(self, top_users, guild, days=7):
        """Créer un graphique des utilisateurs les plus actifs"""
        if not top_users:
            return None

        # Préparer les données (max 8 utilisateurs pour lisibilité)
        top_users = top_users[:8]
        user_names = []
        message_counts = []

        for user_id, count in top_users:
            try:
                user = guild.get_member(int(user_id))
                if user:
                    display_name = user.display_name[:15] + "..." if len(user.display_name) > 15 else user.display_name
                    user_names.append(display_name)
                else:
                    user_names.append(f"Utilisateur {str(user_id)[:8]}")
                message_counts.append(count)
            except:
                user_names.append(f"Utilisateur {str(user_id)[:8]}")
                message_counts.append(count)

        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(user_names, message_counts, color=sns.color_palette("husl", len(user_names)))

        ax.set_title(f'👑 Top {len(top_users)} utilisateurs actifs ({days}j)', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Nombre de messages', fontsize=12)

        # Ajouter les valeurs sur les barres
        for i, (bar, count) in enumerate(zip(bars, message_counts)):
            ax.text(bar.get_width() + max(message_counts) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'{count}', ha='left', va='center', fontweight='bold')

        # Style
        ax.grid(True, alpha=0.3, axis='x')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()

        # Convertir en BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='#2F3136')
        buffer.seek(0)
        plt.close()

        return buffer

    def create_channel_activity_chart(self, channel_activity, guild):
        """Créer un graphique de l'activité par canal"""
        if not channel_activity:
            return None

        # Préparer les données (max 8 canaux)
        channel_activity = channel_activity[:8]
        channel_names = []
        activity_counts = []

        for channel_id, count in channel_activity:
            try:
                channel = guild.get_channel(int(channel_id))
                if channel:
                    channel_name = f"#{channel.name}"[:20] + "..." if len(channel.name) > 20 else f"#{channel.name}"
                    channel_names.append(channel_name)
                else:
                    channel_names.append(f"Canal {str(channel_id)[:8]}")
                activity_counts.append(count)
            except:
                channel_names.append(f"Canal {str(channel_id)[:8]}")
                activity_counts.append(count)

        # Créer le graphique (camembert)
        fig, ax = plt.subplots(figsize=(10, 10))
        colors = sns.color_palette("husl", len(channel_names))

        wedges, texts, autotexts = ax.pie(activity_counts, labels=channel_names, autopct='%1.1f%%',
                                         colors=colors, startangle=90, textprops={'fontsize': 10})

        # Améliorer la lisibilité
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('📊 Activité par canal', fontsize=16, fontweight='bold', pad=20)

        plt.tight_layout()

        # Convertir en BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='#2F3136')
        buffer.seek(0)
        plt.close()

        return buffer

    def create_hourly_activity_chart(self, hourly_activity):
        """Créer un graphique de l'activité par heure"""
        # Préparer les données (24 heures)
        hours = list(range(24))
        activity = [hourly_activity.get(f"{h:02d}", 0) for h in hours]

        # Créer le graphique
        fig, ax = plt.subplots(figsize=(14, 6))
        bars = ax.bar(hours, activity, color=self.colors['info'], alpha=0.8)

        # Mettre en évidence les heures de pointe
        max_activity = max(activity) if activity else 0
        peak_threshold = max_activity * 0.7

        for bar, act in zip(bars, activity):
            if act >= peak_threshold and act > 0:
                bar.set_color(self.colors['warning'])

        ax.set_title('🕐 Activité par heure de la journée', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Heure', fontsize=12)
        ax.set_ylabel('Nombre de messages', fontsize=12)
        ax.set_xticks(hours)
        ax.set_xticklabels([f"{h:02d}h" for h in hours])

        # Style
        ax.grid(True, alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()

        # Convertir en BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='#2F3136')
        buffer.seek(0)
        plt.close()

        return buffer

    def create_member_growth_chart(self, daily_joins, daily_leaves, days=30):
        """Créer un graphique de croissance des membres"""
        # Préparer les données
        end_date = datetime.now(timezone.utc)
        dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days-1, -1, -1)]

        joins = [daily_joins.get(date, 0) for date in dates]
        leaves = [daily_leaves.get(date, 0) for date in dates]
        net_growth = [j - l for j, l in zip(joins, leaves)]

        date_labels = [(end_date - timedelta(days=i)).strftime('%d/%m') for i in range(days-1, -1, -1)]

        # Créer le graphique
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Graphique des arrivées/départs
        ax1.plot(date_labels, joins, marker='o', linewidth=2, color=self.colors['success'], label='Arrivées')
        ax1.plot(date_labels, leaves, marker='s', linewidth=2, color=self.colors['danger'], label='Départs')
        ax1.fill_between(date_labels, joins, alpha=0.3, color=self.colors['success'])
        ax1.fill_between(date_labels, leaves, alpha=0.3, color=self.colors['danger'])

        ax1.set_title(f'📊 Arrivées vs Départs ({days}j)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Nombre de membres')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        # Graphique de croissance nette
        colors = [self.colors['success'] if x >= 0 else self.colors['danger'] for x in net_growth]
        ax2.bar(date_labels, net_growth, color=colors, alpha=0.8)
        ax2.axhline(y=0, color='white', linestyle='-', alpha=0.5)

        ax2.set_title('📈 Croissance nette des membres', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Croissance nette')
        ax2.grid(True, alpha=0.3)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        # Rotation des labels
        for ax in [ax1, ax2]:
            plt.setp(ax.get_xticklabels(), rotation=45)

        plt.tight_layout()

        # Convertir en BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='#2F3136')
        buffer.seek(0)
        plt.close()

        return buffer

    def create_overview_chart(self, stats_data, guild):
        """Créer un graphique de vue d'ensemble"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Messages des 7 derniers jours (ligne)
        daily_messages = stats_data['message_stats']['daily_messages']
        dates = list(daily_messages.keys())[-7:]
        messages = [daily_messages[date] for date in dates]
        date_labels = [datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m') for date in dates]

        ax1.plot(date_labels, messages, marker='o', linewidth=3, color=self.colors['primary'])
        ax1.fill_between(date_labels, messages, alpha=0.3, color=self.colors['primary'])
        ax1.set_title('Messages (7j)', fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # 2. Top 5 utilisateurs (barres horizontales)
        top_users = stats_data['message_stats']['top_users'][:5]
        if top_users:
            user_names = []
            counts = []
            for user_id, count in top_users:
                user = guild.get_member(int(user_id))
                name = user.display_name[:10] if user else f"User{str(user_id)[:4]}"
                user_names.append(name)
                counts.append(count)

            ax2.barh(user_names, counts, color=sns.color_palette("husl", len(user_names)))
            ax2.set_title('Top Utilisateurs', fontweight='bold')

        # 3. Activité par heure (barres)
        hourly_activity = stats_data['message_stats']['hourly_activity']
        hours = list(range(24))
        activity = [hourly_activity.get(f"{h:02d}", 0) for h in hours]

        ax3.bar(hours[::3], activity[::3], color=self.colors['info'], alpha=0.8)
        ax3.set_title('Activité par heure', fontweight='bold')
        ax3.set_xticks(hours[::3])
        ax3.set_xticklabels([f"{h}h" for h in hours[::3]])

        # 4. Croissance des membres (ligne)
        member_stats = stats_data['member_stats']
        daily_joins = member_stats['daily_joins']
        daily_leaves = member_stats['daily_leaves']
        dates = list(daily_joins.keys())[-7:]

        joins = [daily_joins.get(date, 0) for date in dates]
        leaves = [daily_leaves.get(date, 0) for date in dates]
        date_labels = [datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m') for date in dates]

        ax4.plot(date_labels, joins, marker='o', color=self.colors['success'], label='Arrivées')
        ax4.plot(date_labels, leaves, marker='s', color=self.colors['danger'], label='Départs')
        ax4.set_title('Membres (7j)', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        # Style général
        for ax in [ax1, ax2, ax3, ax4]:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        plt.suptitle(f'📊 Dashboard - {guild.name}', fontsize=18, fontweight='bold', y=0.98)
        plt.tight_layout()

        # Convertir en BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='#2F3136')
        buffer.seek(0)
        plt.close()

        return buffer