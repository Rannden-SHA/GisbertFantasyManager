"""
Main dashboard view with KPIs, rankings, and activity feed.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing
from widgets.stat_card import StatCard
from widgets.data_table import DataTable
from utils import format_money, get_rank_medal, get_saldo_color, get_budget_health


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db, on_navigate=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db
        self.on_navigate = on_navigate
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                         scrollbar_button_color=Colors.BG_TERTIARY,
                                         scrollbar_button_hover_color=Colors.BG_HOVER)
        scroll.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.MD))
        ctk.CTkLabel(header, text="📊 Dashboard", font=Fonts.TITLE_LG,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")

        config = self.db.get_config()
        if config:
            ctk.CTkLabel(header, text=f"Liga: {config.name}", font=Fonts.BODY,
                          text_color=Colors.TEXT_SECONDARY).pack(side="right")

        # KPI Cards row
        kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        participants = self.db.get_participants()
        total_saldo = sum(p.saldo for p in participants)
        total_valor = sum(p.valor_equipo for p in participants)
        total_value = sum(p.valor_total for p in participants)
        tx_count = self.db.get_total_transactions_count()

        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        StatCard(kpi_frame, title="Saldo Total Liga", value=format_money(total_saldo, True),
                  icon="💰", accent_color=Colors.ACCENT_GREEN,
                  subtitle=f"{len(participants)} participantes").grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        StatCard(kpi_frame, title="Valor Total Equipos", value=format_money(total_valor, True),
                  icon="🏟️", accent_color=Colors.ACCENT_BLUE).grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        StatCard(kpi_frame, title="Valor Total Liga", value=format_money(total_value, True),
                  icon="🏆", accent_color=Colors.ACCENT_PURPLE).grid(row=0, column=2, sticky="nsew", padx=4, pady=4)
        StatCard(kpi_frame, title="Operaciones", value=str(tx_count),
                  icon="📋", accent_color=Colors.ACCENT_ORANGE,
                  subtitle="transacciones registradas").grid(row=0, column=3, sticky="nsew", padx=4, pady=4)

        # Main content: Ranking + Activity
        content = ctk.CTkFrame(scroll, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)

        # Rankings
        self._build_rankings(content, participants)

        # Activity Feed
        self._build_activity(content)

        # Participant cards
        self._build_participant_cards(scroll, participants)

    def _build_rankings(self, parent, participants):
        rank_frame = ctk.CTkFrame(parent, corner_radius=14, fg_color=Colors.BG_CARD,
                                   border_width=1, border_color=Colors.BORDER)
        rank_frame.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.SM), pady=0)

        container = ctk.CTkFrame(rank_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(container, text="🏆 Clasificación", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.MD))

        sorted_p = sorted(participants, key=lambda p: p.valor_total, reverse=True)
        for i, p in enumerate(sorted_p):
            rank = i + 1
            row = ctk.CTkFrame(container, fg_color="transparent", height=44)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            inner = ctk.CTkFrame(row, fg_color=Colors.BG_TERTIARY if rank <= 3 else "transparent",
                                  corner_radius=8)
            inner.pack(fill="both", expand=True)

            left = ctk.CTkFrame(inner, fg_color="transparent")
            left.pack(side="left", fill="y", padx=Spacing.MD)

            medal = get_rank_medal(rank)
            ctk.CTkLabel(left, text=medal, font=("Segoe UI Emoji", 16), width=30).pack(side="left")
            ctk.CTkLabel(left, text=p.name, font=Fonts.BODY,
                          text_color=Colors.TEXT_PRIMARY).pack(side="left", padx=(Spacing.SM, 0))

            right = ctk.CTkFrame(inner, fg_color="transparent")
            right.pack(side="right", fill="y", padx=Spacing.MD)

            ctk.CTkLabel(right, text=format_money(p.valor_total, True),
                          font=Fonts.MONO_SM, text_color=Colors.ACCENT_BLUE).pack(side="right", pady=10)

    def _build_activity(self, parent):
        activity_frame = ctk.CTkFrame(parent, corner_radius=14, fg_color=Colors.BG_CARD,
                                       border_width=1, border_color=Colors.BORDER)
        activity_frame.grid(row=0, column=1, sticky="nsew", padx=(Spacing.SM, 0), pady=0)

        container = ctk.CTkFrame(activity_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(container, text="📋 Actividad Reciente", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.MD))

        recent_txs = self.db.get_transactions(limit=8)
        if not recent_txs:
            ctk.CTkLabel(container, text="Sin actividad registrada", font=Fonts.BODY_SM,
                          text_color=Colors.TEXT_MUTED).pack(pady=Spacing.XL)
            return

        from utils import get_transaction_icon, get_transaction_color, get_transaction_label
        for tx in recent_txs:
            tx_row = ctk.CTkFrame(container, fg_color="transparent", height=36)
            tx_row.pack(fill="x", pady=1)
            tx_row.pack_propagate(False)

            icon = get_transaction_icon(tx.type)
            color = get_transaction_color(tx.type)

            ctk.CTkLabel(tx_row, text=icon, font=("Segoe UI Emoji", 12), width=20).pack(side="left")
            ctk.CTkLabel(tx_row, text=tx.participant, font=Fonts.BODY_XS,
                          text_color=Colors.TEXT_PRIMARY, width=80, anchor="w").pack(side="left", padx=(4, 0))

            desc = tx.player_name if tx.player_name else get_transaction_label(tx.type)
            ctk.CTkLabel(tx_row, text=desc, font=Fonts.BODY_XS,
                          text_color=Colors.TEXT_SECONDARY, anchor="w").pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(tx_row, text=format_money(tx.amount, True), font=Fonts.BODY_XS,
                          text_color=color).pack(side="right")

    def _build_participant_cards(self, parent, participants):
        if not participants:
            return

        ctk.CTkLabel(parent, text="👥 Participantes", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", padx=Spacing.LG, pady=(Spacing.MD, Spacing.SM))

        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

        cols = min(len(participants), 4)
        for i in range(cols):
            cards_frame.grid_columnconfigure(i, weight=1)

        for i, p in enumerate(participants):
            card = ctk.CTkFrame(cards_frame, corner_radius=14, fg_color=Colors.BG_CARD,
                                 border_width=1, border_color=Colors.BORDER)
            card.grid(row=i // cols, column=i % cols, sticky="nsew", padx=4, pady=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

            # Avatar + Name
            avatar = ctk.CTkFrame(inner, width=40, height=40, corner_radius=20, fg_color=p.avatar_color)
            avatar.pack()
            avatar.pack_propagate(False)
            initials = "".join(w[0].upper() for w in p.name.split()[:2])
            ctk.CTkLabel(avatar, text=initials, font=Fonts.BODY_SM,
                          text_color=Colors.TEXT_PRIMARY).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(inner, text=p.name, font=Fonts.TITLE_SM,
                          text_color=Colors.TEXT_PRIMARY).pack(pady=(Spacing.SM, Spacing.XS))

            # Stats
            stats = [
                ("Saldo", format_money(p.saldo, True), get_saldo_color(p.saldo)),
                ("Valor Equipo", format_money(p.valor_equipo, True), Colors.ACCENT_BLUE),
                ("Puja Máxima", format_money(p.max_bid, True), Colors.ACCENT_PURPLE),
                ("Valor Total", format_money(p.valor_total, True), Colors.TEXT_PRIMARY),
            ]
            for label, value, color in stats:
                row = ctk.CTkFrame(inner, fg_color="transparent")
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(row, text=label, font=Fonts.CAPTION,
                              text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=value, font=Fonts.BODY_XS,
                              text_color=color, anchor="e").pack(side="right")

            # Budget health
            health_label, health_color, health_pct = get_budget_health(
                p.saldo, self.db.get_config().initial_budget if self.db.get_config() else 100_000_000)
            health_bar = ctk.CTkProgressBar(inner, height=6, corner_radius=3,
                                              fg_color=Colors.BG_TERTIARY, progress_color=health_color)
            health_bar.pack(fill="x", pady=(Spacing.SM, 2))
            health_bar.set(max(health_pct, 0.02))
            ctk.CTkLabel(inner, text=f"Salud: {health_label}", font=Fonts.CAPTION,
                          text_color=health_color).pack()

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
