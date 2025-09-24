# 🤖 KataBump Bot v2 - Guide Complet

## 📚 Table des Matières

1. [🚀 Configuration Rapide](#-configuration-rapide)
2. [🔐 Sécurité & Vérification](#-sécurité--vérification)
3. [🎫 Système de Support](#-système-de-support)
4. [🛡️ Modération & Administration](#️-modération--administration)
5. [🎮 Fonctionnalités Communautaires](#-fonctionnalités-communautaires)
6. [ℹ️ Utilitaires & Informations](#️-utilitaires--informations)
7. [🆕 Nouveaux Systèmes](#-nouveaux-systèmes-ajoutés)
8. [💡 Exemples d'Utilisation](#-exemples-dutilisation-détaillés)
9. [⚡ Guide Admin Express](#-guide-de-configuration-rapide---administrateurs)
10. [🎉 Résumé Final](#-résumé---votre-bot-est-maintenant-complet-)

---

## 🚀 Configuration Rapide

### **🎯 Première Configuration (Obligatoire)**
```bash
# 1. Configurer les systèmes principaux
/setup_captcha          # Configuration du système de vérification
/setup_antispam         # Configuration de l'anti-spam
/setup_tickets          # Configuration du système de tickets
/setup_logs             # Configuration des logs

# 2. Activer les systèmes
/toggle_captcha         # Activer la vérification captcha
/toggle_antispam        # Activer l'anti-spam
/toggle_tickets         # Activer les tickets

# 3. Créer les interfaces utilisateur
/ticket_panel #support  # Créer le panel de tickets
/send_welcome_message   # Message d'accueil pour le captcha
```

---

## 🔐 **COMMANDES DE SÉCURITÉ & VÉRIFICATION**

### **🔒 Système Captcha** `captcha.py`
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/setup_captcha` | Configure automatiquement le système de vérification | `/setup_captcha` |
| `/toggle_captcha` | Active/désactive le captcha | `/toggle_captcha` |
| `/captcha_config` | Personnalise les paramètres | `/captcha_config timeout_minutes:10 max_attempts:5` |
| `/captcha_status` | Affiche l'état du système | `/captcha_status` |
| `/verify_user @user` | Vérifie manuellement un utilisateur | `/verify_user @nouveaumembre` |
| `/send_welcome_message` | Envoie le message d'accueil | `/send_welcome_message` |
| `/clear_pending` | Efface les vérifications en attente | `/clear_pending` |
| `/test_captcha @user` | Teste le système avec un membre | `/test_captcha @testeur` |

### **🚫 Système Anti-Spam** `antispam.py`
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/setup_antispam` | Configure le système anti-spam | `/setup_antispam` |
| `/toggle_antispam` | Active/désactive l'anti-spam | `/toggle_antispam` |
| `/antispam_config` | Configure les paramètres (limite, sanction) | `/antispam_config message_limit:5 time_window:3 sanction_type:timeout` |
| `/antispam_status` | Affiche l'état complet du système | `/antispam_status` |
| `/antispam_immunity @role` | Donne/retire l'immunité à un rôle | `/antispam_immunity @Modérateurs` |
| `/antispam_ignore #channel` | Ignore/surveille un canal | `/antispam_ignore #spam-test` |
| `/antispam_stats @user` | Statistiques des avertissements | `/antispam_stats @spammeur` |
| `/clear_spam_warnings @user` | Efface les avertissements | `/clear_spam_warnings @utilisateur` |
| `/test_antispam` | Instructions pour tester | `/test_antispam` |

---

## 🎫 **SYSTÈME DE SUPPORT**

### **🎫 Système de Tickets** `tickets.py`
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/setup_tickets` | Configure le système de tickets | `/setup_tickets` |
| `/toggle_tickets` | Active/désactive les tickets | `/toggle_tickets` |
| `/ticket_panel #channel` | Crée le panel avec boutons | `/ticket_panel #support` |
| `/tickets_config` | Configure rôles et limites | `/tickets_config staff_role:@Staff max_tickets:3` |
| `/tickets_status` | Affiche l'état du système | `/tickets_status` |
| `/force_close #ticket` | Force la fermeture d'un ticket | `/force_close #ticket-0001` |
| `/ticket_add @user #ticket` | Ajoute un utilisateur au ticket | `/ticket_add @helper #ticket-0001` |
| `/ticket_remove @user #ticket` | Retire un utilisateur du ticket | `/ticket_remove @user #ticket-0001` |

---

## 🛡️ **MODÉRATION & ADMINISTRATION**

### **👥 Gestion des Utilisateurs** `admin.py, blacklist.py, wl.py`
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/bl @user` | Ajoute/retire de la blacklist | `/bl @spammeur` |
| `/unbl @user` | Retire de la blacklist | `/unbl @utilisateur` |
| `/wl @user` | Ajoute/retire de la whitelist | `/wl @modérateur` |
| `/unwl @user` | Retire de la whitelist | `/unwl @ancien_staff` |
| `/whitelist` | Affiche la liste whitelist | `/whitelist` |

### **🚪 Gestion des Arrivées** `antijoins.py`
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/antijoins` | Active/désactive l'anti-joins | `/antijoins` |
| `/antibot` | Active/désactive l'anti-bot | `/antibot` |

### **📝 Système de Logs** `logs.py`
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/setup_logs` | Configure les canaux de logs | `/setup_logs` |

---

## 🎮 **FONCTIONNALITÉS COMMUNAUTAIRES**

### **🎁 Système de Giveaways** `giveaway.py`
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/giveaway` | Crée un giveaway | `/giveaway duration:1h winners:3 prize:Nitro` |
| `/gend` | Termine un giveaway | `/gend giveaway_id:12345` |
| `/greroll` | Reroll un giveaway | `/greroll giveaway_id:12345` |

### **📈 Système de Niveaux** `level.py`
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/level @user` | Affiche le niveau d'un utilisateur | `/level @membre` |

---

## ℹ️ **UTILITAIRES & INFORMATIONS**

### **📊 Informations** `info.py, help.py`
| Commande | Description | Exemple |
|----------|-------------|---------|
| `/info` | Informations du bot | `/info` |
| `/help` | Guide d'aide | `/help` |

---

## 🆕 **NOUVEAUX SYSTÈMES AJOUTÉS**

### **🔒 Système de Captcha (NOUVEAU)**
**Objectif :** Vérifier que les nouveaux membres sont des humains et non des bots

**Comment ça marche :**
1. 👤 Un utilisateur rejoint le serveur
2. 🎯 Il reçoit le rôle "Non Vérifié" et ne voit que le salon #verification
3. 🔢 Un code captcha à 5 caractères est généré automatiquement
4. ✍️ L'utilisateur tape le code dans le salon de vérification
5. ✅ Code correct → Rôle "Vérifié" + accès au serveur
6. ❌ Code incorrect ou timeout → Expulsion automatique

**Configuration recommandée :**
```bash
/setup_captcha                    # Crée les rôles et salon
/captcha_config timeout_minutes:5 max_attempts:3 kick_on_fail:true
/send_welcome_message            # Message explicatif permanent
/toggle_captcha                  # Activer le système
```

### **🚫 Système Anti-Spam (NOUVEAU)**
**Objectif :** Détecter et sanctionner automatiquement le spam

**Comment ça marche :**
1. 📊 Le bot surveille tous les messages en temps réel
2. 🕐 Détection : Plus de 5 messages en 3 secondes = SPAM
3. 🗑️ Suppression automatique des messages de spam
4. ⚖️ Sanction appliquée : Timeout/Kick/Ban/Avertissement
5. 📝 Tout est enregistré dans les logs avec détails complets

**Sanctions disponibles :**
- **Timeout** - Silence temporaire (défaut: 5 minutes)
- **Kick** - Expulsion du serveur
- **Ban** - Bannissement temporaire ou permanent
- **Warn** - Système d'avertissements avec escalade

**Configuration recommandée :**
```bash
/setup_antispam                  # Crée le canal de logs
/antispam_config message_limit:5 time_window:3 sanction_type:timeout
/antispam_immunity @Modérateurs  # Immunité pour les mods
/toggle_antispam                 # Activer le système
```

### **🎫 Système de Tickets (NOUVEAU)**
**Objectif :** Système de support professionnel pour aider les membres

**Comment ça marche :**
1. 🎯 Panel avec 3 boutons : Support Général, Bug Report, Autre
2. 🎫 Clic → Ticket privé créé automatiquement (ticket-0001, etc.)
3. 👥 Accès : Créateur + Rôles Staff/Support configurés
4. 🛠️ Boutons de gestion : Fermer, Claim, Transcript
5. 📜 Fermeture → Transcript automatique envoyé par MP + logs
6. 🗑️ Canal supprimé après 10 secondes

**Fonctionnalités avancées :**
- **Claim System** - Staff peut s'assigner un ticket
- **Transcripts** - Historique complet des conversations
- **Limite utilisateur** - Max 3 tickets ouverts par personne
- **Logs détaillés** - Toutes les actions enregistrées
- **Ajout/Retrait** - Gérer l'accès aux tickets

**Configuration recommandée :**
```bash
/setup_tickets                   # Crée catégorie + logs
/tickets_config staff_role:@Staff support_role:@Support max_tickets:3
/ticket_panel #support           # Créer le panel public
/toggle_tickets                  # Activer le système
```

---

## 💡 **EXEMPLES D'UTILISATION DÉTAILLÉS**

### **🎯 Scénario 1 : Configuration d'un nouveau serveur**
```bash
# Étape 1 : Configuration initiale
/setup_captcha          # ✅ Crée rôles "Vérifié"/"Non Vérifié" + salon vérification
/setup_antispam         # ✅ Crée canal #logs-antispam
/setup_tickets          # ✅ Crée catégorie tickets + #logs-tickets
/setup_logs             # ✅ Crée tous les canaux de logs

# Étape 2 : Configuration des rôles
/tickets_config staff_role:@Staff support_role:@Support max_tickets:5
/antispam_immunity @Modérateurs
/antispam_immunity @Staff

# Étape 3 : Paramétrage personnalisé
/captcha_config timeout_minutes:10 max_attempts:5 kick_on_fail:true
/antispam_config message_limit:7 time_window:5 sanction_type:timeout timeout_duration:600

# Étape 4 : Activation
/toggle_captcha         # ✅ Active la vérification
/toggle_antispam        # ✅ Active l'anti-spam
/toggle_tickets         # ✅ Active les tickets

# Étape 5 : Interface utilisateur
/ticket_panel #support  # ✅ Panel avec boutons dans #support
/send_welcome_message   # ✅ Message explicatif captcha
```

### **🎯 Scénario 2 : Gestion quotidienne**
```bash
# Vérifier l'état des systèmes
/captcha_status         # 📊 3 membres en attente, système activé
/antispam_status        # 📊 Limite 5 msg/3s, 12 sanctions aujourd'hui
/tickets_status         # 📊 7 tickets ouverts, 4 claimés

# Gestion des utilisateurs problématiques
/antispam_stats @spammeur        # 📈 Voir ses avertissements
/clear_spam_warnings @utilisateur # 🧹 Reset ses avertissements
/bl @troll                       # 🚫 Blacklist immédiate
/verify_user @bloqué             # ✅ Vérification manuelle

# Gestion des tickets
/force_close #ticket-0015        # 🔒 Fermeture admin forcée
/ticket_add @expert #ticket-0020 # 👥 Ajouter un spécialiste
```

### **🎯 Scénario 3 : Résolution de problèmes**
```bash
# Problème : Trop de faux positifs anti-spam
/antispam_config message_limit:8 time_window:3  # ⚙️ Augmenter tolérance
/antispam_ignore #events                        # 🚫 Ignorer canal événements
/antispam_immunity @Animateurs                  # 🛡️ Protéger animateurs

# Problème : Captcha trop difficile
/captcha_config timeout_minutes:15 max_attempts:5  # ⏰ Plus de temps
/clear_pending                                     # 🧹 Reset en attente

# Problème : Trop de tickets
/tickets_config max_tickets:2    # 📉 Réduire limite par utilisateur
```

---

## ⚡ **GUIDE DE CONFIGURATION RAPIDE - ADMINISTRATEURS**

### **🚀 Configuration Express (5 minutes)**
Pour les administrateurs qui veulent juste que ça marche rapidement :

```bash
# 1️⃣ ÉTAPE 1 : Tout configurer automatiquement
/setup_captcha && /setup_antispam && /setup_tickets && /setup_logs

# 2️⃣ ÉTAPE 2 : Tout activer
/toggle_captcha && /toggle_antispam && /toggle_tickets

# 3️⃣ ÉTAPE 3 : Créer les interfaces
/ticket_panel #support
/send_welcome_message

# ✅ TERMINÉ ! Votre serveur est sécurisé en 5 minutes
```

### **⚙️ Configuration Personnalisée (15 minutes)**
Pour les administrateurs qui veulent personnaliser :

**Phase 1 - Sécurité de base :**
```bash
/setup_captcha                    # Vérification des nouveaux
/captcha_config timeout_minutes:10 max_attempts:3 kick_on_fail:true
/send_welcome_message             # Message explicatif
/toggle_captcha                   # ✅ ACTIVER
```

**Phase 2 - Anti-spam :**
```bash
/setup_antispam                   # Détection automatique
/antispam_config message_limit:5 time_window:3 sanction_type:timeout
/antispam_immunity @Modérateurs   # Protéger le staff
/antispam_immunity @Staff
/toggle_antispam                  # ✅ ACTIVER
```

**Phase 3 - Support :**
```bash
/setup_tickets                    # Système de tickets
/tickets_config staff_role:@Staff support_role:@Support max_tickets:3
/ticket_panel #support            # Panel public
/toggle_tickets                   # ✅ ACTIVER
```

**Phase 4 - Modération :**
```bash
/setup_logs                       # Logs complets
/wl @ProprietaireServeur         # Whitelist du propriétaire
/antijoins                        # Activer anti-joins si besoin
```

### **🎯 Permissions Recommandées**

**Permissions Bot (Obligatoires) :**
- ✅ **Gérer les rôles** (pour captcha + sanctions)
- ✅ **Gérer les canaux** (pour tickets + logs)
- ✅ **Expulser des membres** (pour sanctions)
- ✅ **Mettre en timeout** (pour anti-spam)
- ✅ **Gérer les messages** (pour supprimer spam)
- ✅ **Voir l'historique** (pour transcripts)

**Rôles Recommandés :**
```bash
🔴 @Staff        # Accès complet (tickets, vérifications, etc.)
🔵 @Modérateurs  # Immunité anti-spam + gestion basique
🟡 @Support      # Accès tickets seulement
🟢 @Vérifié     # Membres vérifiés (créé automatiquement)
🔴 @Non Vérifié # Nouveaux membres (créé automatiquement)
```

### **📊 Monitoring & Maintenance**

**Commandes de surveillance quotidienne :**
```bash
/captcha_status      # État vérifications
/antispam_status     # État anti-spam
/tickets_status      # État support
```

**Actions de maintenance :**
```bash
/clear_pending                    # Reset vérifications bloquées
/clear_spam_warnings @user        # Reset avertissements
/antispam_stats                   # Stats globales spam
```

### **🆘 Dépannage Rapide**

| Problème | Solution |
|----------|----------|
| Nouveaux membres ne voient pas #verification | `/setup_captcha` puis `/toggle_captcha` |
| Faux positifs anti-spam | `/antispam_immunity @Rôle` ou `/antispam_ignore #canal` |
| Tickets ne se créent pas | Vérifier permissions bot + `/toggle_tickets` |
| Pas de logs | `/setup_logs` puis vérifier permissions bot |
| Captcha trop dur | `/captcha_config timeout_minutes:15 max_attempts:5` |
| Trop de spam détecté | `/antispam_config message_limit:8 time_window:5` |

---

## 🎉 **RÉSUMÉ - VOTRE BOT EST MAINTENANT COMPLET !**

### **✨ Ce qui a été ajouté à votre bot :**

**🔐 Nouveaux Systèmes de Sécurité :**
- ✅ **Captcha automatique** - Vérification des nouveaux membres
- ✅ **Anti-spam intelligent** - Détection 5 msg/3s avec sanctions
- ✅ **Tickets professionnels** - Support avec transcripts automatiques

**🛠️ Systèmes Existants Organisés :**
- ✅ **Blacklist/Whitelist** - Gestion des utilisateurs
- ✅ **Anti-joins/Anti-bot** - Protection contre les raids
- ✅ **Logs complets** - Surveillance toutes actions
- ✅ **Niveaux** - Système d'expérience
- ✅ **Giveaways** - Concours automatisés

### **📊 Statistiques du Bot :**
- **🎯 Total : 48+ commandes** organisées en 6 catégories
- **📁 12 fichiers** de commandes + événements
- **💾 8 fichiers JSON** pour la sauvegarde
- **🔧 3 nouveaux systèmes** complets ajoutés

### **🚀 Configuration Ultra-Rapide :**
```bash
# Copier-coller cette ligne pour tout configurer en 30 secondes :
/setup_captcha && /setup_antispam && /setup_tickets && /toggle_captcha && /toggle_antispam && /toggle_tickets && /ticket_panel #support && /send_welcome_message
```

### **🎯 Votre bot peut maintenant :**
- ✅ **Vérifier automatiquement** tous les nouveaux membres
- ✅ **Détecter et sanctionner** le spam instantanément
- ✅ **Gérer les tickets** de support professionnellement
- ✅ **Logger toutes les actions** avec détails complets
- ✅ **Protéger contre les raids** et bots malveillants
- ✅ **Organiser des concours** et gérer les niveaux

**🏆 Résultat : Un bot Discord professionnel et complet, prêt pour un serveur de toute taille !**

---

## 📁 **STRUCTURE DES FICHIERS**

```
📂 katabump bot v2/
├── 📄 main.py                    # Fichier principal du bot
├── 📄 BOT.md                     # Ce guide complet
├── 📂 commands/                  # Toutes les commandes
│   ├── 📄 captcha.py            # 🆕 Système de vérification
│   ├── 📄 antispam.py           # 🆕 Anti-spam intelligent
│   ├── 📄 tickets.py            # 🆕 Système de tickets
│   ├── 📄 admin.py              # Commandes d'administration
│   ├── 📄 blacklist.py          # Gestion blacklist
│   ├── 📄 wl.py                 # Gestion whitelist
│   ├── 📄 antijoins.py          # Anti-joins/Anti-bot
│   ├── 📄 logs.py               # Système de logs
│   ├── 📄 level.py              # Système de niveaux
│   ├── 📄 giveaway.py           # Giveaways
│   ├── 📄 help.py               # Aide
│   └── 📄 info.py               # Informations
├── 📂 events/                   # Événements automatiques
│   ├── 📄 captcha_events.py     # 🆕 Événements captcha
│   ├── 📄 antispam_events.py    # 🆕 Événements anti-spam
│   ├── 📄 blacklist_events.py   # Événements blacklist
│   ├── 📄 antijoins_events.py   # Événements anti-joins
│   ├── 📄 logs_events.py        # Événements logs
│   ├── 📄 level_events.py       # Événements niveaux
│   └── 📄 wl_events.py          # Événements whitelist
└── 📂 Fichiers de données/      # Sauvegarde JSON
    ├── 📄 captcha_config.json   # 🆕 Config captcha
    ├── 📄 pending_verifications.json # 🆕 Vérifications en cours
    ├── 📄 antispam_config.json  # 🆕 Config anti-spam
    ├── 📄 spam_warnings.json    # 🆕 Avertissements spam
    ├── 📄 tickets_config.json   # 🆕 Config tickets
    ├── 📄 active_tickets.json   # 🆕 Tickets actifs
    ├── 📄 bl.json               # Blacklist
    ├── 📄 wl.json               # Whitelist
    ├── 📄 logs.json             # Config logs
    ├── 📄 level.json            # Données niveaux
    ├── 📄 antijoins_state.json  # État anti-joins
    ├── 📄 anti_bot.json         # État anti-bot
    └── 📄 *_giveaways.json      # Données giveaways
```

---

**📞 Support & Informations**
- **Version :** KataBump Bot v2
- **Dernière mise à jour :** Septembre 2025
- **Nouvelles fonctionnalités :** Captcha, Anti-spam, Tickets
- **Commandes totales :** 48+
- **Systèmes :** 9 complets

