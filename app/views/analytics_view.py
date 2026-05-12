"""
Analytics view with charts and deep statistics.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing
from widgets.chart_widget import ChartWidget
from widgets.stat_card import StatCard
from utils import format_money, format_percent


class AnalyticsView(ctk.CTkFrame):
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
        ctk.CTkLabel(header, text="📈 Centro de Analítica", font=Fonts.TITLE_LG,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")

        participants = self.db.get_participants()
        if not participants:
            ctk.CTkLabel(scroll, text="Carga una liga para ver analíticas",
                          font=Fonts.BODY, text_color=Colors.TEXT_MUTED).pack(pady=Spacing.XXL)
            return

        # Row 1: Saldo + Valor charts
        row1 = ctk.CTkFrame(scroll, fg_color="transparent")
        row1.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        row1.grid_columnconfigure((0, 1), weight=1)

        # Saldo chart
        saldo_chart = ChartWidget(row1, title="💰 Saldos por Participante", figsize=(5, 3))
        saldo_chart.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.XS), pady=Spacing.XS)
        names = [p.name for p in participants]
        saldos = [p.saldo for p in participants]
        saldo_colors = [Colors.ACCENT_GREEN if s >= 0 else Colors.ACCENT_RED for s in saldos]
        saldo_chart.plot_bar(names, saldos, colors=saldo_colors, ylabel="Saldo (€)")

        # Valor equipo chart
        valor_chart = ChartWidget(row1, title="🏟️ Valor de Equipos", figsize=(5, 3))
        valor_chart.grid(row=0, column=1, sticky="nsew", padx=(Spacing.XS, 0), pady=Spacing.XS)
        valores = [p.valor_equipo for p in participants]
        valor_chart.plot_bar(names, valores, ylabel="Valor (€)")

        # Row 2: Overbid + Distribution
        row2 = ctk.CTkFrame(scroll, fg_color="transparent")
        row2.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        row2.grid_columnconfigure((0, 1), weight=1)

        # Overbid analysis
        overbid_chart = ChartWidget(row2, title="📊 Sobrepuja Promedio (%)", figsize=(5, 3))
        overbid_chart.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.XS), pady=Spacing.XS)
        overbids = []
        for p in participants:
            obs = self.db.get_purchase_overbids(p.name)
            avg = sum(obs) / len(obs) if obs else 0
            overbids.append(avg)
        ob_colors = [Colors.ACCENT_RED if o > 50 else Colors.ACCENT_ORANGE if o > 20
                     else Colors.ACCENT_GREEN for o in overbids]
        overbid_chart.plot_bar(names, overbids, colors=ob_colors, ylabel="Sobrepuja (%)")

        # Spending distribution (donut)
        spending_chart = ChartWidget(row2, title="🍩 Distribución de Gasto", figsize=(5, 3))
        spending_chart.grid(row=0, column=1, sticky="nsew", padx=(Spacing.XS, 0), pady=Spacing.XS)
        spending = []
        for p in participants:
            stats = self.db.get_participant_stats(p.name)
            spending.append(max(stats["total_spent"], 0))
        if any(s > 0 for s in spending):
            spending_chart.plot_donut(names, [max(s, 0.01) for s in spending])
        else:
            spending_chart.plot_bar(names, spending, ylabel="Gasto (€)")

        # Row 3: Ranking table (max bid)
        row3 = ctk.CTkFrame(scroll, fg_color="transparent")
        row3.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        row3.grid_columnconfigure((0, 1), weight=1)

        # Max bid chart
        bid_chart = ChartWidget(row3, title="🎯 Puja Máxima Disponible", figsize=(5, 3))
        bid_chart.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.XS), pady=Spacing.XS)
        max_bids = [p.max_bid for p in participants]
        bid_chart.plot_horizontal_bar(names, max_bids, xlabel="Puja Máxima (€)")

        # Valor Total ranking
        total_chart = ChartWidget(row3, title="🏆 Valor Total (Saldo + Equipo)", figsize=(5, 3))
        total_chart.grid(row=0, column=1, sticky="nsew", padx=(Spacing.XS, 0), pady=Spacing.XS)
        totals = [p.valor_total for p in participants]
        sorted_pairs = sorted(zip(names, totals), key=lambda x: x[1])
        total_chart.plot_horizontal_bar([x[0] for x in sorted_pairs],
                                          [x[1] for x in sorted_pairs], xlabel="Valor Total (€)")

        # Stats cards row
        stats_row = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_row.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))
        stats_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        total_moved = self.db.get_total_money_moved()
        total_txs = self.db.get_total_transactions_count()
        avg_overbid = sum(overbids) / len(overbids) if overbids else 0
        best_p = max(participants, key=lambda p: p.valor_total)

        StatCard(stats_row, title="Dinero Movido Total", value=format_money(total_moved, True),
                  icon="💸", accent_color=Colors.ACCENT_BLUE).grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        StatCard(stats_row, title="Operaciones Totales", value=str(total_txs),
                  icon="📝", accent_color=Colors.ACCENT_ORANGE).grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        StatCard(stats_row, title="Sobrepuja Media Liga", value=format_percent(avg_overbid),
                  icon="📊", accent_color=Colors.ACCENT_PURPLE).grid(row=0, column=2, sticky="nsew", padx=4, pady=4)
        StatCard(stats_row, title="Líder de Liga", value=best_p.name,
                  icon="🏆", accent_color=Colors.GOLD,
                  subtitle=format_money(best_p.valor_total, True)).grid(row=0, column=3, sticky="nsew", padx=4, pady=4)

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
