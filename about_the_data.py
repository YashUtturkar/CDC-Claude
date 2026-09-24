"""
Content for the "About the Data" tab.

Pulled into its own module because it's static reference text rather
than logic — keeping it out of app.py means updating the data caveats
or source attribution never requires touching layout code, and vice
versa.
"""

import streamlit as st

ABOUT_MARKDOWN = """
- **Source:** CDC WONDER, Provisional Natality data, 2025.
- **Provisional status:** These figures are preliminary and will be
  revised as additional birth records are finalized.
- **Counts, not rates:** Every number in this dashboard is a raw birth
  count. It is **not** normalized by population, so cross-state
  comparisons reflect population size as much as any underlying trend.
  Use birth *rates* (births per 1,000 population) for population-adjusted
  comparisons — not included in this dataset.
- **Geography:** 50 states plus the District of Columbia.
- **Columns:**
    - `state_of_residence` — state of the mother's residence
    - `month` — birth month
    - `sex_of_infant` — Female / Male
    - `births` — count of births for that state, month, and sex
"""


def render_about_tab() -> None:
    """Render the static 'About the Data' tab content."""
    st.subheader("About This Data")
    st.markdown(ABOUT_MARKDOWN)
