"""
Data loading and validation.

`load_data` is the single entry point every other module relies on.
It is decorated with st.cache_data so the CSV is parsed once per
session rather than on every rerun (Streamlit reruns the whole script
on each widget interaction).
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from constants import (
    COL_MONTH,
    COL_MONTH_CODE,
    COL_SEX,
    COL_BIRTHS,
    DATA_PATH,
    MONTH_ORDER,
    REQUIRED_COLUMNS,
    VALID_SEXES,
)


class DataValidationError(Exception):
    """Raised when the source CSV fails a structural sanity check."""


def _resolve_path() -> Path:
    """
    Resolve the data path relative to this file's location, so the app
    finds the CSV whether it's launched from the repo root locally or
    deployed on Streamlit Community Cloud (which sets the working
    directory to the app's own folder either way, but relative-to-file
    resolution is the more robust of the two options).
    """
    return Path(__file__).parent / DATA_PATH


def _validate(df: pd.DataFrame) -> None:
    """Raise DataValidationError with a specific message on any failure."""
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise DataValidationError(f"Missing expected column(s): {missing_cols}")

    if df[COL_BIRTHS].isna().any():
        raise DataValidationError("`births` contains missing values.")

    if not pd.api.types.is_numeric_dtype(df[COL_BIRTHS]):
        raise DataValidationError("`births` is not numeric.")

    if (df[COL_BIRTHS] < 0).any():
        raise DataValidationError("`births` contains negative values.")

    bad_sexes = set(df[COL_SEX].unique()) - VALID_SEXES
    if bad_sexes:
        raise DataValidationError(f"Unexpected sex_of_infant value(s): {bad_sexes}")

    bad_months = set(df[COL_MONTH].unique()) - set(MONTH_ORDER)
    if bad_months:
        raise DataValidationError(f"Unrecognized month value(s): {bad_months}")

    dup_key = ["state_of_residence", COL_MONTH, COL_SEX]
    dupes = df.duplicated(subset=dup_key).sum()
    if dupes:
        raise DataValidationError(
            f"{dupes} duplicate (state, month, sex) row(s) found."
        )


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load, validate, and lightly enrich the natality CSV.

    Adds an ordered categorical `month` column so every downstream
    `sort_values("month")` stays chronological without each caller
    re-specifying the order.
    """
    path = _resolve_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find the data file at {path}. Make sure the CSV "
            f"lives in the `data/` folder next to app.py."
        )

    df = pd.read_csv(path)
    _validate(df)

    df[COL_MONTH] = pd.Categorical(df[COL_MONTH], categories=MONTH_ORDER, ordered=True)
    df = df.sort_values([COL_MONTH_CODE, "state_of_residence", COL_SEX]).reset_index(drop=True)

    return df
