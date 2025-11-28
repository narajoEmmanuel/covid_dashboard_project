import numpy as np
from io import BytesIO
import base64
import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
import plotly.express as px

# =========================================================
# PAGE SETUP
# =========================================================
st.set_page_config(
    page_title="COVID19 Comparative Dashboard 2020 to 2022",
    layout="wide",
)

# =========================================================
# LOAD CSS
# =========================================================
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
DATA_PATH = Path("data/merged_covid_dataset_FINAL_with_population.csv")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Date_reported"] = pd.to_datetime(df["Date_reported"], errors="coerce")
    df = df[(df["Date_reported"] >= "2020-01-01") &
            (df["Date_reported"] <= "2022-12-31")]
    return df


df = load_data()

# =========================================================
# FLAG IMAGES
# =========================================================


def load_flag(path):
    try:
        return Image.open(path)
    except:
        return None


flag_chile = load_flag("assets/chile.png")
flag_ireland = load_flag("assets/ireland.png")
flag_mexico = load_flag("assets/mexico.png")

# =========================================================
# PLOT FUNCTIONS — ENHANCED FOR STORYTELLING
# =========================================================
VACCINE_START_GLOBAL = pd.to_datetime("2020-12-25")


def plot_cases(df):
    fig = px.line(
        df,
        x="Date_reported",
        y="cases_per_million",
        color="Country",
        color_discrete_map={
            "Chile": "#2F6FED",
            "Ireland": "#FF8C42",
            "Mexico": "#2E8B57",
        },
    )

    fig.update_layout(
        yaxis_title="Cases per million",
        xaxis_title="",
        height=380,
        legend_title="",
        margin=dict(l=20, r=20, t=50, b=20),

        # Axis font size
        xaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=18),
        ),
        yaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=18),
        ),

        # Legend font
        legend=dict(
            font=dict(size=18),
        )
    )
    fig.add_vline(
        x=VACCINE_START_GLOBAL,
        line_width=2,
        line_dash="dash",
        line_color="#444",
        opacity=0.9
    )

    fig.add_annotation(
        x=VACCINE_START_GLOBAL,
        y=df["cases_per_million"].max() * 0.95,
        text="Approx. start of vaccination",
        showarrow=False,
        font=dict(size=16, color="#444"),
        xanchor="left"
    )

    fig.update_traces(line=dict(width=3))
    fig.update_layout(showlegend=True)

    return fig

# =========================================================


def plot_deaths(df):
    max_val = df["deaths_per_million"].max()

    fig = px.line(
        df,
        x="Date_reported",
        y="deaths_per_million",
        color="Country",
        color_discrete_map={
            "Chile": "#2F6FED",
            "Ireland": "#FF8C42",
            "Mexico": "#2E8B57",
        },
    )

    fig.update_layout(
        yaxis_title="Deaths per million",
        xaxis_title="",
        height=420,
        legend_title="",
        yaxis=dict(
            range=[0, max_val * 1.15],
            title_font=dict(size=20),
            tickfont=dict(size=18),
        ),
        xaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=18),
        ),
        margin=dict(l=20, r=20, t=60, b=40),

        legend=dict(
            font=dict(size=18),
        )
    )
    fig.add_vline(
        x=VACCINE_START_GLOBAL,
        line_width=2,
        line_dash="dash",
        line_color="#444",
        opacity=0.9
    )

    fig.add_annotation(
        x=VACCINE_START_GLOBAL,
        y=df["deaths_per_million"].max() * 0.95,
        text="Approx. start of vaccination",
        showarrow=False,
        font=dict(size=16, color="#444"),
        xanchor="right"
    )

    fig.update_traces(line=dict(width=3))

    return fig

# =========================================================


def compute_mortality_change(df, country):
    df_c = df[df["Country"] == country].copy()

    vaccination_cutoff = pd.to_datetime("2021-03-01")

    before = df_c[df_c["Date_reported"] <
                  vaccination_cutoff]["deaths_per_million"].mean()
    after = df_c[df_c["Date_reported"] >=
                 vaccination_cutoff]["deaths_per_million"].mean()

    if pd.isna(before) or pd.isna(after) or before == 0:
        return None

    change = ((after - before) / before) * 100
    return round(change, 1)


# =========================================================


def mortality_card(country, value):
    return f"""
    <div style="
        background-color:#F7F9FC;
        border:1px solid #E5E5E5;
        border-radius:0.9rem;
        padding:1.2rem;
        text-align:center;
    ">
        <div style="font-family:Montserrat; font-size:24px; font-weight:600; margin-bottom:0.6rem;">
            {country}
        </div>

        <div style="font-size:38px; font-weight:700; color:#2E8B57; margin-bottom:0.4rem;">
            {value}%
        </div>

        <div style="font-size:18px; color:#555; line-height:1.4;">
            Change in mortality rate<br>
            Avg deaths per million<br>
            12 months before vs after vaccination start
        </div>
    </div>
    """


# =========================================================
# HEADER
# =========================================================
st.markdown(
    "<h1 style='text-align:center;'>COVID19 Comparative Dashboard 2020 to 2022</h1>",
    unsafe_allow_html=True
)

st.markdown("""
<p class='small-text' style='text-align:center; margin-bottom:0.2rem;'>
Comparative epidemiological analysis of Chile, Ireland and Mexico<br>
for strategic pandemic preparedness using WHO official data.
</p>
""", unsafe_allow_html=True)


# =========================================================
# COUNTRY INTRO CARDS
# =========================================================


# Extract populations automatically
pop_chile = int(df[df["Country"] == "Chile"]["population"].iloc[0])
pop_ireland = int(df[df["Country"] == "Ireland"]["population"].iloc[0])
pop_mexico = int(df[df["Country"] == "Mexico"]["population"].iloc[0])

col_c1, col_c2, col_c3 = st.columns(3)


def country_card(flag, name, population, text):
    flag_html = ""
    if flag:
        flag_html = f"<img src='data:image/png;base64,{image_to_base64(flag)}' width='70' style='margin-bottom:0.8rem;'>"

    return f"""
    <div style="
        background-color:#F7F9FC;
        border:1px solid #E5E5E5;
        border-radius:0.9rem;
        padding:1.2rem;
        text-align:center;
    ">
        {flag_html}
        <div style="font-family:Montserrat; font-size:24px; font-weight:600; margin-bottom:0.4rem;">
            {name}
        </div>
        <div style="font-size:20px; color:#444;">
            Population: {population:,}
        </div>
        <div style="font-size:20px; margin-top:0.6rem; color:#555;">
            {text}
        </div>
    </div>
    """


# helper to convert image to base64


def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


with col_c1:
    st.markdown(country_card(
        flag_chile,
        "Chile",
        pop_chile,
        "Fast vaccination trajectory and strong decoupling during Delta and Omicron."
    ), unsafe_allow_html=True)

with col_c2:
    st.markdown(country_card(
        flag_ireland,
        "Ireland",
        pop_ireland,
        "High resilience, rapid CFR decline and the lowest mortality pressure."
    ), unsafe_allow_html=True)

with col_c3:
    st.markdown(country_card(
        flag_mexico,
        "Mexico",
        pop_mexico,
        "Early vaccination start but slower coverage, sustaining higher mortality pressure."
    ), unsafe_allow_html=True)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =========================================================
# SECTION 1 — EPIDEMIOLOGICAL TIMELINE
# =========================================================
st.markdown("<h2>Epidemiological timeline</h2>", unsafe_allow_html=True)


# ------------------------------
# CASES PLOT (REAL)
# ------------------------------
st.markdown("### Transmission intensity over time (cases per million)")

st.markdown("""
<p class="explanation-text">
Chile shows the highest early surge, Ireland presents fewer but sharper peaks,
and Mexico maintains long, sustained waves with slower declines.
</p>
""", unsafe_allow_html=True)

st.plotly_chart(plot_cases(df), use_container_width=True)

st.markdown("&nbsp;", unsafe_allow_html=True)

# ------------------------------
# DEATHS PLOT (REAL)
# ------------------------------
st.markdown("### Mortality pressure over time (deaths per million)")

st.markdown("""
<p class="explanation-text">
Ireland maintains the lowest mortality burden, Chile sees rapid drops after vaccination,
and Mexico experiences prolonged mortality pressure during early stages.
</p>
""", unsafe_allow_html=True)

st.plotly_chart(plot_deaths(df), use_container_width=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =========================================================
# SECTION 2 — MORTALITY CHANGE AFTER VACCINATION
# =========================================================

st.markdown("<h2 style='text-align:center;'>Mortality impact after vaccination</h2>",
            unsafe_allow_html=True)

st.markdown("""
<p class='small-text' style='text-align:center; margin-bottom:2rem;'>
We compare the average deaths per million 12 months before vs 12 months after vaccination started.
</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='text-align:center; font-family:Montserrat;'>
        <div style='font-size:24px; font-weight:600; color:#444; margin-bottom:0.8rem;'>Chile</div>
        <div style='font-size:40px; font-weight:700; color:#2EB857;'>-16.3% </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align:center; font-family:Montserrat;'>
        <div style='font-size:24px; font-weight:600; color:#444; margin-bottom:0.8rem;'>Ireland</div>
        <div style='font-size:40px; font-weight:700; color:#2EB857;'>-53.2%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align:center; font-family:Montserrat;'>
        <div style='font-size:24px; font-weight:600; color:#444; margin-bottom:0.8rem;'>Mexico</div>
        <div style='font-size:40px; font-weight:700; color:#2EB857;'>-69.9%</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# SECTION 3 — INTERPRETATION OF MORTALITY CHANGE
# =========================================================
st.write("  ")
st.write("  ")
st.markdown("<h2>How to interpret the mortality changes?</h2>",
            unsafe_allow_html=True)

st.markdown("""
<p class="explanation-text">
Mexico shows a large decline because its mortality burden before vaccination was extremely high and prolonged.
Ireland and Chile display smaller percentage shifts, but they reached much lower absolute mortality levels and stabilized earlier.
</p>
""", unsafe_allow_html=True)


# =========================================================
# SECTION 3 — Mortality wave silhouettes
# =========================================================


# --------------------------
# Helper function for silhouette plots
# --------------------------


def plot_silhouette(df, country, color):
    sub = df[df["Country"] == country].copy()

    fig = px.line(
        sub,
        x="Date_reported",
        y="deaths_per_million",
        color_discrete_sequence=[color]
    )

    # Remove everything except the curve
    fig.update_layout(
        height=180,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    # Thicker line
    fig.update_traces(line=dict(width=4))

    # Global vaccination marker
    fig.add_vline(
        x=VACCINE_START_GLOBAL,
        line_width=2,
        line_dash="dash",
        line_color="#444",
        opacity=0.9,
    )

    return fig


# --------------------------
# Render 3 silhouettes in a row
# --------------------------
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    st.markdown("<h3 style='text-align:center;'>Chile</h3>",
                unsafe_allow_html=True)
    st.plotly_chart(plot_silhouette(df, "Chile", "#2F6FED"),
                    use_container_width=True)

with col_s2:
    st.markdown("<h3 style='text-align:center;'>Ireland</h3>",
                unsafe_allow_html=True)
    st.plotly_chart(plot_silhouette(df, "Ireland", "#FF8C42"),
                    use_container_width=True)

with col_s3:
    st.markdown("<h3 style='text-align:center;'>Mexico</h3>",
                unsafe_allow_html=True)
    st.plotly_chart(plot_silhouette(df, "Mexico", "#2E8B57"),
                    use_container_width=True)


# --------------------------
# Interpretative block
# --------------------------
st.markdown("""
<div class="card" style="margin-top:1rem;">
    <div class="card-title">Interpretation</div>
    <div class="card-body">
        Chile and Ireland exhibit short, sharp mortality waves that decline rapidly after vaccination,
        illustrating fast decoupling and strong health system response.
        Mexico, in contrast, presents long and persistent mortality waves prior to vaccination,
        indicating slower epidemic control, higher baseline pressure, and a more demanding hospital load.
        These wave shapes reveal fundamental differences in surveillance capacity, timing of interventions,
        and population level protection across countries.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# =========================================================
# FINAL STRATEGIC RECOMMENDATIONS — FIXED AND CSS-COMPATIBLE
# =========================================================

st.markdown(
    "<h2>Final Recommendations for the Ministry of Health</h2>",
    unsafe_allow_html=True
)


# ------------------------------------------
# MAIN CARD WITH RECOMMENDATIONS
# ------------------------------------------
st.markdown("""
<div class="card" style="margin-top:1rem;">
<div class="card-title">What can Mexico learn?</div>
<div class="card-body">
<ul style="font-size:20px; line-height:1.45; padding-left:1.2rem; margin-top:0.4rem;">
<li><strong>Strengthen early wave detection.</strong> Improve real time surveillance in high density regions to anticipate transmission surges earlier. Chile and Ireland benefited from faster wave recognition, which supported faster decoupling.</li>
<li><strong>Accelerate vaccination rollout in structurally vulnerable regions.</strong> Mexico shows large percentage reductions but remained with higher absolute mortality. Faster vaccination and booster uptake in plateau prone regions reduce prolonged mortality.</li>
<li><strong>Expand hospital surge capacity readiness.</strong> Ireland’s low mortality reflects strong ICU elasticity. Mexico would benefit from reinforced surge protocols, oxygen distribution stability, and ICU scaling triggers.</li>
<li><strong>Improve community risk communication during long plateaus.</strong> Mexico’s mortality waves show long, sustained phases. Targeted messaging during plateaus accelerates behavioral change and helps shorten prolonged high pressure periods.</li>
</ul>
</div>
</div>
""", unsafe_allow_html=True)
