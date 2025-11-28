import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go


def render_cases():

    # --------------------------------------------
    # PATHS AND CONSTANTS
    # --------------------------------------------
    DATA_PATH = Path("data/merged_covid_dataset_FINAL_with_population.csv")
    COUNTRIES = ["Chile", "Ireland", "Mexico"]

    COLOR_MAP = {
        "Chile": "#2F6FED",     # blue
        "Ireland": "#FF8C42",   # orange
        "Mexico": "#2E8B57",    # green
    }

    # --------------------------------------------
    # LOAD DATA
    # --------------------------------------------

    @st.cache_data
    def load_data() -> pd.DataFrame:
        if not DATA_PATH.exists():
            st.error(
                f"Dataset not found at {DATA_PATH}. Please check the path.")
            return pd.DataFrame()

        df = pd.read_csv(DATA_PATH)
        df["Date_reported"] = pd.to_datetime(df["Date_reported"])

        df = df[df["Country"].isin(COUNTRIES)].copy()
        df = df[(df["Date_reported"] >= "2020-01-01") &
                (df["Date_reported"] <= "2022-12-31")]

        # Ensure numeric cols
        for col in [
            "cases_per_million", "deaths_per_million",
            "New_cases_roll7", "New_deaths_roll7",
            "CFR_roll7_clean", "population"
        ]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df.sort_values(["Country", "Date_reported"], inplace=True)
        return df

    # --------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------
    def compute_kpis(df: pd.DataFrame) -> pd.DataFrame:
        summary = (
            df.groupby("Country")
            .agg(
                peak_cases_pm=("cases_per_million", "max"),
                peak_deaths_pm=("deaths_per_million", "max"),
                max_cfr=("CFR_roll7_clean", "max"),
            )
            .reset_index()
        )

        summary["peak_cases_pm"] = summary["peak_cases_pm"].round(1)
        summary["peak_deaths_pm"] = summary["peak_deaths_pm"].round(1)
        summary["max_cfr"] = summary["max_cfr"].round(3)

        return summary

    # --------------------------------------------
    # LAG ANALYSIS
    # --------------------------------------------
    def compute_lag_cases_deaths(df: pd.DataFrame, max_lag_days: int = 30) -> pd.DataFrame:
        results = []

        for country in COUNTRIES:
            sub = df[df["Country"] == country].sort_values(
                "Date_reported").copy()
            cases = np.nan_to_num(sub["New_cases_roll7"].values)
            deaths = np.nan_to_num(sub["New_deaths_roll7"].values)

            if np.all(cases == 0) or np.all(deaths == 0):
                continue

            best_lag = 0
            best_corr = 0.0

            for lag in range(0, max_lag_days + 1):
                if lag == 0:
                    c = np.corrcoef(cases, deaths)[0, 1]
                else:
                    c = np.corrcoef(cases[:-lag], deaths[lag:])[0, 1]

                if not np.isnan(c) and c > best_corr:
                    best_corr = c
                    best_lag = lag

            results.append({
                "Country": country,
                "lag_days_cases_to_deaths": int(best_lag),
                "max_correlation": round(float(best_corr), 2),
            })

        return pd.DataFrame(results)

    # --------------------------------------------
    # VACCINATION INTRO (single date)
    # --------------------------------------------
    def get_vaccine_intro_by_country(df: pd.DataFrame) -> pd.Series:
        tmp = df.dropna(subset=["COVID_VACCINE_DATE_INTRO_FIRST"]).copy()
        tmp["COVID_VACCINE_DATE_INTRO_FIRST"] = pd.to_datetime(
            tmp["COVID_VACCINE_DATE_INTRO_FIRST"]
        )
        return tmp.groupby("Country")["COVID_VACCINE_DATE_INTRO_FIRST"].min()

    # --------------------------------------------
    # GLOBAL STYLE (same as Home)
    # --------------------------------------------
    def inject_global_style():
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

            html, body, [class^="css-"] {
                font-family: 'Inter', sans-serif !important;
                font-size: 18px !important;
                line-height: 1.5 !important;
            }

            h1 {
                font-family: 'Montserrat', sans-serif !important;
                font-size: 40px !important;
                margin-bottom: 0.4rem !important;
            }

            h2 {
                font-family: 'Montserrat', sans-serif !important;
                font-size: 30px !important;
                margin-top: 1rem !important;
                margin-bottom: 0.3rem !important;
            }

            .section-caption {
                font-size: 15px !important;
                color: #666;
                margin-bottom: 0.6rem;
            }

            .kpi-block {
                background-color: #F7F9FC;
                border-radius: 0.8rem;
                padding: 1.1rem 1.3rem;
                border: 1px solid #E5E5E5;
            }

            .kpi-title {
                font-size: 11px;
                letter-spacing: 0.08em;
                font-weight: 600;
                text-transform: uppercase;
                color: #666666;
                margin-bottom: 0.2rem;
            }

            .kpi-value {
                font-size: 28px;
                font-weight: 700;
                color: #111111;
                margin-bottom: 0.2rem;
            }

            .kpi-sub {
                font-size: 13px;
                color: #777777;
            }

            .block-container {
                max-width: 94% !important;
            }
            </style>
        """, unsafe_allow_html=True)

    # --------------------------------------------
    # PLOTS
    # --------------------------------------------
    def plot_cases(df):
        fig = px.line(
            df, x="Date_reported", y="cases_per_million",
            color="Country", color_discrete_map=COLOR_MAP
        )
        fig.update_layout(
            title="Transmission intensity over time",
            height=380, margin=dict(l=10, r=10, t=50, b=10)
        )
        return fig

    def plot_deaths(df):
        fig = px.line(
            df, x="Date_reported", y="deaths_per_million",
            color="Country", color_discrete_map=COLOR_MAP
        )
        fig.update_layout(
            title="Mortality pressure across waves",
            height=380, margin=dict(l=10, r=10, t=50, b=10)
        )
        return fig

    def plot_cfr(df):
        fig = px.line(
            df, x="Date_reported", y="CFR_roll7_clean",
            color="Country", color_discrete_map=COLOR_MAP
        )
        fig.update_layout(
            title="Smoothed case fatality ratio",
            height=380, margin=dict(l=10, r=10, t=50, b=10)
        )
        return fig

    def plot_mexico_vax_turning_point(df, intro_dates):
        mex = df[df["Country"] == "Mexico"].copy()
        fig = px.line(
            mex,
            x="Date_reported",
            y="cases_per_million",
            color_discrete_sequence=["#2E8B57"],
        )

        mex_intro = intro_dates.get("Mexico", None)
        if hasattr(mex_intro, "iloc"):  # fix possible Series
            mex_intro = mex_intro.iloc[0]

        if pd.notna(mex_intro):
            mex_intro = pd.to_datetime(mex_intro)

            # clean vline (no auto annotation)
            fig.add_vline(
                x=mex_intro,
                line_dash="dash",
                line_color="#CC0000",
                opacity=0.9,
            )

            fig.add_annotation(
                x=mex_intro,
                y=mex["cases_per_million"].max() * 0.9,
                text="Start of vaccination",
                showarrow=False,
                font=dict(color="#CC0000", size=12),
                xanchor="left"
            )

        fig.update_layout(
            title="Mexico — first vaccination date highlighted",
            height=380,
            margin=dict(l=10, r=10, t=50, b=10),
            showlegend=False,
        )
        return fig

    # --------------------------------------------
    # RENDER PAGE
    # --------------------------------------------
    st.set_page_config(layout="wide")
    inject_global_style()

    df = load_data()
    if df.empty:
        return

    kpi_df = compute_kpis(df)
    lag_df = compute_lag_cases_deaths(df)
    vax_intro = get_vaccine_intro_by_country(df)

    # ---------------- TITLE ----------------
    st.markdown("<h1>Cases and mortality, 2020 to 2022</h1>",
                unsafe_allow_html=True)

    st.markdown("""
        <p class="section-caption">
        Rolling, population adjusted indicators show where each country faced higher pressure and
        how mortality evolved as vaccination advanced.
        </p>
    """, unsafe_allow_html=True)

    # ---------------- KPI BLOCKS ----------------
    st.markdown("## Executive overview")

    col1, col2, col3 = st.columns(3)

    for col, country in zip([col1, col2, col3], COUNTRIES):
        row = kpi_df[kpi_df["Country"] == country].iloc[0]
        with col:
            st.markdown(f"""
                <div class="kpi-block">
                    <div class="kpi-title">Peak cases per million ({country})</div>
                    <div class="kpi-value">{row['peak_cases_pm']}</div>
                    <div class="kpi-sub">Highest observed rolling infection intensity.</div>
                    <br/>
                    <div class="kpi-title">Peak deaths per million ({country})</div>
                    <div class="kpi-value">{row['peak_deaths_pm']}</div>
                    <div class="kpi-sub">Maximum mortality pressure in 2020 to 2022.</div>
                    <br/>
                    <div class="kpi-title">Highest smoothed CFR ({country})</div>
                    <div class="kpi-value">{row['max_cfr']}</div>
                    <div class="kpi-sub">Upper bound of observed case fatality.</div>
                </div>
            """, unsafe_allow_html=True)

    # ---------------- MAIN GRAPHS ----------------
    st.markdown("## Cases and deaths per million")

    col_cases, col_deaths = st.columns(2)

    with col_cases:
        st.plotly_chart(plot_cases(df), use_container_width=True)

    with col_deaths:
        st.plotly_chart(plot_deaths(df), use_container_width=True)

    # ---------------- CFR ----------------
    st.markdown("## Severity and decoupling")

    st.markdown("""
        <p class="section-caption">
        CFR helps assess how severity declined as vaccination expanded.
        </p>
    """, unsafe_allow_html=True)

    st.plotly_chart(plot_cfr(df), use_container_width=True)

    # ---------------- LAG ----------------
    st.markdown("## Lag between cases and deaths")

    lag_text_col, lag_table_col = st.columns([1.4, 1.0])

    with lag_text_col:
        st.markdown("""
            The time between rising infections and rising deaths provides a practical
            operational window for planning hospital capacity and mitigation actions.
        """)

    with lag_table_col:
        st.dataframe(lag_df, hide_index=True)

    # ---------------- VACCINATION TURNING POINT ----------------
    st.markdown("## Vaccination as a turning point — Mexico")

    vax_text, vax_chart = st.columns([1.4, 1.2])

    with vax_text:
        mex_intro_date = vax_intro.get("Mexico", None)
        intro_str = (
            pd.to_datetime(mex_intro_date).strftime("%d %b %Y")
            if pd.notna(mex_intro_date) else "not available"
        )

        st.markdown(f"""
            Mexico's first COVID 19 vaccination date (**{intro_str}**) marks a structural
            shift in the trajectory. Before this date, epidemic control depended on
            non pharmaceutical interventions. After vaccination begins, reductions in
            severity and transmission start to become visible.
        """)

    with vax_chart:
        st.plotly_chart(
            plot_mexico_vax_turning_point(df, vax_intro),
            use_container_width=True,
        )
