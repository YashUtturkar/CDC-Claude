"""
CDC Provisional Natality 2025 Dashboard
Entry point: page config, header, sidebar wiring, KPI cards, and tabs.

Run locally with:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from charts import (
    fig_choropleth,
    fig_monthly_trend,
    fig_sex_comparison,
    fig_state_month_heatmap,
    fig_state_ranking,
    fig_top_bottom,
)
from data_loader import DataValidationError, load_data
from filters import render_sidebar
from metrics import compute_kpis

st.set_page_config(
    page_title="CDC Provisional Natality 2025",
    page_icon="👶",
    layout="wide",
)


def render_header() -> None:
    st.title("CDC Provisional Natality Dashboard, 2025")
    st.caption(
        "Explore 2025 U.S. birth counts by state, month, and infant sex."
    )
    st.info(
        "**Provisional data.** Figures are preliminary CDC estimates for "
        "2025 and are subject to revision as more complete records are "
        "processed. **These are birth counts, not birth rates** — they "
        "are not adjusted for population size, so larger states will "
        "naturally show higher counts regardless of any underlying trend."
    )
    st.caption("Source: CDC WONDER, Provisional Natality data.")


def render_kpis(filtered: pd.DataFrame) -> None:
    kpis = compute_kpis(filtered)
    cols = st.columns(5)

    if kpis["total_births"] is None:
        for c in cols:
            c.metric("—", "No data")
        return

    cols[0].metric("Total Births", f"{kpis['total_births']:,}")
    cols[1].metric("Geographies Selected", f"{kpis['n_geographies']:,}")
    cols[2].metric("Avg. Births / Month", f"{kpis['avg_births_per_month']:,.0f}")
    cols[3].metric("Top Geography", kpis["top_geography"])
    cols[4].metric("Top Month", kpis["top_month"])


def render_empty_state() -> None:
    st.warning(
        "No observations match the current filters. Try selecting more "
        "states, months, or a different infant-sex filter — or use "
        "**Reset Filters** in the sidebar."
    )


def render_overview_tab(filtered: pd.DataFrame) -> None:
    st.plotly_chart(fig_monthly_trend(filtered), use_container_width=True)
    st.subheader("Filtered Data Summary")
    summary = (
        filtered.groupby("state_of_residence")["births"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"state_of_residence": "State", "births": "Total Births"})
    )
    st.dataframe(
        summary.style.format({"Total Births": "{:,}"}),
        use_container_width=True,
        hide_index=True,
    )


def render_geographic_tab(filtered: pd.DataFrame) -> None:
    st.plotly_chart(fig_state_ranking(filtered), use_container_width=True)
    st.plotly_chart(fig_choropleth(filtered), use_container_width=True)
    st.plotly_chart(fig_top_bottom(filtered), use_container_width=True)


def render_monthly_sex_tab(filtered: pd.DataFrame) -> None:
    st.plotly_chart(fig_sex_comparison(filtered), use_container_width=True)
    st.plotly_chart(fig_state_month_heatmap(filtered), use_container_width=True)


def render_data_tab(filtered: pd.DataFrame) -> None:
    st.subheader("Filtered Records")
    search = st.text_input("Search by state name")
    display_df = filtered.copy()
    if search:
        display_df = display_df[
            display_df["state_of_residence"].str.contains(search, case=False, na=False)
        ]
    st.dataframe(
        display_df.rename(
            columns={
                "state_of_residence": "State",
                "month": "Month",
                "sex_of_infant": "Sex",
                "births": "Births",
            }
        )[["State", "Month", "Sex", "Births"]],
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download filtered data as CSV",
        data=display_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_natality_2025.csv",
        mime="text/csv",
    )


def render_about_tab() -> None:
    st.subheader("About This Data")
    st.markdown(
        """
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
    )


def main() -> None:
    render_header()

    try:
        df = load_data()
    except (DataValidationError, FileNotFoundError) as e:
        st.error(f"Could not load the dataset: {e}")
        st.stop()

    filtered = render_sidebar(df)

    render_kpis(filtered)
    st.divider()

    if filtered.empty:
        render_empty_state()
        return

    tab_overview, tab_geo, tab_monthly_sex, tab_data, tab_about = st.tabs(
        [
            "Overview",
            "Geographic Analysis",
            "Monthly and Sex Analysis",
            "Data Table and Download",
            "About the Data",
        ]
    )

    with tab_overview:
        render_overview_tab(filtered)
    with tab_geo:
        render_geographic_tab(filtered)
    with tab_monthly_sex:
        render_monthly_sex_tab(filtered)
    with tab_data:
        render_data_tab(filtered)
    with tab_about:
        render_about_tab()


if __name__ == "__main__":
    main()
