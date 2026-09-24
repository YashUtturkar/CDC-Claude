# CDC Provisional Natality 2025 Dashboard

A Streamlit dashboard for exploring 2025 U.S. birth counts by state,
month, and infant sex, built for an undergraduate business analytics
audience.

## Quick start

```bash
# from inside natality_dashboard/
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. No configuration or API keys
are required — the dataset ships in `data/`.

## Data

- **Source:** CDC WONDER, Provisional Natality data, 2025.
- **File:** `data/Provisional_Natality_2025_CDC1.csv`
- **Shape:** 1,224 rows — 51 geographies (50 states + DC) × 12 months × 2 sexes.
- **Columns:** `state_of_residence`, `month`, `month_code`, `year_code`,
  `sex_of_infant`, `births`.
- These are **birth counts, not birth rates** — not adjusted for
  population, and the CDC labels them **provisional** (subject to
  revision). Both facts are surfaced in the app header and the "About
  the Data" tab.

To swap in an updated CDC export, replace the CSV in `data/` and keep
the same filename and column names, or update `DATA_PATH` in
`constants.py`. `data_loader.py` will validate the new file on load
and raise a specific error if a column is missing, `births` is
negative or non-numeric, or an unrecognized month/sex value appears.

## Project structure

```
natality_dashboard/
├── app.py                # Entry point: page config, layout, tabs
├── data_loader.py         # Cached load + validation + month ordering
├── filters.py              # Sidebar filters (state/month/sex, select all, reset)
├── metrics.py               # KPI calculations
├── charts.py                 # Plotly figure builders (one function per chart)
├── state_mapping.py           # State name -> USPS abbreviation (for the map)
├── constants.py                 # Month order, column names, color palette
├── requirements.txt
├── .streamlit/config.toml         # Theme (accessible, colorblind-safe palette)
└── data/
    └── Provisional_Natality_2025_CDC1.csv
```

Each module owns one responsibility — e.g., every chart is a pure
function in `charts.py` that takes a filtered DataFrame and returns a
Plotly figure, with no Streamlit calls inside, so charts can be
inspected or tested independently of the running app.

## Dashboard layout

- **Header** — title, description, CDC source attribution, provisional-data
  notice, counts-vs-rates clarification.
- **Sidebar filters** — state multiselect, month multiselect (calendar
  order), infant-sex selector, Select All, Reset Filters, and an active-filter
  summary.
- **KPI cards** — total births, geographies selected, average births per
  month, top geography, top month, all reflecting the current filter selection.
- **Tabs:**
  - *Overview* — monthly trend chart + per-state summary table.
  - *Geographic Analysis* — state ranking bar chart, US choropleth, top vs.
    bottom geography comparison.
  - *Monthly and Sex Analysis* — female/male comparison chart, state-by-month
    heatmap.
  - *Data Table and Download* — searchable filtered table with CSV download.
  - *About the Data* — source, provisional-data caveat, and column definitions.

## Notes on implementation choices

- **Caching:** `load_data()` in `data_loader.py` is wrapped in
  `st.cache_data` so the CSV is parsed once per session rather than on
  every widget interaction (Streamlit reruns the whole script on each
  rerun).
- **State mapping:** `state_mapping.py` uses a static dict rather than a
  geocoding library — CDC state names are clean and consistent, so a
  lookup table is both sufficient and has no external dependency risk on
  Streamlit Community Cloud.
- **Paths:** the data path is resolved relative to `data_loader.py`'s own
  location (`Path(__file__).parent / ...`), so the app finds the CSV the
  same way locally and when deployed.
- **Month ordering:** `month` is loaded as an ordered pandas categorical
  (`constants.MONTH_ORDER`), so every chart and groupby stays chronological
  without re-specifying the order.

## Deploying to Streamlit Community Cloud

1. Push this folder (including `data/` and `.streamlit/config.toml`) to a
   GitHub repo.
2. On [share.streamlit.io](https://share.streamlit.io), point a new app at
   `app.py` in that repo.
3. No secrets or environment variables are needed — the CSV is bundled and
   read via a relative path.

## Known limitations

- The choropleth only renders the 50 states (Plotly's `USA-states`
  locationmode has no polygon for DC); DC's total is noted below the map
  rather than silently dropped.
- The dataset covers a single year (2025) only, so there's no year-over-year
  comparison in this version.
