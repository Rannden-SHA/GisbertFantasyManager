"""
Market operations view — unified buy/sell/money/points interface.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing, Fantasy
from widgets.transaction_form import TransactionForm
from widgets.data_table import DataTable
from models import Transaction, Player
from utils import format_money, calculate_overbid_percent, get_transaction_icon, get_transaction_label
from datetime import datetime


class MarketView(ctk.CTkFrame):
    def __init__(self, parent, db, on_refresh=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db
        self.on_refresh = on_refresh
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                         scrollbar_button_color=Colors.BG_TERTIARY,
                                         scrollbar_button_hover_color=Colors.BG_HOVER)
        scroll.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.MD))
        ctk.CTkLabel(header, text="🏪 Mercado de Operaciones", font=Fonts.TITLE_LG,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")

        # Layout: Form left, Recent right
        content = ctk.CTkFrame(scroll, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)

        # Transaction form
        participants = [p.name for p in self.db.get_participants()]
        self.form = TransactionForm(content, participants=participants,
                                     on_submit=self._handle_submit, form_type="purchase")
        self.form.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.SM))

        # Recent transactions
        self._build_recent(content)

        # Undo button
        undo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        undo_frame.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))
        ctk.CTkButton(undo_frame, text="↩ Deshacer Última Operación", font=Fonts.BODY_SM,
                       height=36, corner_radius=8, fg_color=Colors.BG_TERTIARY,
                       hover_color=Colors.ACCENT_RED_HOVER, text_color=Colors.ACCENT_RED,
                       border_width=1, border_color=Colors.BORDER,
                       command=self._undo_last).pack(side="right")

    def _build_recent(self, parent):
        recent_frame = ctk.CTkFrame(parent, corner_radius=14, fg_color=Colors.BG_CARD,
                                     border_width=1, border_color=Colors.BORDER)
        recent_frame.grid(row=0, column=1, sticky="nsew", padx=(Spacing.SM, 0))

        container = ctk.CTkFrame(recent_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(container, text="📋 Últimas Operaciones", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.MD))

        recent = self.db.get_transactions(limit=12)
        if not recent:
            ctk.CTkLabel(container, text="Sin operaciones registradas", font=Fonts.BODY_SM,
                          text_color=Colors.TEXT_MUTED).pack(pady=Spacing.XL)
            return

        for tx in recent:
            row = ctk.CTkFrame(container, fg_color="transparent", height=32)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            icon = get_transaction_icon(tx.type)
            ctk.CTkLabel(row, text=icon, font=("Segoe UI Emoji", 11), width=20).pack(side="left")
            ctk.CTkLabel(row, text=tx.participant, font=Fonts.CAPTION,
                          text_color=Colors.TEXT_PRIMARY, width=70, anchor="w").pack(side="left")

            desc = tx.player_name or get_transaction_label(tx.type)
            ctk.CTkLabel(row, text=desc, font=Fonts.CAPTION,
                          text_color=Colors.TEXT_SECONDARY, anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(row, text=format_money(tx.amount, True), font=Fonts.CAPTION,
                          text_color=Colors.TEXT_MUTED).pack(side="right")

    def _handle_submit(self, data):
        try:
            tx_type = data["type"]
            participant_name = data["participant"]
            participant = self.db.get_participant(participant_name)
            if not participant:
                self._show_error("Participante no encontrado")
                return

            prev_saldo = participant.saldo

            if tx_type == "purchase":
                amount = float(data.get("amount", 0))
                market_value = float(data.get("market_value", 0))
                player_name = data.get("player_name", "")
                if not player_name or amount <= 0:
                    self._show_error("Completa todos los campos")
                    return
                new_saldo = prev_saldo - amount
                overbid = calculate_overbid_percent(amount, market_value)
                tx = Transaction(participant=participant_name, type="purchase",
                                  player_name=player_name, amount=amount,
                                  market_value=market_value, saldo_before=prev_saldo,
                                  saldo_after=new_saldo, overbid_percent=overbid)
                self.db.update_participant_saldo(participant_name, new_saldo)
                self.db.add_transaction(tx)
                # Add player to database
                player = Player(name=player_name, market_value=market_value,
                                 owner=participant_name, purchase_price=amount,
                                 purchase_date=datetime.now().isoformat())
                self.db.add_player(player)

            elif tx_type == "sale":
                amount = float(data.get("amount", 0))
                player_name = data.get("player_name", "")
                if not player_name or amount <= 0:
                    self._show_error("Completa todos los campos")
                    return
                new_saldo = prev_saldo + amount
                tx = Transaction(participant=participant_name, type="sale",
                                  player_name=player_name, amount=amount,
                                  saldo_before=prev_saldo, saldo_after=new_saldo)
                self.db.update_participant_saldo(participant_name, new_saldo)
                self.db.add_transaction(tx)

            elif tx_type == "money":
                amount = float(data.get("amount", 0))
                if amount == 0:
                    self._show_error("Introduce una cantidad")
                    return
                new_saldo = prev_saldo + amount
                tx = Transaction(participant=participant_name, type="money",
                                  amount=amount, saldo_before=prev_saldo, saldo_after=new_saldo)
                self.db.update_participant_saldo(participant_name, new_saldo)
                self.db.add_transaction(tx)

            elif tx_type == "points":
                points = int(float(data.get("points", 0)))
                if points == 0:
                    self._show_error("Introduce los puntos")
                    return
                money = points * Fantasy.POINTS_TO_MONEY_MULTIPLIER
                new_saldo = prev_saldo + money
                tx = Transaction(participant=participant_name, type="points",
                                  amount=money, saldo_before=prev_saldo, saldo_after=new_saldo,
                                  notes=f"{points} puntos")
                self.db.update_participant_saldo(participant_name, new_saldo)
                self.db.add_transaction(tx)
                # Update total points
                participant.total_points += points
                self.db.update_participant_points(participant_name, participant.total_points)

            elif tx_type == "team_value":
                new_value = float(data.get("amount", 0))
                tx = Transaction(participant=participant_name, type="team_value",
                                  amount=new_value, saldo_before=prev_saldo, saldo_after=prev_saldo,
                                  notes=f"Valor equipo actualizado a {new_value:,.0f}€")
                self.db.update_participant_team_value(participant_name, new_value)
                self.db.add_transaction(tx)

            # Success feedback
            self.form.clear()
            self._show_success("Operación registrada correctamente")
            if self.on_refresh:
                self.on_refresh()

        except (ValueError, TypeError) as e:
            self._show_error(f"Error en los datos: {str(e)}")

    def _undo_last(self):
        last_tx = self.db.get_last_transaction()
        if not last_tx:
            return
        # Revert saldo
        participant = self.db.get_participant(last_tx.participant)
        if participant:
            self.db.update_participant_saldo(last_tx.participant, last_tx.saldo_before)
            if last_tx.type == "team_value":
                # Cannot fully revert team value without storing old value — skip
                pass
            elif last_tx.type == "points" and last_tx.notes:
                try:
                    pts = int(last_tx.notes.split()[0])
                    self.db.update_participant_points(last_tx.participant, participant.total_points - pts)
                except (ValueError, IndexError):
                    pass
        self.db.delete_transaction(last_tx.id)
        self._show_success("Última operación deshecha")
        if self.on_refresh:
            self.on_refresh()

    def _show_error(self, msg):
        from tkinter import messagebox
        messagebox.showerror("Error", msg)

    def _show_success(self, msg):
        from tkinter import messagebox
        messagebox.showinfo("Éxito", msg)

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
