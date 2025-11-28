import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go


def render_variant_waves():

    DATA_PATH = Path("data/merged_covid_dataset_FINAL_with_population.csv")
    COUNTRIES = ["Chile", "Ireland", "Mexico"]

    COLOR_MAP = {
        "Chile": "#2F6FED",
        "Ireland": "#FF8C42",
        "Mexico": "#2E8B57",
    }

    VARIANT_COLORS = {
        "Pre-Alpha": "#BDBDBD",
        "Alpha": "#90CAF9",
        "Delta": "#FFCC80",
        "Omicron": "#CE93D8",
        "Post-Omicron": "#A5D6A7",
    }

    VARIANT_TRANSITIONS = {
        "Pre-Alpha_end": "2020-12-31",
        "Alpha_end": "2021-06-30",
        "Delta_end": "2021-11-30",
        "Omicron_end": "2022-06-30",
    }

    # =======================
    # LOAD DATA
    # =======================
    @st.cache_data
    def load_data():
        if not DATA_PATH.exists():
            st.error(f"Dataset not found at: {DATA_PATH}")
            return pd.DataFrame()

        df = pd.read_csv(DATA_PATH)

        df["Date_reported"] = pd.to_datetime(
            df["Date_reported"], errors="coerce")
        df = df[df["Country"].isin(COUNTRIES)].copy()

        df = df[(df["Date_reported"] >= "2020-01-01") &
                (df["Date_reported"] <= "2022-12-31")]

        for col in ["cases_per_million", "deaths_per_million", "CFR_roll7_clean"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.sort_values(["Country", "Date_reported"], inplace=True)
        return df

    # =======================
    # STYLE
    # =======================
    def inject_style():
        st.markdown("""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

        html, body, [class^="css"] {
            font-family: Inter, sans-serif !important;
            font-size: 18px !important;
        }

        h1 {
            font-family: Montserrat, sans-serif !important;
            font-size: 36px !important;
            font-weight: 700 !important;
            margin-bottom: 0.5rem !important;
        }

        h2 {
            font-family: Montserrat, sans-serif !important;
            font-size: 28px !important;
            font-weight: 600 !important;
            margin-top: 1rem !important;
            margin-bottom: 0.3rem !important;
        }

        h3 {
            font-family: Montserrat, sans-serif !important;
            font-size: 22px !important;
            font-weight: 600 !important;
            margin-bottom: 0.2rem !important;
        }

        .small-text {
            font-size: 14px !important;
            color: #666 !important;
        }

        .variant-tag {
            background-color: #F1F4F9;
            padding: 0.4rem 0.8rem;
            border-radius: 0.6rem;
            font-size: 14px;
            display: inline-block;
            margin-right: 0.4rem;
            border: 1px solid #E0E0E0;
        }

        .block-container {
            max-width: 94 percent !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        </style>
        """, unsafe_allow_html=True)

    # =======================
    # PLOTS
    # =======================
    def add_variant_lines(fig):
        for name, date_str in VARIANT_TRANSITIONS.items():
            date = pd.to_datetime(date_str)
            fig.add_vline(
                x=date,
                line_width=1.1,
                line_dash="dot",
                line_color="#9E9E9E"
            )
        return fig

    def plot_cases_variant(df):
        fig = px.line(
            df,
            x="Date_reported",
            y="cases_per_million",
            color="Country",
            color_discrete_map=COLOR_MAP,
        )

        fig.update_layout(
            title="Transmission intensity segmented by variant transitions",
            xaxis_title="Date",
            yaxis_title="Cases per million (rolling)",
            height=380,
            margin=dict(l=10, r=10, t=50, b=10)
        )

        return add_variant_lines(fig)

    def plot_deaths_variant(df):
        fig = px.line(
            df,
            x="Date_reported",
            y="deaths_per_million",
            color="Country",
            color_discrete_map=COLOR_MAP,
        )

        fig.update_layout(
            title="Mortality pressure under different variant eras",
            xaxis_title="Date",
            yaxis_title="Deaths per million (rolling)",
            height=380,
            margin=dict(l=10, r=10, t=50, b=10)
        )

        return add_variant_lines(fig)

    def plot_cfr_box(df):
        fig = px.box(
            df,
            x="Variant_phase",
            y="CFR_roll7_clean",
            color="Country",
            color_discrete_map=COLOR_MAP,
            points=False
        )

        fig.update_layout(
            title="Severity distribution by variant phase",
            xaxis_title="Variant phase",
            yaxis_title="Case fatality ratio (smoothed)",
            height=380,
            margin=dict(l=10, r=10, t=50, b=10)
        )

        return fig

    def compute_peak_table(df):
        table_cases = df.groupby(["Variant_phase", "Country"])[
            "cases_per_million"].max().unstack().round(1)
        table_deaths = df.groupby(["Variant_phase", "Country"])[
            "deaths_per_million"].max().unstack().round(1)
        return table_cases, table_deaths

    # =======================
    # PAGE CONTENT
    # =======================
    st.set_page_config(layout="wide")
    inject_style()

    df = load_data()
    if df.empty:
        return

    # Title
    st.markdown("<h1>Variant waves</h1>", unsafe_allow_html=True)

    st.markdown("""
        <p class="small-text">
        Variant driven segmentation of the pandemic in Chile, Ireland and Mexico, using transmission,
        mortality and severity patterns from 2020 to 2022.
        </p>
    """, unsafe_allow_html=True)

    # Variant badges
    st.markdown("## Variant phases")
    st.markdown("""
        <div>
            <span class="variant-tag">Pre Alpha</span>
            <span class="variant-tag">Alpha</span>
            <span class="variant-tag">Delta</span>
            <span class="variant-tag">Omicron</span>
            <span class="variant-tag">Post Omicron</span>
        </div>
    """, unsafe_allow_html=True)

    # CASES
    st.markdown("## Transmission over time")
    st.plotly_chart(plot_cases_variant(df), use_container_width=True)

    # DEATHS
    st.markdown("## Mortality over time")
    st.plotly_chart(plot_deaths_variant(df), use_container_width=True)

    # CFR BOX PLOT
    st.markdown("## Severity by variant phase")
    st.plotly_chart(plot_cfr_box(df), use_container_width=True)

    # PEAK TABLES
    st.markdown("## Peak pressure by variant phase")

    table_cases, table_deaths = compute_peak_table(df)

    st.markdown("### Peak cases per million")
    st.dataframe(table_cases, use_container_width=True)

    st.markdown("### Peak deaths per million")
    st.dataframe(table_deaths, use_container_width=True)

    st.markdown("""
        <p class="small-text">
        Delta produced the highest severity in all three countries, while Omicron drove the largest waves of transmission.
        </p>
    """, unsafe_allow_html=True)
