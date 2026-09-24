"""KPI calculations for the header metric cards."""

import pandas as pd

from constants import COL_BIRTHS, COL_MONTH


def compute_kpis(filtered_df: pd.DataFrame) -> dict:
    """
    Compute the five headline KPIs from an already-filtered dataframe.
    Returns a dict of plain Python values (str/int) ready for st.metric,
    or None values when the selection is empty.
    """
    if filtered_df.empty:
        return {
            "total_births": None,
            "n_geographies": 0,
            "avg_births_per_month": None,
            "top_geography": None,
            "top_month": None,
        }

    total_births = int(filtered_df[COL_BIRTHS].sum())
    n_geographies = filtered_df["state_of_residence"].nunique()

    by_month = filtered_df.groupby(COL_MONTH, observed=True)[COL_BIRTHS].sum()
    avg_births_per_month = by_month.mean()

    by_state = filtered_df.groupby("state_of_residence")[COL_BIRTHS].sum()
    top_geography = by_state.idxmax()

    top_month = by_month.idxmax()

    return {
        "total_births": total_births,
        "n_geographies": n_geographies,
        "avg_births_per_month": avg_births_per_month,
        "top_geography": top_geography,
        "top_month": str(top_month),
    }
