import json
import os
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
import sqlite3

class StatsDatabase:
    def __init__(self, db_path="server_stats.db"):
        self.db_path = db_path
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_cache_update = {}
        self.init_database()

    def init_database(self):
        """Initialiser la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table pour les messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                timestamp DATETIME NOT NULL,
                message_length INTEGER DEFAULT 0,
                date TEXT NOT NULL
            )
        ''')

        # Table pour les membres (joins/leaves)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                date TEXT NOT NULL
            )
        ''')

        # Table pour les statistiques quotidiennes (pré-calculées)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                total_messages INTEGER DEFAULT 0,
                total_users INTEGER DEFAULT 0,
                new_members INTEGER DEFAULT 0,
                left_members INTEGER DEFAULT 0,
                active_channels TEXT DEFAULT '{}',
                top_users TEXT DEFAULT '{}',
                UNIQUE(guild_id, date)
            )
        ''')

        # Index pour optimiser les requêtes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_guild ON messages(guild_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_events_date ON member_events(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_stats_guild_date ON daily_stats(guild_id, date)')

        conn.commit()
        conn.close()

    def log_message(self, user_id, channel_id, guild_id, message_length=0):
        """Enregistrer un message"""
        now = datetime.now(timezone.utc)
        date_str = now.strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO messages (user_id, channel_id, guild_id, timestamp, message_length, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, channel_id, guild_id, now, message_length, date_str))

        conn.commit()
        conn.close()

    def log_member_event(self, user_id, guild_id, event_type):
        """Enregistrer un événement membre (join/leave)"""
        now = datetime.now(timezone.utc)
        date_str = now.strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO member_events (user_id, guild_id, event_type, timestamp, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, guild_id, event_type, now, date_str))

        conn.commit()
        conn.close()

    def _is_cache_valid(self, cache_key):
        """Vérifier si le cache est encore valide"""
        if cache_key not in self.last_cache_update:
            return False

        elapsed = (datetime.now(timezone.utc) - self.last_cache_update[cache_key]).total_seconds()
        return elapsed < self.cache_timeout

    def _get_cache_key(self, guild_id, days, stat_type):
        """Générer une clé de cache"""
        return f"{stat_type}_{guild_id}_{days}"

    def get_message_stats(self, guild_id, days=7):
        """Récupérer les statistiques des messages avec mise en cache"""
        cache_key = self._get_cache_key(guild_id, days, 'messages')

        # Vérifier le cache
        if self._is_cache_valid(cache_key) and cache_key in self.cache:
            return self.cache[cache_key]

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        start_date_str = start_date.strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Messages par jour
        cursor.execute('''
            SELECT date, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND date >= ?
            GROUP BY date
            ORDER BY date
        ''', (guild_id, start_date_str))

        daily_messages = dict(cursor.fetchall())

        # Top utilisateurs
        cursor.execute('''
            SELECT user_id, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND date >= ?
            GROUP BY user_id
            ORDER BY count DESC
            LIMIT 10
        ''', (guild_id, start_date_str))

        top_users = cursor.fetchall()

        # Activité par canal
        cursor.execute('''
            SELECT channel_id, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND date >= ?
            GROUP BY channel_id
            ORDER BY count DESC
            LIMIT 10
        ''', (guild_id, start_date_str))

        channel_activity = cursor.fetchall()

        # Messages par heure
        cursor.execute('''
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND date >= ?
            GROUP BY hour
            ORDER BY hour
        ''', (guild_id, start_date_str))

        hourly_activity = dict(cursor.fetchall())

        conn.close()

        result = {
            'daily_messages': daily_messages,
            'top_users': top_users,
            'channel_activity': channel_activity,
            'hourly_activity': hourly_activity
        }

        # Mettre en cache
        self.cache[cache_key] = result
        self.last_cache_update[cache_key] = datetime.now(timezone.utc)

        return result

    def get_member_stats(self, guild_id, days=30):
        """Récupérer les statistiques des membres avec mise en cache"""
        cache_key = self._get_cache_key(guild_id, days, 'members')

        # Vérifier le cache
        if self._is_cache_valid(cache_key) and cache_key in self.cache:
            return self.cache[cache_key]

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        start_date_str = start_date.strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Joins par jour
        cursor.execute('''
            SELECT date, COUNT(*) as count
            FROM member_events
            WHERE guild_id = ? AND event_type = 'join' AND date >= ?
            GROUP BY date
            ORDER BY date
        ''', (guild_id, start_date_str))

        daily_joins = dict(cursor.fetchall())

        # Leaves par jour
        cursor.execute('''
            SELECT date, COUNT(*) as count
            FROM member_events
            WHERE guild_id = ? AND event_type = 'leave' AND date >= ?
            GROUP BY date
            ORDER BY date
        ''', (guild_id, start_date_str))

        daily_leaves = dict(cursor.fetchall())

        conn.close()

        result = {
            'daily_joins': daily_joins,
            'daily_leaves': daily_leaves
        }

        # Mettre en cache
        self.cache[cache_key] = result
        self.last_cache_update[cache_key] = datetime.now(timezone.utc)

        return result

    def calculate_daily_stats(self, guild_id, date=None):
        """Calculer et sauvegarder les statistiques quotidiennes"""
        if date is None:
            date = datetime.now(timezone.utc).strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Messages totaux
        cursor.execute('''
            SELECT COUNT(*) FROM messages
            WHERE guild_id = ? AND date = ?
        ''', (guild_id, date))
        total_messages = cursor.fetchone()[0]

        # Utilisateurs actifs
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM messages
            WHERE guild_id = ? AND date = ?
        ''', (guild_id, date))
        total_users = cursor.fetchone()[0]

        # Nouveaux membres
        cursor.execute('''
            SELECT COUNT(*) FROM member_events
            WHERE guild_id = ? AND event_type = 'join' AND date = ?
        ''', (guild_id, date))
        new_members = cursor.fetchone()[0]

        # Membres partis
        cursor.execute('''
            SELECT COUNT(*) FROM member_events
            WHERE guild_id = ? AND event_type = 'leave' AND date = ?
        ''', (guild_id, date))
        left_members = cursor.fetchone()[0]

        # Canaux actifs
        cursor.execute('''
            SELECT channel_id, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND date = ?
            GROUP BY channel_id
            ORDER BY count DESC
        ''', (guild_id, date))
        active_channels = dict(cursor.fetchall())

        # Top utilisateurs
        cursor.execute('''
            SELECT user_id, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND date = ?
            GROUP BY user_id
            ORDER BY count DESC
            LIMIT 10
        ''', (guild_id, date))
        top_users = dict(cursor.fetchall())

        # Sauvegarder les statistiques
        cursor.execute('''
            INSERT OR REPLACE INTO daily_stats
            (guild_id, date, total_messages, total_users, new_members, left_members, active_channels, top_users)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (guild_id, date, total_messages, total_users, new_members, left_members,
              json.dumps(active_channels), json.dumps(top_users)))

        conn.commit()
        conn.close()

        return {
            'total_messages': total_messages,
            'total_users': total_users,
            'new_members': new_members,
            'left_members': left_members,
            'active_channels': active_channels,
            'top_users': top_users
        }

    def cleanup_old_data(self, days_to_keep=90):
        """Nettoyer les anciennes données et vider le cache"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM messages WHERE date < ?', (cutoff_date_str,))
        cursor.execute('DELETE FROM member_events WHERE date < ?', (cutoff_date_str,))
        cursor.execute('DELETE FROM daily_stats WHERE date < ?', (cutoff_date_str,))

        conn.commit()
        conn.close()

        # Vider le cache après nettoyage
        self.cache.clear()
        self.last_cache_update.clear()

    def clear_cache(self):
        """Vider manuellement le cache"""
        self.cache.clear()
        self.last_cache_update.clear()

    def get_cache_status(self):
        """Obtenir des informations sur le cache"""
        return {
            'cached_entries': len(self.cache),
            'cache_keys': list(self.cache.keys()),
            'last_updates': {k: v.isoformat() for k, v in self.last_cache_update.items()}
        }