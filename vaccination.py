import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render_vaccination():

    DATA_PATH = Path("data/merged_covid_dataset_FINAL_with_population.csv")
    COUNTRIES = ["Chile", "Ireland", "Mexico"]

    COLOR_MAP = {
        "Chile": "#2F6FED",
        "Ireland": "#FF8C42",
        "Mexico": "#2E8B57",
    }

    # =========================
    # DATA LOADING
    # =========================
    @st.cache_data
    def load_data():
        if not DATA_PATH.exists():
            st.error(f"Dataset not found at {DATA_PATH}")
            return pd.DataFrame()

        df = pd.read_csv(DATA_PATH)
        df["Date_reported"] = pd.to_datetime(df["Date_reported"])

        df = df[df["Country"].isin(COUNTRIES)].copy()
        df = df[(df["Date_reported"] >= "2020-01-01") &
                (df["Date_reported"] <= "2022-12-31")]

        for col in [
            "COVID_VACCINE_COV_TOT_A1D",
            "COVID_VACCINE_COV_TOT_CPS",
            "COVID_VACCINE_COV_TOT_BOOST",
        ]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        if "COVID_VACCINE_DATE_INTRO_FIRST" in df.columns:
            df["COVID_VACCINE_DATE_INTRO_FIRST"] = pd.to_datetime(
                df["COVID_VACCINE_DATE_INTRO_FIRST"],
                errors="coerce"
            )

        df.sort_values(["Country", "Date_reported"], inplace=True)
        return df

    # =========================
    # METRICS
    # =========================
    def compute_vax_kpis(df):
        agg = (
            df.groupby("Country")
            .agg(
                vax_start=("COVID_VACCINE_DATE_INTRO_FIRST", "min"),
                max_cps=("COVID_VACCINE_COV_TOT_CPS", "max"),
                max_boost=("COVID_VACCINE_COV_TOT_BOOST", "max"),
            )
            .reset_index()
        )

        agg["max_cps"] = agg["max_cps"].round(1)
        agg["max_boost"] = agg["max_boost"].round(1)
        agg["vax_start_str"] = agg["vax_start"].dt.strftime("%d %b %Y")

        return agg

    def compute_coverage_milestones(df):
        milestones = [20, 40, 60, 80]
        rows = []

        for country in COUNTRIES:
            sub = df[df["Country"] == country]
            start_date = sub["COVID_VACCINE_DATE_INTRO_FIRST"].dropna().min()

            if pd.isna(start_date):
                rows.append({
                    "Country": country,
                    "20 percent": pd.NA,
                    "40 percent": pd.NA,
                    "60 percent": pd.NA,
                    "80 percent": pd.NA,
                })
                continue

            sub_after = sub[sub["Date_reported"] >= start_date]

            result = {"Country": country}
            for m in milestones:
                reached = sub_after[sub_after["COVID_VACCINE_COV_TOT_CPS"] >= m]
                if reached.empty:
                    result[f"{m} percent"] = pd.NA
                else:
                    result[f"{m} percent"] = (
                        reached["Date_reported"].iloc[0] - start_date).days

            rows.append(result)

        return pd.DataFrame(rows)

    # =========================
    # STYLING
    # =========================
    def inject_global_style():
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

        html, body, [class^="css-"] {
            font-family: 'Inter', sans-serif !important;
            font-size: 18px !important;
            line-height: 1.5 !important;
        }

        h1 { font-family: 'Montserrat'; font-size: 36px; font-weight: 700; }
        h2 { font-family: 'Montserrat'; font-size: 28px; font-weight: 600; }
        h3 { font-family: 'Montserrat'; font-size: 22px; font-weight: 600; }

        .block-container {
            max-width: 94% !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        .kpi-block {
            background-color: #F7F9FC;
            border-radius: 0.9rem;
            padding: 1rem 1.2rem;
            border: 1px solid #E5E5E5;
        }

        .kpi-title {
            font-size: 11px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #666;
        }

        .kpi-value {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 0.1rem;
        }

        .kpi-sub {
            font-size: 13px;
            color: #777;
        }
        </style>
        """, unsafe_allow_html=True)

    # =========================
    # PLOTS
    # =========================
    def plot_vax_coverage(df):
        fig = go.Figure()
        for country in COUNTRIES:
            sub = df[df["Country"] == country]
            fig.add_trace(go.Scatter(
                x=sub["Date_reported"],
                y=sub["COVID_VACCINE_COV_TOT_CPS"],
                mode="lines",
                name=f"{country} CPS",
                line=dict(color=COLOR_MAP[country], width=2.2),
            ))
        fig.update_layout(
            title="Vaccination coverage (complete primary series)",
            height=380,
            xaxis_title="Date",
            yaxis_title="Coverage percent"
        )
        return fig

    def plot_booster(df, country):
        sub = df[df["Country"] == country]
        fig = px.line(
            sub,
            x="Date_reported",
            y="COVID_VACCINE_COV_TOT_BOOST",
            color_discrete_sequence=[COLOR_MAP[country]],
        )
        fig.update_layout(
            title=f"{country} booster coverage",
            height=260,
            showlegend=False
        )
        return fig

    def plot_vax_vs_cfr(df, country):
        sub = df[df["Country"] == country].copy()
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Scatter(
            x=sub["Date_reported"],
            y=sub["COVID_VACCINE_COV_TOT_CPS"],
            mode="lines",
            name="CPS",
            line=dict(color=COLOR_MAP[country], width=2),
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=sub["Date_reported"],
            y=sub["CFR_roll7_clean"],
            mode="lines",
            name="CFR",
            line=dict(color="#444", width=1.8, dash="dot"),
        ), secondary_y=True)

        fig.update_layout(
            title=f"Coverage vs CFR in {country}",
            height=380
        )

        fig.update_yaxes(title_text="Coverage percent", secondary_y=False)
        fig.update_yaxes(title_text="CFR", secondary_y=True)

        return fig

    # =========================
    # PAGE CONTENT (NO MAIN FUNCTION)
    # =========================
    st.set_page_config(layout="wide")
    inject_global_style()

    df = load_data()
    if df.empty:
        return

    vax_kpis = compute_vax_kpis(df)
    milestones = compute_coverage_milestones(df)

    # TITLE
    st.markdown("<h1>Vaccination Progress</h1>", unsafe_allow_html=True)

    # KPIs
    st.markdown("## Executive vaccination KPIs")
    col1, col2, col3 = st.columns(3)

    for col, country in zip([col1, col2, col3], COUNTRIES):
        row = vax_kpis[vax_kpis["Country"] == country].iloc[0]
        col.markdown(f"""
        <div class="kpi-block">
            <div class="kpi-title">Start date</div>
            <div class="kpi-value">{row['vax_start_str']}</div>
            <br/>
            <div class="kpi-title">Peak CPS</div>
            <div class="kpi-value">{row['max_cps']}%</div>
            <br/>
            <div class="kpi-title">Peak booster</div>
            <div class="kpi-value">{row['max_boost']}%</div>
        </div>
        """, unsafe_allow_html=True)

    # MAIN COVERAGE
    st.markdown("## Coverage (CPS)")
    st.plotly_chart(plot_vax_coverage(df), use_container_width=True)

    # MILESTONES
    st.markdown("## Milestones (days to reach CPS targets)")
    st.dataframe(milestones, hide_index=True)

    # BOOSTERS
    st.markdown("## Booster rollout")
    b1, b2, b3 = st.columns(3)
    b1.plotly_chart(plot_booster(df, "Chile"), use_container_width=True)
    b2.plotly_chart(plot_booster(df, "Ireland"), use_container_width=True)
    b3.plotly_chart(plot_booster(df, "Mexico"), use_container_width=True)

    # CPS vs CFR
    st.markdown("## Coverage versus severity")
    selected = st.selectbox("Country", COUNTRIES, index=2)
    st.plotly_chart(plot_vax_vs_cfr(df, selected), use_container_width=True)
