"""
Jornada tracker view for recording matchday points.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing, Fantasy
from widgets.chart_widget import ChartWidget
from widgets.stat_card import StatCard
from models import JornadaRecord
from utils import format_money


class JornadaView(ctk.CTkFrame):
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

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.MD))
        ctk.CTkLabel(header, text="📅 Registro de Jornadas", font=Fonts.TITLE_LG,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")

        config = self.db.get_config()
        current_j = config.current_jornada if config else 0

        # New jornada form
        form_card = ctk.CTkFrame(scroll, corner_radius=14, fg_color=Colors.BG_CARD,
                                  border_width=1, border_color=Colors.BORDER)
        form_card.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        form_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(form_inner, text=f"⭐ Registrar Jornada {current_j + 1}",
                      font=Fonts.TITLE_SM, text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.MD))

        participants = self.db.get_participants()
        self.jornada_entries = {}

        points_grid = ctk.CTkFrame(form_inner, fg_color="transparent")
        points_grid.pack(fill="x")

        cols = min(len(participants), 4) if participants else 1
        for i in range(cols):
            points_grid.grid_columnconfigure(i, weight=1)

        for i, p in enumerate(participants):
            cell = ctk.CTkFrame(points_grid, fg_color="transparent")
            cell.grid(row=i // cols, column=i % cols, sticky="nsew", padx=4, pady=4)

            ctk.CTkLabel(cell, text=p.name, font=Fonts.BODY_SM,
                          text_color=Colors.TEXT_PRIMARY).pack(anchor="w")
            entry = ctk.CTkEntry(cell, placeholder_text="Puntos", font=Fonts.BODY, height=36,
                                  corner_radius=8, fg_color=Colors.BG_TERTIARY,
                                  border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY, border_width=1)
            entry.pack(fill="x", pady=(2, 0))
            self.jornada_entries[p.name] = entry

        ctk.CTkButton(form_inner, text=f"✓ Registrar Jornada {current_j + 1}",
                       font=Fonts.BODY, height=40, corner_radius=10,
                       fg_color=Colors.ACCENT_PURPLE, hover_color=Colors.ACCENT_PURPLE_HOVER,
                       command=lambda: self._register_jornada(current_j + 1)).pack(fill="x", pady=(Spacing.MD, 0))

        # Jornada history chart
        all_jornadas = self.db.get_jornadas()
        if all_jornadas:
            self._build_charts(scroll, participants, all_jornadas)
            self._build_jornada_history(scroll, all_jornadas, participants)

    def _build_charts(self, parent, participants, jornadas):
        charts_row = ctk.CTkFrame(parent, fg_color="transparent")
        charts_row.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        charts_row.grid_columnconfigure((0, 1), weight=1)

        # Points per jornada (line chart)
        line_chart = ChartWidget(charts_row, title="📈 Puntos Acumulados por Jornada", figsize=(5, 3))
        line_chart.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.XS), pady=Spacing.XS)

        # Build cumulative data
        max_j = max(j.jornada for j in jornadas)
        x_data = list(range(1, max_j + 1))
        y_data = {}
        for p in participants:
            p_jornadas = sorted([j for j in jornadas if j.participant == p.name], key=lambda j: j.jornada)
            cumulative = []
            total = 0
            j_dict = {j.jornada: j.points for j in p_jornadas}
            for jn in range(1, max_j + 1):
                total += j_dict.get(jn, 0)
                cumulative.append(total)
            y_data[p.name] = cumulative

        line_chart.plot_line(x_data, y_data, xlabel="Jornada", ylabel="Puntos Acumulados")

        # Per-jornada winner
        bar_chart = ChartWidget(charts_row, title="🏆 Puntos por Última Jornada", figsize=(5, 3))
        bar_chart.grid(row=0, column=1, sticky="nsew", padx=(Spacing.XS, 0), pady=Spacing.XS)

        last_j = max_j
        last_records = [j for j in jornadas if j.jornada == last_j]
        if last_records:
            names = [j.participant for j in last_records]
            points = [j.points for j in last_records]
            bar_chart.plot_bar(names, points, ylabel="Puntos")

    def _build_jornada_history(self, parent, jornadas, participants):
        history_card = ctk.CTkFrame(parent, corner_radius=14, fg_color=Colors.BG_CARD,
                                     border_width=1, border_color=Colors.BORDER)
        history_card.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

        inner = ctk.CTkFrame(history_card, fg_color="transparent")
        inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(inner, text="📋 Historial de Jornadas", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.MD))

        max_j = max(j.jornada for j in jornadas)
        for jn in range(max_j, 0, -1):
            records = sorted([j for j in jornadas if j.jornada == jn],
                              key=lambda j: j.points, reverse=True)
            if not records:
                continue

            j_frame = ctk.CTkFrame(inner, fg_color=Colors.BG_TERTIARY, corner_radius=8)
            j_frame.pack(fill="x", pady=2)

            j_inner = ctk.CTkFrame(j_frame, fg_color="transparent")
            j_inner.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)

            ctk.CTkLabel(j_inner, text=f"Jornada {jn}", font=Fonts.BODY_SM,
                          text_color=Colors.ACCENT_BLUE).pack(side="left")

            winner = records[0]
            ctk.CTkLabel(j_inner, text=f"🏆 {winner.participant}: {winner.points} pts",
                          font=Fonts.BODY_SM, text_color=Colors.GOLD).pack(side="right")

    def _register_jornada(self, jornada_num):
        from models import Transaction
        from datetime import datetime

        any_registered = False
        for name, entry in self.jornada_entries.items():
            try:
                points = int(entry.get())
            except (ValueError, TypeError):
                continue

            if points == 0:
                continue

            money = points * Fantasy.POINTS_TO_MONEY_MULTIPLIER
            record = JornadaRecord(participant=name, jornada=jornada_num,
                                    points=points, money_earned=money)
            self.db.add_jornada(record)

            # Update saldo
            participant = self.db.get_participant(name)
            if participant:
                prev_saldo = participant.saldo
                new_saldo = prev_saldo + money
                self.db.update_participant_saldo(name, new_saldo)
                self.db.update_participant_points(name, participant.total_points + points)

                tx = Transaction(participant=name, type="points", amount=money,
                                  saldo_before=prev_saldo, saldo_after=new_saldo,
                                  jornada=jornada_num,
                                  notes=f"Jornada {jornada_num}: {points} puntos")
                self.db.add_transaction(tx)
            any_registered = True

        if any_registered:
            # Update current jornada
            config = self.db.get_config()
            if config:
                config.current_jornada = jornada_num
                self.db.save_config(config)

            from tkinter import messagebox
            messagebox.showinfo("Jornada Registrada", f"Jornada {jornada_num} registrada correctamente")
            if self.on_refresh:
                self.on_refresh()

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
