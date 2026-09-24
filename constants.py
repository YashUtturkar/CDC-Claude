"""
Shared constants used across the dashboard.

Centralizing these avoids re-declaring the month order, column names,
or palette in multiple files, which is how dashboards quietly drift
out of sync (e.g., one chart sorted alphabetically while another is
chronological).
"""

# Chronological month order (CDC data uses full month names as strings).
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Column names, as constants so a rename in the source CSV only needs
# to be updated here.
COL_STATE = "state_of_residence"
COL_MONTH = "month"
COL_MONTH_CODE = "month_code"
COL_YEAR_CODE = "year_code"
COL_SEX = "sex_of_infant"
COL_BIRTHS = "births"

REQUIRED_COLUMNS = [
    COL_STATE, COL_MONTH, COL_MONTH_CODE, COL_YEAR_CODE, COL_SEX, COL_BIRTHS,
]

VALID_SEXES = {"Female", "Male"}

# Okabe-Ito palette: colorblind-safe, used consistently across charts.
COLOR_FEMALE = "#E69F00"   # orange
COLOR_MALE = "#0072B2"     # blue
COLOR_SEQUENTIAL = "Blues"  # Plotly colorscale name, for the choropleth/heatmap
COLOR_ACCENT = "#009E73"   # bluish green, for single-series highlight charts

DATA_PATH = "data/Provisional_Natality_2025_CDC1.csv"
