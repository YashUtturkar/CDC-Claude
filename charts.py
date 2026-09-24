"""
One function per chart. Each takes an already-filtered dataframe and
returns a Plotly figure, ready for st.plotly_chart(). Keeping these as
pure functions (no Streamlit calls inside) makes them independently
testable and keeps app.py focused on layout, not chart internals.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from constants import (
    COL_BIRTHS,
    COL_MONTH,
    COL_SEX,
    COLOR_ACCENT,
    COLOR_FEMALE,
    COLOR_MALE,
    COLOR_SEQUENTIAL,
    MONTH_ORDER,
)
from state_mapping import state_to_abbrev

SEX_COLOR_MAP = {"Female": COLOR_FEMALE, "Male": COLOR_MALE}


def fig_monthly_trend(df: pd.DataFrame) -> go.Figure:
    """Total births by month, summed across the current selection."""
    monthly = (
        df.groupby(COL_MONTH, observed=True)[COL_BIRTHS]
        .sum()
        .reindex(MONTH_ORDER)
        .dropna()
        .reset_index()
    )
    fig = px.line(
        monthly,
        x=COL_MONTH,
        y=COL_BIRTHS,
        markers=True,
        title="Monthly Birth Trend",
        color_discrete_sequence=[COLOR_ACCENT],
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Births",
        yaxis_tickformat=",",
        hovermode="x unified",
    )
    fig.update_yaxes(rangemode="tozero")
    return fig


def fig_sex_comparison(df: pd.DataFrame) -> go.Figure:
    """Grouped bar: female vs. male births by month."""
    grouped = (
        df.groupby([COL_MONTH, COL_SEX], observed=True)[COL_BIRTHS]
        .sum()
        .reset_index()
    )
    fig = px.bar(
        grouped,
        x=COL_MONTH,
        y=COL_BIRTHS,
        color=COL_SEX,
        barmode="group",
        category_orders={COL_MONTH: MONTH_ORDER},
        color_discrete_map=SEX_COLOR_MAP,
        title="Female vs. Male Births by Month",
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Births", yaxis_tickformat=",")
    fig.update_yaxes(rangemode="tozero")
    return fig


def fig_state_ranking(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Horizontal bar of the top N geographies by total births."""
    by_state = (
        df.groupby("state_of_residence")[COL_BIRTHS]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    fig = px.bar(
        by_state.sort_values(COL_BIRTHS),
        x=COL_BIRTHS,
        y="state_of_residence",
        orientation="h",
        title=f"Top {min(top_n, len(by_state))} Geographies by Total Births",
        color_discrete_sequence=[COLOR_ACCENT],
    )
    fig.update_layout(xaxis_title="Births", yaxis_title="", xaxis_tickformat=",")
    fig.update_xaxes(rangemode="tozero")
    return fig


def fig_top_bottom(df: pd.DataFrame, n: int = 5) -> go.Figure:
    """Side-by-side comparison of the top N and bottom N geographies."""
    by_state = df.groupby("state_of_residence")[COL_BIRTHS].sum().sort_values(ascending=False)
    top = by_state.head(n)
    bottom = by_state.tail(n)
    combined = pd.concat([top, bottom]).reset_index()
    combined.columns = ["state_of_residence", COL_BIRTHS]
    combined["group"] = ["Top"] * len(top) + ["Bottom"] * len(bottom)

    fig = px.bar(
        combined.sort_values(COL_BIRTHS),
        x=COL_BIRTHS,
        y="state_of_residence",
        color="group",
        orientation="h",
        title=f"Top {n} vs. Bottom {n} Geographies",
        color_discrete_map={"Top": COLOR_MALE, "Bottom": COLOR_FEMALE},
    )
    fig.update_layout(xaxis_title="Births", yaxis_title="", xaxis_tickformat=",")
    fig.update_xaxes(rangemode="tozero")
    return fig


def fig_choropleth(df: pd.DataFrame) -> go.Figure:
    """US state choropleth of total births in the current selection."""
    by_state = df.groupby("state_of_residence")[COL_BIRTHS].sum().reset_index()
    by_state["abbrev"] = by_state["state_of_residence"].map(state_to_abbrev)
    unmapped = by_state[by_state["abbrev"].isna()]
    by_state = by_state.dropna(subset=["abbrev"])

    fig = px.choropleth(
        by_state,
        locations="abbrev",
        locationmode="USA-states",
        color=COL_BIRTHS,
        scope="usa",
        color_continuous_scale=COLOR_SEQUENTIAL,
        hover_name="state_of_residence",
        hover_data={"abbrev": False, COL_BIRTHS: ":,"},
        title="Total Births by State",
    )
    fig.update_layout(coloraxis_colorbar_title="Births")

    if not unmapped.empty:
        # DC and territories don't render on a state choropleth; surfaced
        # to the caller via the figure's metadata rather than silently
        # dropped, so app.py can note it beneath the chart.
        fig.update_layout(
            annotations=[
                dict(
                    text=f"Note: {', '.join(unmapped['state_of_residence'])} not shown (no state polygon).",
                    showarrow=False, x=0.5, y=-0.08, xref="paper", yref="paper",
                    font=dict(size=11, color="gray"),
                )
            ]
        )
    return fig


def fig_state_month_heatmap(df: pd.DataFrame) -> go.Figure:
    """State x month heatmap of total births."""
    pivot = (
        df.groupby(["state_of_residence", COL_MONTH], observed=True)[COL_BIRTHS]
        .sum()
        .reset_index()
        .pivot(index="state_of_residence", columns=COL_MONTH, values=COL_BIRTHS)
        .reindex(columns=MONTH_ORDER)
    )
    # Order states by total births so the heatmap reads top-to-bottom
    # from highest to lowest volume rather than alphabetically.
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]

    fig = px.imshow(
        pivot,
        color_continuous_scale=COLOR_SEQUENTIAL,
        aspect="auto",
        title="State-by-Month Birth Heatmap",
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="State",
        coloraxis_colorbar_title="Births",
        height=max(400, 18 * len(pivot)),
    )
    return fig
