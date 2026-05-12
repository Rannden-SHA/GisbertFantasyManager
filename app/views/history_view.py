"""
Transaction history view with timeline and filtering.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing
from widgets.search_bar import SearchBar
from utils import format_money, get_transaction_icon, get_transaction_label, get_transaction_color


class HistoryView(ctk.CTkFrame):
    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                         scrollbar_button_color=Colors.BG_TERTIARY,
                                         scrollbar_button_hover_color=Colors.BG_HOVER)
        scroll.pack(fill="both", expand=True)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.MD))
        ctk.CTkLabel(header, text="📜 Historial de Operaciones", font=Fonts.TITLE_LG,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")

        # Export button
        ctk.CTkButton(header, text="📥 Exportar CSV", font=Fonts.BODY_SM, height=36,
                       corner_radius=8, fg_color=Colors.BG_TERTIARY,
                       hover_color=Colors.BG_HOVER, border_width=1, border_color=Colors.BORDER,
                       text_color=Colors.TEXT_SECONDARY,
                       command=self._export_csv).pack(side="right")

        # Search + filters
        self.search = SearchBar(scroll, placeholder="Buscar en historial...",
                                 on_search=self._on_search,
                                 filters=[
                                     {"id": "purchase", "label": "🛒 Compras"},
                                     {"id": "sale", "label": "💰 Ventas"},
                                     {"id": "money", "label": "💵 Dinero"},
                                     {"id": "points", "label": "⭐ Puntos"},
                                 ])
        self.search.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        # Timeline
        self.timeline_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.timeline_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        self._render_timeline()

    def _render_timeline(self, search_term="", filter_type=""):
        for w in self.timeline_frame.winfo_children():
            w.destroy()

        transactions = self.db.get_transactions(tx_type=filter_type or "")
        if search_term:
            transactions = [tx for tx in transactions
                            if search_term.lower() in tx.participant.lower()
                            or search_term.lower() in tx.player_name.lower()
                            or search_term.lower() in tx.notes.lower()]

        if not transactions:
            ctk.CTkLabel(self.timeline_frame, text="Sin operaciones registradas",
                          font=Fonts.BODY, text_color=Colors.TEXT_MUTED).pack(pady=Spacing.XXL)
            return

        ctk.CTkLabel(self.timeline_frame, text=f"{len(transactions)} operaciones",
                      font=Fonts.BODY_SM, text_color=Colors.TEXT_MUTED).pack(anchor="w", pady=(0, Spacing.SM))

        for i, tx in enumerate(transactions):
            self._render_timeline_item(self.timeline_frame, tx, i == len(transactions) - 1)

    def _render_timeline_item(self, parent, tx, is_last):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")

        # Timeline line
        line_frame = ctk.CTkFrame(row, fg_color="transparent", width=40)
        line_frame.pack(side="left", fill="y")
        line_frame.pack_propagate(False)

        color = get_transaction_color(tx.type)

        # Dot
        dot = ctk.CTkFrame(line_frame, width=12, height=12, corner_radius=6, fg_color=color)
        dot.place(x=14, y=16)

        if not is_last:
            line = ctk.CTkFrame(line_frame, width=2, height=60, fg_color=Colors.BORDER)
            line.place(x=19, y=30)

        # Content card
        card = ctk.CTkFrame(row, corner_radius=10, fg_color=Colors.BG_CARD,
                              border_width=1, border_color=Colors.BORDER)
        card.pack(side="left", fill="x", expand=True, pady=(0, Spacing.XS))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)

        # Top: icon + type + participant
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        icon = get_transaction_icon(tx.type)
        label = get_transaction_label(tx.type)

        ctk.CTkLabel(top, text=f"{icon} {label}", font=Fonts.BODY_SM,
                      text_color=color).pack(side="left")
        ctk.CTkLabel(top, text=tx.participant, font=Fonts.BODY_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left", padx=(Spacing.SM, 0))

        # Amount
        ctk.CTkLabel(top, text=format_money(tx.amount, True), font=Fonts.MONO_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(side="right")

        # Details
        details = []
        if tx.player_name:
            details.append(f"Jugador: {tx.player_name}")
        if tx.market_value > 0:
            details.append(f"V. Mercado: {format_money(tx.market_value, True)}")
        if tx.overbid_percent != 0:
            details.append(f"Sobrepuja: {tx.overbid_percent:+.1f}%")
        if tx.notes and tx.type != "team_value":
            details.append(tx.notes)

        if details:
            detail_text = " • ".join(details)
            ctk.CTkLabel(inner, text=detail_text, font=Fonts.CAPTION,
                          text_color=Colors.TEXT_MUTED, anchor="w").pack(fill="x")

        # Saldo change
        saldo_text = f"Saldo: {format_money(tx.saldo_before, True)} → {format_money(tx.saldo_after, True)}"
        ctk.CTkLabel(inner, text=saldo_text, font=Fonts.CAPTION,
                      text_color=Colors.TEXT_MUTED, anchor="w").pack(fill="x")

        # Timestamp
        ts = tx.timestamp[:16].replace("T", " ") if tx.timestamp else ""
        ctk.CTkLabel(inner, text=ts, font=Fonts.CAPTION,
                      text_color=Colors.TEXT_DISABLED, anchor="w").pack(fill="x")

    def _on_search(self, term, filter_id):
        self._render_timeline(search_term=term, filter_type=filter_id or "")

    def _export_csv(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                              filetypes=[("CSV", "*.csv")])
        if path:
            self.db.export_transactions_csv(path)
            from tkinter import messagebox
            messagebox.showinfo("Exportado", f"Historial exportado a:\n{path}")

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
