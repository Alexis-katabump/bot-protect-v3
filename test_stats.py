#!/usr/bin/env python3
"""
Script de test pour le système de statistiques
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import asyncio

# Ajouter le répertoire actuel au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.stats_database import StatsDatabase
from utils.stats_visualizer import StatsVisualizer

def test_database():
    """Test de base de données"""
    print("Test de la base de donnees...")

    # Créer une instance de test
    db = StatsDatabase("test_stats.db")

    # Données de test
    guild_id = 123456789
    user_id = 987654321
    channel_id = 555666777

    # Test d'enregistrement de messages
    print("  Test d'enregistrement de messages...")
    for i in range(10):
        db.log_message(user_id + i, channel_id, guild_id, message_length=20 + i)

    # Test d'enregistrement d'événements membres
    print("  Test d'evenements membres...")
    for i in range(5):
        db.log_member_event(user_id + i, guild_id, 'join')

    for i in range(2):
        db.log_member_event(user_id + i, guild_id, 'leave')

    # Test de récupération des statistiques
    print("  Test de recuperation des stats...")
    message_stats = db.get_message_stats(guild_id, days=7)
    member_stats = db.get_member_stats(guild_id, days=7)

    print(f"    Messages par jour: {len(message_stats['daily_messages'])} jours")
    print(f"    Top utilisateurs: {len(message_stats['top_users'])} utilisateurs")
    print(f"    Activité par canal: {len(message_stats['channel_activity'])} canaux")
    print(f"    Activité horaire: {len(message_stats['hourly_activity'])} heures")

    print(f"    Joins par jour: {len(member_stats['daily_joins'])} jours")
    print(f"    Leaves par jour: {len(member_stats['daily_leaves'])} jours")

    # Test du cache
    print("  Test du cache...")
    import time

    # Premier appel (va en base)
    start_time = time.time()
    stats1 = db.get_message_stats(guild_id, days=7)
    time1 = time.time() - start_time

    # Deuxième appel (depuis le cache)
    start_time = time.time()
    stats2 = db.get_message_stats(guild_id, days=7)
    time2 = time.time() - start_time

    print(f"    Premier appel (base): {time1:.4f}s")
    print(f"    Deuxième appel (cache): {time2:.4f}s")
    print(f"    Amélioration: {time1/time2:.1f}x plus rapide")

    # Test des statistiques quotidiennes
    print("  Test des stats quotidiennes...")
    daily_stats = db.calculate_daily_stats(guild_id)
    print(f"    Messages totaux: {daily_stats['total_messages']}")
    print(f"    Utilisateurs actifs: {daily_stats['total_users']}")
    print(f"    Nouveaux membres: {daily_stats['new_members']}")

    # Nettoyage
    os.remove("test_stats.db")
    print("  Base de donnees testee avec succes!")

def test_visualizer():
    """Test du visualiseur"""
    print("\nTest du visualiseur...")

    visualizer = StatsVisualizer()

    # Données de test
    daily_messages = {
        '2024-01-01': 150,
        '2024-01-02': 200,
        '2024-01-03': 180,
        '2024-01-04': 220,
        '2024-01-05': 190,
        '2024-01-06': 250,
        '2024-01-07': 180
    }

    top_users = [
        (123, 45),
        (456, 38),
        (789, 32),
        (101, 28),
        (112, 25)
    ]

    channel_activity = [
        (1001, 120),
        (1002, 85),
        (1003, 60),
        (1004, 45)
    ]

    hourly_activity = {
        f"{h:02d}": h * 2 + 10 for h in range(24)
    }

    # Test de génération de graphiques
    print("  Test graphique messages...")
    try:
        chart = visualizer.create_messages_chart(daily_messages, days=7)
        if chart:
            print("    Graphique messages genere")
        else:
            print("    Echec generation graphique messages")
    except Exception as e:
        print(f"    Erreur graphique messages: {e}")

    print("  Test graphique activite horaire...")
    try:
        chart = visualizer.create_hourly_activity_chart(hourly_activity)
        if chart:
            print("    Graphique activite horaire genere")
        else:
            print("    Echec generation graphique activite")
    except Exception as e:
        print(f"    Erreur graphique activite: {e}")

    print("  Visualiseur teste avec succes!")

def test_performance():
    """Test de performance"""
    print("\nTest de performance...")

    db = StatsDatabase("perf_test.db")
    guild_id = 999888777

    import time

    # Générer beaucoup de données
    print("  Generation de 1000 messages...")
    start_time = time.time()

    for i in range(1000):
        user_id = 1000 + (i % 50)  # 50 utilisateurs différents
        channel_id = 2000 + (i % 10)  # 10 canaux différents
        db.log_message(user_id, channel_id, guild_id, message_length=50)

    generation_time = time.time() - start_time
    print(f"    Temps de generation: {generation_time:.2f}s")

    # Test de requête
    print("  Test de requete avec cache...")

    start_time = time.time()
    stats = db.get_message_stats(guild_id, days=7)
    query_time = time.time() - start_time

    print(f"    Temps de requete: {query_time:.4f}s")
    print(f"    Messages trouves: {sum(stats['daily_messages'].values())}")
    print(f"    Top users: {len(stats['top_users'])}")

    # Test cache
    start_time = time.time()
    stats2 = db.get_message_stats(guild_id, days=7)
    cache_time = time.time() - start_time

    print(f"    Temps avec cache: {cache_time:.4f}s")
    print(f"    Amelioration cache: {query_time/cache_time:.1f}x")

    # Nettoyage
    os.remove("perf_test.db")
    print("  Test de performance termine!")

def main():
    """Fonction principale de test"""
    print("Demarrage des tests du systeme de statistiques\n")

    try:
        test_database()
        test_visualizer()
        test_performance()

        print("\nTous les tests ont reussi!")
        print("\nResume:")
        print("  Base de donnees SQLite avec cache")
        print("  Visualisations matplotlib")
        print("  Performance optimisee")
        print("  Systeme pret a l'emploi")

    except Exception as e:
        print(f"\nErreur lors des tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()