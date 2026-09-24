"""
Sidebar filters: state multiselect, month multiselect, sex selector,
Select All, Reset Filters, and an active-filters summary line.

All widget state lives in st.session_state under explicit keys so the
Reset button can restore defaults deterministically.
"""

import pandas as pd
import streamlit as st

from constants import COL_MONTH, COL_SEX, MONTH_ORDER

STATE_KEY = "filter_states"
MONTH_KEY = "filter_months"
SEX_KEY = "filter_sex"

SEX_OPTIONS = ["Both", "Female", "Male"]


def _default_states(all_states: list[str]) -> None:
    st.session_state[STATE_KEY] = list(all_states)


def _default_months() -> None:
    st.session_state[MONTH_KEY] = list(MONTH_ORDER)


def _default_sex() -> None:
    st.session_state[SEX_KEY] = "Both"


def _init_defaults(all_states: list[str]) -> None:
    if STATE_KEY not in st.session_state:
        _default_states(all_states)
    if MONTH_KEY not in st.session_state:
        _default_months()
    if SEX_KEY not in st.session_state:
        _default_sex()


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render the sidebar filter controls and return the filtered dataframe.
    Also renders a one-line summary of the active filters.
    """
    all_states = sorted(df["state_of_residence"].unique())
    _init_defaults(all_states)

    st.sidebar.header("Filters")

    col_a, col_b = st.sidebar.columns(2)
    if col_a.button("Select All", use_container_width=True):
        _default_states(all_states)
        _default_months()
        _default_sex()
    if col_b.button("Reset Filters", use_container_width=True):
        _default_states(all_states)
        _default_months()
        _default_sex()

    st.sidebar.multiselect(
        "State / geography",
        options=all_states,
        key=STATE_KEY,
    )

    st.sidebar.multiselect(
        "Month",
        options=MONTH_ORDER,
        key=MONTH_KEY,
        help="Options are listed in calendar order.",
    )

    st.sidebar.radio(
        "Infant sex",
        options=SEX_OPTIONS,
        key=SEX_KEY,
        horizontal=True,
    )

    selected_states = st.session_state[STATE_KEY]
    selected_months = st.session_state[MONTH_KEY]
    selected_sex = st.session_state[SEX_KEY]

    filtered = df[
        df["state_of_residence"].isin(selected_states)
        & df[COL_MONTH].isin(selected_months)
    ]
    if selected_sex != "Both":
        filtered = filtered[filtered[COL_SEX] == selected_sex]

    n_states = len(selected_states)
    n_months = len(selected_months)
    st.sidebar.caption(
        f"Showing **{n_states}** of {len(all_states)} geographies, "
        f"**{n_months}** of {len(MONTH_ORDER)} months, sex: **{selected_sex}**."
    )

    return filtered
