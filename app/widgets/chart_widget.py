"""
Chart widget for embedding matplotlib charts in CustomTkinter.
"""
import customtkinter as ctk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from config import Colors, Fonts, Spacing


class ChartWidget(ctk.CTkFrame):
    """Reusable matplotlib chart embedded in a CTk card."""

    def __init__(self, parent, title="", chart_type="bar", figsize=(5, 3), **kwargs):
        super().__init__(parent, corner_radius=14, fg_color=Colors.BG_CARD,
                         border_width=1, border_color=Colors.BORDER, **kwargs)
        self.chart_type = chart_type
        self.fig = Figure(figsize=figsize, dpi=100, facecolor=Colors.BG_CARD)
        self.ax = self.fig.add_subplot(111)
        self._style_axes()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

        if title:
            ctk.CTkLabel(container, text=title, font=Fonts.TITLE_SM,
                          text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.SM))

        self.canvas = FigureCanvasTkAgg(self.fig, master=container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _style_axes(self):
        self.ax.set_facecolor(Colors.BG_CARD)
        self.ax.tick_params(colors=Colors.TEXT_MUTED, labelsize=9)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_color(Colors.BORDER)
        self.ax.spines["left"].set_color(Colors.BORDER)
        self.ax.xaxis.label.set_color(Colors.TEXT_SECONDARY)
        self.ax.yaxis.label.set_color(Colors.TEXT_SECONDARY)
        self.ax.title.set_color(Colors.TEXT_PRIMARY)

    def plot_bar(self, labels, values, colors=None, xlabel="", ylabel=""):
        self.ax.clear()
        self._style_axes()
        if not colors:
            colors = [Colors.CHART_COLORS[i % len(Colors.CHART_COLORS)] for i in range(len(labels))]
        bars = self.ax.bar(labels, values, color=colors, edgecolor="none", width=0.6)
        for bar, val in zip(bars, values):
            self.ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                         f"{val:,.0f}", ha="center", va="bottom",
                         fontsize=8, color=Colors.TEXT_SECONDARY)
        if xlabel: self.ax.set_xlabel(xlabel, fontsize=10)
        if ylabel: self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.tick_params(axis='x', rotation=30)
        self.fig.tight_layout()
        self.canvas.draw()

    def plot_line(self, x_data, y_data_dict, xlabel="", ylabel=""):
        """Plot multiple lines. y_data_dict = {label: [values]}"""
        self.ax.clear()
        self._style_axes()
        for i, (label, values) in enumerate(y_data_dict.items()):
            color = Colors.CHART_COLORS[i % len(Colors.CHART_COLORS)]
            self.ax.plot(x_data[:len(values)], values, color=color, linewidth=2,
                         marker="o", markersize=4, label=label)
        self.ax.legend(fontsize=8, facecolor=Colors.BG_TERTIARY, edgecolor=Colors.BORDER,
                        labelcolor=Colors.TEXT_SECONDARY)
        if xlabel: self.ax.set_xlabel(xlabel, fontsize=10)
        if ylabel: self.ax.set_ylabel(ylabel, fontsize=10)
        self.fig.tight_layout()
        self.canvas.draw()

    def plot_donut(self, labels, values, colors=None):
        self.ax.clear()
        if not colors:
            colors = Colors.CHART_COLORS[:len(labels)]
        wedges, texts, autotexts = self.ax.pie(
            values, labels=None, colors=colors, autopct="%1.0f%%",
            startangle=90, pctdistance=0.75,
            textprops={"color": Colors.TEXT_PRIMARY, "fontsize": 9}
        )
        centre_circle = plt.Circle((0, 0), 0.55, fc=Colors.BG_CARD)
        self.ax.add_artist(centre_circle)
        self.ax.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5),
                        fontsize=8, facecolor=Colors.BG_TERTIARY,
                        edgecolor=Colors.BORDER, labelcolor=Colors.TEXT_SECONDARY)
        self.fig.tight_layout()
        self.canvas.draw()

    def plot_horizontal_bar(self, labels, values, colors=None, xlabel=""):
        self.ax.clear()
        self._style_axes()
        if not colors:
            colors = [Colors.CHART_COLORS[i % len(Colors.CHART_COLORS)] for i in range(len(labels))]
        bars = self.ax.barh(labels, values, color=colors, edgecolor="none", height=0.5)
        for bar, val in zip(bars, values):
            self.ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                         f" {val:,.0f}", ha="left", va="center",
                         fontsize=8, color=Colors.TEXT_SECONDARY)
        if xlabel: self.ax.set_xlabel(xlabel, fontsize=10)
        self.fig.tight_layout()
        self.canvas.draw()

    def clear_chart(self):
        self.ax.clear()
        self._style_axes()
        self.canvas.draw()
