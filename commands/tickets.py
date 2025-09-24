import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timezone
import asyncio
import io

def load_tickets_config():
    if os.path.exists("tickets_config.json"):
        with open("tickets_config.json", "r") as file:
            data = json.load(file)
            default_config = {
                "enabled": False,
                "category_id": 0,
                "logs_channel_id": 0,
                "staff_role_id": 0,
                "support_role_id": 0,
                "panel_channel_id": 0,
                "panel_message_id": 0,
                "ticket_counter": 0,
                "max_tickets_per_user": 3,
                "auto_close_inactive": False,
                "inactive_hours": 24,
                "ticket_categories": {
                    "general": {
                        "name": "Support Général",
                        "emoji": "🎫",
                        "description": "Questions générales et aide"
                    },
                    "bug": {
                        "name": "Report de Bug",
                        "emoji": "🐛",
                        "description": "Signaler un problème technique"
                    },
                    "other": {
                        "name": "Autre",
                        "emoji": "❓",
                        "description": "Autres demandes"
                    }
                }
            }
            return {**default_config, **data}
    return {
        "enabled": False,
        "category_id": 0,
        "logs_channel_id": 0,
        "staff_role_id": 0,
        "support_role_id": 0,
        "panel_channel_id": 0,
        "panel_message_id": 0,
        "ticket_counter": 0,
        "max_tickets_per_user": 3,
        "auto_close_inactive": False,
        "inactive_hours": 24,
        "ticket_categories": {
            "general": {
                "name": "Support Général",
                "emoji": "🎫",
                "description": "Questions générales et aide"
            },
            "bug": {
                "name": "Report de Bug",
                "emoji": "🐛",
                "description": "Signaler un problème technique"
            },
            "other": {
                "name": "Autre",
                "emoji": "❓",
                "description": "Autres demandes"
            }
        }
    }

def save_tickets_config(config):
    with open("tickets_config.json", "w") as file:
        json.dump(config, file, indent=2)

def load_active_tickets():
    if os.path.exists("active_tickets.json"):
        with open("active_tickets.json", "r") as file:
            return json.load(file)
    return {}

def save_active_tickets(data):
    with open("active_tickets.json", "w") as file:
        json.dump(data, file, indent=2)

class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Support Général", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="ticket_general")
    async def general_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "general")

    @discord.ui.button(label="Report de Bug", style=discord.ButtonStyle.danger, emoji="🐛", custom_id="ticket_bug")
    async def bug_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "bug")

    @discord.ui.button(label="Autre", style=discord.ButtonStyle.secondary, emoji="❓", custom_id="ticket_other")
    async def other_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "other")

    async def create_ticket(self, interaction: discord.Interaction, category: str):
        config = load_tickets_config()

        if not config["enabled"]:
            await interaction.response.send_message("❌ Le système de tickets est désactivé.", ephemeral=True)
            return

        # Vérifier si l'utilisateur a déjà trop de tickets ouverts
        active_tickets = load_active_tickets()
        user_tickets = [t for t in active_tickets.values() if t["user_id"] == interaction.user.id and t["status"] == "open"]

        if len(user_tickets) >= config["max_tickets_per_user"]:
            await interaction.response.send_message(f"❌ Vous avez déjà {config['max_tickets_per_user']} ticket(s) ouvert(s). Fermez-en un avant d'en créer un nouveau.", ephemeral=True)
            return

        guild = interaction.guild
        category_channel = guild.get_channel(config["category_id"])

        if not category_channel:
            await interaction.response.send_message("❌ Catégorie de tickets non configurée.", ephemeral=True)
            return

        # Incrémenter le compteur de tickets
        config["ticket_counter"] += 1
        ticket_number = config["ticket_counter"]
        save_tickets_config(config)

        # Créer le canal du ticket
        ticket_name = f"ticket-{ticket_number:04d}"

        # Permissions du ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True, manage_messages=True)
        }

        # Ajouter les rôles staff/support
        if config["staff_role_id"]:
            staff_role = guild.get_role(config["staff_role_id"])
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)

        if config["support_role_id"]:
            support_role = guild.get_role(config["support_role_id"])
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        try:
            ticket_channel = await guild.create_text_channel(
                ticket_name,
                category=category_channel,
                overwrites=overwrites,
                reason=f"Ticket créé par {interaction.user}"
            )

            # Enregistrer le ticket
            ticket_data = {
                "channel_id": ticket_channel.id,
                "user_id": interaction.user.id,
                "category": category,
                "status": "open",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "claimed_by": None,
                "messages": []
            }

            active_tickets[str(ticket_channel.id)] = ticket_data
            save_active_tickets(active_tickets)

            # Créer l'embed d'accueil
            category_info = config["ticket_categories"].get(category, config["ticket_categories"]["general"])
            embed = discord.Embed(
                title=f"{category_info['emoji']} {category_info['name']} - Ticket #{ticket_number:04d}",
                description=f"Bonjour {interaction.user.mention} !\n\nVotre ticket a été créé avec succès. Un membre du staff va vous aider bientôt.\n\n**Catégorie:** {category_info['description']}",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="📋 Instructions", value="• Décrivez votre problème en détail\n• Restez poli et patient\n• Utilisez les boutons ci-dessous pour les actions", inline=False)
            embed.set_footer(text=f"Ticket de {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

            # Vue avec boutons de gestion
            view = TicketManagement()

            welcome_msg = await ticket_channel.send(f"{interaction.user.mention}", embed=embed, view=view)

            # Pin le message d'accueil
            await welcome_msg.pin()

            await interaction.response.send_message(f"✅ Votre ticket a été créé ! {ticket_channel.mention}", ephemeral=True)

            # Log la création
            await self.log_ticket_action(guild, "create", interaction.user, ticket_channel, category_info["name"])

        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas les permissions pour créer le ticket.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de la création du ticket: {str(e)}", ephemeral=True)

    async def log_ticket_action(self, guild, action, user, channel, extra_info=""):
        config = load_tickets_config()
        if config["logs_channel_id"] == 0:
            return

        logs_channel = guild.get_channel(config["logs_channel_id"])
        if not logs_channel:
            return

        action_colors = {
            "create": discord.Color.green(),
            "close": discord.Color.red(),
            "claim": discord.Color.blue(),
            "unclaim": discord.Color.orange()
        }

        action_titles = {
            "create": "🎫 Ticket Créé",
            "close": "🔒 Ticket Fermé",
            "claim": "👤 Ticket Réclamé",
            "unclaim": "🔄 Ticket Libéré"
        }

        embed = discord.Embed(
            title=action_titles.get(action, "📋 Action Ticket"),
            color=action_colors.get(action, discord.Color.blue()),
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(name="👤 Utilisateur", value=f"{user.mention} ({user.id})", inline=True)
        embed.add_field(name="📍 Canal", value=f"{channel.mention}" if channel else "Canal supprimé", inline=True)

        if extra_info:
            embed.add_field(name="ℹ️ Détails", value=extra_info, inline=False)

        embed.set_thumbnail(url=user.display_avatar.url)

        try:
            await logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass

class TicketManagement(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fermer", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CloseTicketModal())

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="👤", custom_id="ticket_claim")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = load_tickets_config()

        # Vérifier si l'utilisateur a les permissions
        if not self.has_ticket_permissions(interaction.user, config):
            await interaction.response.send_message("❌ Vous n'avez pas les permissions pour claim ce ticket.", ephemeral=True)
            return

        active_tickets = load_active_tickets()
        ticket_data = active_tickets.get(str(interaction.channel.id))

        if not ticket_data:
            await interaction.response.send_message("❌ Ce ticket n'est pas enregistré.", ephemeral=True)
            return

        if ticket_data.get("claimed_by"):
            claimer = interaction.guild.get_member(ticket_data["claimed_by"])
            await interaction.response.send_message(f"❌ Ce ticket est déjà claim par {claimer.mention if claimer else 'un membre du staff'}.", ephemeral=True)
            return

        # Claim le ticket
        ticket_data["claimed_by"] = interaction.user.id
        active_tickets[str(interaction.channel.id)] = ticket_data
        save_active_tickets(active_tickets)

        embed = discord.Embed(
            title="👤 Ticket Claim",
            description=f"{interaction.user.mention} s'occupe maintenant de ce ticket.",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )

        await interaction.response.send_message(embed=embed)

        # Log l'action
        panel = TicketPanel()
        await panel.log_ticket_action(interaction.guild, "claim", interaction.user, interaction.channel)

    @discord.ui.button(label="Transcript", style=discord.ButtonStyle.secondary, emoji="📜", custom_id="ticket_transcript")
    async def transcript_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = load_tickets_config()

        if not self.has_ticket_permissions(interaction.user, config):
            await interaction.response.send_message("❌ Vous n'avez pas les permissions pour générer un transcript.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Générer le transcript
            transcript_file = await self.generate_transcript(interaction.channel)

            # Créer un fichier
            filename = f"transcript-{interaction.channel.name}.txt"
            file = discord.File(transcript_file, filename=filename)

            await interaction.followup.send("📜 Transcript du ticket:", file=file, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la génération du transcript: {str(e)}", ephemeral=True)

    def has_ticket_permissions(self, user, config):
        """Vérifier si l'utilisateur a les permissions pour gérer les tickets"""
        if user.guild_permissions.administrator:
            return True

        user_role_ids = [role.id for role in user.roles]
        return (config["staff_role_id"] in user_role_ids or
                config["support_role_id"] in user_role_ids)

    async def generate_transcript(self, channel):
        """Générer un transcript du ticket"""
        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            author = f"{message.author.display_name} ({message.author.id})"
            content = message.content or "[Message vide ou embed]"

            if message.attachments:
                content += "\n[Fichiers joints: " + ", ".join(att.filename for att in message.attachments) + "]"

            messages.append(f"[{timestamp}] {author}: {content}")

        transcript_content = f"""=== TRANSCRIPT DU TICKET ===
Canal: {channel.name}
Généré le: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")} UTC
Nombre de messages: {len(messages)}

{'='*50}

""" + "\n".join(messages)

        # Créer un objet BytesIO au lieu de retourner directement les bytes
        transcript_file = io.BytesIO(transcript_content.encode('utf-8'))
        transcript_file.seek(0)
        return transcript_file

class CloseTicketModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Fermer le Ticket")

    reason = discord.ui.TextInput(
        label="Raison de la fermeture",
        placeholder="Pourquoi fermez-vous ce ticket ?",
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        config = load_tickets_config()
        active_tickets = load_active_tickets()

        ticket_data = active_tickets.get(str(interaction.channel.id))
        if not ticket_data:
            await interaction.response.send_message("❌ Ce ticket n'est pas enregistré.", ephemeral=True)
            return

        # Générer le transcript automatiquement
        ticket_mgmt = TicketManagement()
        transcript_file = await ticket_mgmt.generate_transcript(interaction.channel)
        filename = f"transcript-{interaction.channel.name}.txt"

        # Envoyer le transcript au créateur du ticket
        ticket_creator = interaction.guild.get_member(ticket_data["user_id"])
        if ticket_creator:
            try:
                embed = discord.Embed(
                    title="🔒 Ticket Fermé",
                    description=f"Votre ticket sur **{interaction.guild.name}** a été fermé.",
                    color=discord.Color.red(),
                    timestamp=datetime.now(timezone.utc)
                )

                if self.reason.value:
                    embed.add_field(name="📝 Raison", value=self.reason.value, inline=False)

                embed.add_field(name="👤 Fermé par", value=interaction.user.display_name, inline=True)
                embed.set_footer(text="Merci d'avoir utilisé notre système de support !")

                # Créer une copie du transcript pour l'utilisateur
                transcript_file.seek(0)
                user_file = discord.File(io.BytesIO(transcript_file.read()), filename=filename)
                await ticket_creator.send(embed=embed, file=user_file)
            except discord.Forbidden:
                pass

        # Envoyer le transcript dans les logs
        if config["logs_channel_id"]:
            logs_channel = interaction.guild.get_channel(config["logs_channel_id"])
            if logs_channel:
                try:
                    log_embed = discord.Embed(
                        title="🔒 Ticket Fermé",
                        color=discord.Color.red(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    log_embed.add_field(name="👤 Créateur", value=f"<@{ticket_data['user_id']}>", inline=True)
                    log_embed.add_field(name="👤 Fermé par", value=interaction.user.mention, inline=True)
                    log_embed.add_field(name="📍 Canal", value=f"#{interaction.channel.name}", inline=True)

                    if self.reason.value:
                        log_embed.add_field(name="📝 Raison", value=self.reason.value, inline=False)

                    # Créer une copie du transcript pour les logs
                    transcript_file.seek(0)
                    logs_file = discord.File(io.BytesIO(transcript_file.read()), filename=filename)
                    await logs_channel.send(embed=log_embed, file=logs_file)
                except discord.Forbidden:
                    pass

        # Supprimer le ticket des tickets actifs
        if str(interaction.channel.id) in active_tickets:
            del active_tickets[str(interaction.channel.id)]
            save_active_tickets(active_tickets)

        # Message de fermeture
        embed = discord.Embed(
            title="🔒 Fermeture du Ticket",
            description="Ce ticket sera supprimé dans 10 secondes...",
            color=discord.Color.red()
        )

        if self.reason.value:
            embed.add_field(name="📝 Raison", value=self.reason.value, inline=False)

        await interaction.response.send_message(embed=embed)

        # Attendre et supprimer le canal
        await asyncio.sleep(10)
        try:
            await interaction.channel.delete(reason=f"Ticket fermé par {interaction.user}")
        except discord.NotFound:
            pass

class Tickets(commands.Cog):
    def __init__(self, client):
        self.client = client
        # Ajouter les vues persistantes au démarrage
        self.client.add_view(TicketPanel())
        self.client.add_view(TicketManagement())

    @app_commands.command(name="setup_tickets", description="Configurer le système de tickets")
    @app_commands.default_permissions(administrator=True)
    async def setup_tickets(self, inter: discord.Interaction):
        await inter.response.send_message("⚙️ Configuration du système de tickets en cours...", ephemeral=True)

        try:
            config = load_tickets_config()
            guild = inter.guild

            # Créer la catégorie des tickets
            if config["category_id"] == 0:
                tickets_category = await guild.create_category(
                    "🎫 ━━━ TICKETS ━━━",
                    reason="Catégorie pour le système de tickets"
                )
                config["category_id"] = tickets_category.id

            # Créer le canal des logs
            if config["logs_channel_id"] == 0:
                logs_category = discord.utils.get(guild.categories, name="📁・Espace logs")
                if not logs_category:
                    logs_category = await guild.create_category("📁・Espace logs")

                logs_channel = await guild.create_text_channel(
                    "📁・logs-tickets",
                    category=logs_category,
                    reason="Canal de logs pour les tickets"
                )
                config["logs_channel_id"] = logs_channel.id

                # Permissions du canal logs
                await logs_channel.set_permissions(guild.default_role, read_messages=False)

            save_tickets_config(config)

            # Réponse de succès
            category = guild.get_channel(config["category_id"])
            logs = guild.get_channel(config["logs_channel_id"])

            embed = discord.Embed(
                title="✅ Configuration des Tickets terminée",
                description="Le système de tickets a été configuré avec succès !",
                color=discord.Color.green()
            )
            embed.add_field(name="📊 Statut", value="❌ Désactivé" if not config["enabled"] else "✅ Activé", inline=True)
            embed.add_field(name="📁 Catégorie", value=category.mention if category else "❌ Erreur", inline=True)
            embed.add_field(name="📝 Logs", value=logs.mention if logs else "❌ Erreur", inline=True)
            embed.add_field(name="🎫 Tickets créés", value=f"{config['ticket_counter']}", inline=True)
            embed.add_field(name="📊 Max par utilisateur", value=f"{config['max_tickets_per_user']}", inline=True)

            await inter.edit_original_response(content=None, embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur de Configuration",
                description=f"Erreur lors de la configuration : {str(e)}",
                color=discord.Color.red()
            )
            await inter.edit_original_response(content=None, embed=error_embed)

    @app_commands.command(name="toggle_tickets", description="Activer ou désactiver le système de tickets")
    @app_commands.default_permissions(administrator=True)
    async def toggle_tickets(self, inter: discord.Interaction):
        config = load_tickets_config()
        config["enabled"] = not config["enabled"]
        save_tickets_config(config)

        status = "✅ activé" if config["enabled"] else "❌ désactivé"
        embed = discord.Embed(
            title="🔄 Système de Tickets mis à jour",
            description=f"Le système de tickets est maintenant {status}",
            color=discord.Color.green() if config["enabled"] else discord.Color.red()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ticket_panel", description="Créer le panel de création de tickets")
    @app_commands.default_permissions(administrator=True)
    async def ticket_panel(self, inter: discord.Interaction, channel: discord.TextChannel = None):
        config = load_tickets_config()

        if not config["enabled"]:
            await inter.response.send_message("❌ Le système de tickets est désactivé. Activez-le avec `/toggle_tickets`.", ephemeral=True)
            return

        target_channel = channel or inter.channel

        # Créer l'embed du panel
        embed = discord.Embed(
            title="🎫 Système de Support",
            description="Besoin d'aide ? Créez un ticket en cliquant sur l'un des boutons ci-dessous selon votre demande.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🎫 Support Général",
            value="Questions générales et aide",
            inline=True
        )
        embed.add_field(
            name="🐛 Report de Bug",
            value="Signaler un problème technique",
            inline=True
        )
        embed.add_field(
            name="❓ Autre",
            value="Autres demandes",
            inline=True
        )

        embed.add_field(
            name="📋 Instructions",
            value="• Un seul ticket par problème\n• Soyez précis dans votre demande\n• Restez poli et patient\n• Un staff vous répondra rapidement",
            inline=False
        )

        embed.set_footer(text="Système de tickets • Cliquez sur un bouton pour commencer")

        view = TicketPanel()

        try:
            message = await target_channel.send(embed=embed, view=view)

            # Sauvegarder l'ID du message du panel
            config["panel_channel_id"] = target_channel.id
            config["panel_message_id"] = message.id
            save_tickets_config(config)

            await inter.response.send_message(f"✅ Panel de tickets créé dans {target_channel.mention}", ephemeral=True)

        except discord.Forbidden:
            await inter.response.send_message("❌ Je n'ai pas les permissions pour envoyer des messages dans ce canal.", ephemeral=True)

    @app_commands.command(name="tickets_config", description="Configurer les paramètres des tickets")
    @app_commands.default_permissions(administrator=True)
    async def tickets_config(self, inter: discord.Interaction,
                           staff_role: discord.Role = None,
                           support_role: discord.Role = None,
                           max_tickets: int = None):

        config = load_tickets_config()

        if staff_role:
            config["staff_role_id"] = staff_role.id

        if support_role:
            config["support_role_id"] = support_role.id

        if max_tickets is not None:
            if max_tickets < 1 or max_tickets > 10:
                await inter.response.send_message("❌ Le nombre maximum de tickets par utilisateur doit être entre 1 et 10.", ephemeral=True)
                return
            config["max_tickets_per_user"] = max_tickets

        save_tickets_config(config)

        embed = discord.Embed(
            title="⚙️ Configuration des Tickets mise à jour",
            color=discord.Color.blue()
        )

        if staff_role:
            embed.add_field(name="👨‍💼 Rôle Staff", value=staff_role.mention, inline=True)
        if support_role:
            embed.add_field(name="🎧 Rôle Support", value=support_role.mention, inline=True)
        if max_tickets:
            embed.add_field(name="📊 Max tickets/utilisateur", value=str(max_tickets), inline=True)

        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="tickets_status", description="Afficher le statut du système de tickets")
    @app_commands.default_permissions(administrator=True)
    async def tickets_status(self, inter: discord.Interaction):
        config = load_tickets_config()
        active_tickets = load_active_tickets()
        guild = inter.guild

        # Compter les tickets par statut
        open_tickets = len([t for t in active_tickets.values() if t["status"] == "open"])
        claimed_tickets = len([t for t in active_tickets.values() if t.get("claimed_by")])

        embed = discord.Embed(
            title="🎫 Statut du Système de Tickets",
            color=discord.Color.blue() if config["enabled"] else discord.Color.greyple()
        )

        # Statut général
        status_value = "✅ Activé" if config["enabled"] else "❌ Désactivé"
        embed.add_field(name="📊 Statut", value=status_value, inline=True)
        embed.add_field(name="🎫 Tickets ouverts", value=f"{open_tickets}", inline=True)
        embed.add_field(name="👤 Tickets claim", value=f"{claimed_tickets}", inline=True)

        # Configuration
        embed.add_field(name="📈 Total créés", value=f"{config['ticket_counter']}", inline=True)
        embed.add_field(name="📊 Max par utilisateur", value=f"{config['max_tickets_per_user']}", inline=True)

        # Rôles et canaux
        category = guild.get_channel(config["category_id"])
        logs_channel = guild.get_channel(config["logs_channel_id"])
        staff_role = guild.get_role(config["staff_role_id"])
        support_role = guild.get_role(config["support_role_id"])

        embed.add_field(name="📁 Catégorie", value=category.mention if category else "❌ Non configuré", inline=True)
        embed.add_field(name="📝 Canal logs", value=logs_channel.mention if logs_channel else "❌ Non configuré", inline=True)

        if staff_role or support_role:
            roles_text = ""
            if staff_role:
                roles_text += f"**Staff:** {staff_role.mention}\n"
            if support_role:
                roles_text += f"**Support:** {support_role.mention}"
            embed.add_field(name="👥 Rôles", value=roles_text, inline=False)

        await inter.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="force_close", description="Forcer la fermeture d'un ticket")
    @app_commands.default_permissions(administrator=True)
    async def force_close(self, inter: discord.Interaction, channel: discord.TextChannel = None):
        target_channel = channel or inter.channel
        active_tickets = load_active_tickets()

        ticket_data = active_tickets.get(str(target_channel.id))
        if not ticket_data:
            await inter.response.send_message("❌ Ce canal n'est pas un ticket enregistré.", ephemeral=True)
            return

        # Générer transcript
        ticket_mgmt = TicketManagement()
        transcript_file = await ticket_mgmt.generate_transcript(target_channel)
        filename = f"transcript-{target_channel.name}.txt"

        # Envoyer le transcript au créateur
        ticket_creator = inter.guild.get_member(ticket_data["user_id"])
        if ticket_creator:
            try:
                embed = discord.Embed(
                    title="🔒 Ticket Fermé (Force)",
                    description=f"Votre ticket sur **{inter.guild.name}** a été fermé par un administrateur.",
                    color=discord.Color.red()
                )
                embed.add_field(name="👤 Fermé par", value=inter.user.display_name, inline=True)

                transcript_file.seek(0)
                file = discord.File(io.BytesIO(transcript_file.read()), filename=filename)
                await ticket_creator.send(embed=embed, file=file)
            except discord.Forbidden:
                pass

        # Supprimer du registre
        if str(target_channel.id) in active_tickets:
            del active_tickets[str(target_channel.id)]
            save_active_tickets(active_tickets)

        await inter.response.send_message("✅ Le ticket sera fermé dans 5 secondes...", ephemeral=True)

        await asyncio.sleep(5)
        try:
            await target_channel.delete(reason=f"Ticket fermé de force par {inter.user}")
        except discord.NotFound:
            pass

    @app_commands.command(name="ticket_add", description="Ajouter un utilisateur à un ticket")
    @app_commands.default_permissions(manage_channels=True)
    async def ticket_add(self, inter: discord.Interaction, user: discord.Member, channel: discord.TextChannel = None):
        target_channel = channel or inter.channel
        active_tickets = load_active_tickets()

        if str(target_channel.id) not in active_tickets:
            await inter.response.send_message("❌ Ce canal n'est pas un ticket enregistré.", ephemeral=True)
            return

        try:
            await target_channel.set_permissions(user, read_messages=True, send_messages=True)

            embed = discord.Embed(
                title="👤 Utilisateur Ajouté",
                description=f"{user.mention} a été ajouté à ce ticket par {inter.user.mention}.",
                color=discord.Color.green()
            )

            await target_channel.send(embed=embed)
            await inter.response.send_message(f"✅ {user.mention} a été ajouté au ticket.", ephemeral=True)

        except discord.Forbidden:
            await inter.response.send_message("❌ Je n'ai pas les permissions pour modifier ce canal.", ephemeral=True)

    @app_commands.command(name="ticket_remove", description="Retirer un utilisateur d'un ticket")
    @app_commands.default_permissions(manage_channels=True)
    async def ticket_remove(self, inter: discord.Interaction, user: discord.Member, channel: discord.TextChannel = None):
        target_channel = channel or inter.channel
        active_tickets = load_active_tickets()

        if str(target_channel.id) not in active_tickets:
            await inter.response.send_message("❌ Ce canal n'est pas un ticket enregistré.", ephemeral=True)
            return

        # Ne pas permettre de retirer le créateur du ticket
        ticket_data = active_tickets[str(target_channel.id)]
        if user.id == ticket_data["user_id"]:
            await inter.response.send_message("❌ Vous ne pouvez pas retirer le créateur du ticket.", ephemeral=True)
            return

        try:
            await target_channel.set_permissions(user, overwrite=None)

            embed = discord.Embed(
                title="👤 Utilisateur Retiré",
                description=f"{user.mention} a été retiré de ce ticket par {inter.user.mention}.",
                color=discord.Color.orange()
            )

            await target_channel.send(embed=embed)
            await inter.response.send_message(f"✅ {user.mention} a été retiré du ticket.", ephemeral=True)

        except discord.Forbidden:
            await inter.response.send_message("❌ Je n'ai pas les permissions pour modifier ce canal.", ephemeral=True)

async def setup(client):
    await client.add_cog(Tickets(client))