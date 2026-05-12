"""
Design tokens, constants and configuration for Gisbert's Fantasy Manager v2.0
"""

# ─── Application Info ───────────────────────────────────────────────
APP_NAME = "Gisbert's Fantasy Manager"
APP_VERSION = "2.0"
APP_AUTHOR = "Gisbert"
WINDOW_MIN_WIDTH = 1280
WINDOW_MIN_HEIGHT = 780
SIDEBAR_WIDTH = 220
SIDEBAR_COLLAPSED_WIDTH = 60

# ─── Colors (Dark Theme) ────────────────────────────────────────────
class Colors:
    # Backgrounds
    BG_PRIMARY = "#0f1117"
    BG_SECONDARY = "#1a1d27"
    BG_TERTIARY = "#252836"
    BG_HOVER = "#2d3143"
    BG_CARD = "#1e2130"

    # Accents
    ACCENT_BLUE = "#3b82f6"
    ACCENT_BLUE_HOVER = "#2563eb"
    ACCENT_GREEN = "#10b981"
    ACCENT_GREEN_HOVER = "#059669"
    ACCENT_RED = "#ef4444"
    ACCENT_RED_HOVER = "#dc2626"
    ACCENT_ORANGE = "#f59e0b"
    ACCENT_ORANGE_HOVER = "#d97706"
    ACCENT_PURPLE = "#8b5cf6"
    ACCENT_PURPLE_HOVER = "#7c3aed"
    ACCENT_CYAN = "#06b6d4"
    ACCENT_TEAL = "#14b8a6"

    # Text
    TEXT_PRIMARY = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    TEXT_DISABLED = "#475569"

    # Rankings
    GOLD = "#fbbf24"
    SILVER = "#9ca3af"
    BRONZE = "#d97706"

    # Borders
    BORDER = "#2d3143"
    BORDER_LIGHT = "#374151"

    # Gradients (for matplotlib)
    GRADIENT_BLUE = ["#3b82f6", "#1d4ed8"]
    GRADIENT_GREEN = ["#10b981", "#047857"]
    GRADIENT_PURPLE = ["#8b5cf6", "#6d28d9"]
    GRADIENT_ORANGE = ["#f59e0b", "#b45309"]

    # Chart colors
    CHART_COLORS = [
        "#3b82f6", "#10b981", "#f59e0b", "#ef4444",
        "#8b5cf6", "#06b6d4", "#ec4899", "#14b8a6",
        "#f97316", "#6366f1", "#84cc16", "#e879f9"
    ]


# ─── Fonts ───────────────────────────────────────────────────────────
class Fonts:
    FAMILY = "Segoe UI"
    FAMILY_MONO = "Cascadia Code"

    # Sizes
    TITLE_XL = (FAMILY, 28, "bold")
    TITLE_LG = (FAMILY, 22, "bold")
    TITLE_MD = (FAMILY, 18, "bold")
    TITLE_SM = (FAMILY, 15, "bold")
    BODY_LG = (FAMILY, 14)
    BODY = (FAMILY, 13)
    BODY_SM = (FAMILY, 12)
    BODY_XS = (FAMILY, 11)
    CAPTION = (FAMILY, 10)
    MONO_LG = (FAMILY_MONO, 20, "bold")
    MONO_MD = (FAMILY_MONO, 16, "bold")
    MONO_SM = (FAMILY_MONO, 13)


# ─── Spacing ─────────────────────────────────────────────────────────
class Spacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    XXXL = 48


# ─── Border Radius ───────────────────────────────────────────────────
class Radius:
    SM = 6
    MD = 10
    LG = 14
    XL = 20
    FULL = 999


# ─── La Liga Fantasy Constants ───────────────────────────────────────
class Fantasy:
    POINTS_TO_MONEY_MULTIPLIER = 100_000  # 1 punto = 100.000€
    MAX_BID_TEAM_PERCENT = 0.20  # 20% del valor del equipo
    CLAUSULA_THRESHOLD = 1_000_000  # Umbral para cláusula
    CLAUSULA_BELOW_THRESHOLD = 1_000_000  # Cláusula fija si <1M
    CLAUSULA_PERCENT = 0.66  # 66% del valor si >1M
    DEFAULT_INITIAL_BUDGET = 100_000_000  # 100M presupuesto inicial

    TRANSACTION_TYPES = {
        "purchase": {"label": "Compra", "icon": "🛒", "color": Colors.ACCENT_GREEN},
        "sale": {"label": "Venta", "icon": "💰", "color": Colors.ACCENT_ORANGE},
        "money": {"label": "Dinero", "icon": "💵", "color": Colors.ACCENT_BLUE},
        "points": {"label": "Puntos", "icon": "⭐", "color": Colors.ACCENT_PURPLE},
        "team_value": {"label": "Valor Equipo", "icon": "📊", "color": Colors.ACCENT_CYAN},
    }

    POSITIONS = ["POR", "DEF", "MED", "DEL"]
    POSITION_LABELS = {
        "POR": "Portero",
        "DEF": "Defensa",
        "MED": "Mediocampista",
        "DEL": "Delantero",
    }


# ─── Navigation Items ───────────────────────────────────────────────
NAV_ITEMS = [
    {"id": "dashboard", "label": "Dashboard", "icon": "📊"},
    {"id": "market", "label": "Mercado", "icon": "🏪"},
    {"id": "players", "label": "Jugadores", "icon": "👤"},
    {"id": "analytics", "label": "Analítica", "icon": "📈"},
    {"id": "jornada", "label": "Jornadas", "icon": "📅"},
    {"id": "clausulazo", "label": "Clausulazo", "icon": "💰"},
    {"id": "history", "label": "Historial", "icon": "📜"},
    {"id": "settings", "label": "Ajustes", "icon": "⚙️"},
]
