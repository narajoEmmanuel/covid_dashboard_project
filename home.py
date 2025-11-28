import streamlit as st
from PIL import Image
import base64


def render_home():

    def img_to_base64(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    # ==================== TYPOGRAPHY FIXED AND LARGE ====================
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

    html, body {
        font-family: 'Inter', sans-serif !important;
        line-height: 1.5 !important;
        font-size: 18px !important;
    }

    h1 {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 46px !important;
        font-weight: 700 !important;
        margin-bottom: 0.3rem !important;
    }

    h2 {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 32px !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.3rem !important;
    }

    h3 {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 26px !important;
        font-weight: 600 !important;
        margin-top: 0.8rem !important;
        margin-bottom: 0.2rem !important;
    }

    .card-body {
        font-size: 17px !important;
        line-height: 1.45 !important;
        color: #333333 !important;
    }

    .card-title {
        font-size: 20px !important;
        font-weight: 600 !important;
        margin-bottom: 0.2rem !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    .small-text {
        font-size: 15px !important;
        color: #666666 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ==================== LAYOUT AND GRID STYLING ====================
    st.markdown("""
    <style>
    .block-container {
        max-width: 94% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 0.2rem !important;
        padding-bottom: 2rem !important;
    }
    .element-container {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    p.small-text {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    .card {
        background-color: #F7F9FC;
        border-radius: 0.8rem;
        padding: 1.0rem 1.3rem !important;
        border: 1px solid #E5E5E5;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    .card-title {
        margin-bottom: 0.3rem !important;
    }
    .element-container img {
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-bottom: 0.4rem !important;
    }
    h1 { margin-bottom: 0.1rem !important; }
    h2 { margin-top: 0.5rem !important; margin-bottom: 0.1rem !important; }
    h3 { margin-top: 0.5rem !important; margin-bottom: 0.1rem !important; }
    </style>
    """, unsafe_allow_html=True)

    # ========= HERO SECTION =========
    st.markdown("<h1>COVID-19 Comparative Dashboard 2020 to 2022</h1>",
                unsafe_allow_html=True)

    try:
        banner = Image.open("assets/banner.png")
        banner = banner.resize((banner.width, 260))
        st.image(banner, use_container_width=True)
    except:
        st.warning(
            "Banner not found. Please add banner.png to the assets/ folder.")

    st.markdown(
        "<p class='small-text'>Comparative epidemiological analysis of Chile, Ireland, and Mexico for strategic pandemic preparedness.</p>",
        unsafe_allow_html=True
    )

    # ========= ROLE AND STAKEHOLDER =========
    st.markdown("## Role and Stakeholder")

    col_role, col_stake = st.columns(2)

    with col_role:
        st.markdown("""
            <div class="card">
                <div class="card-title">Analyst role</div>
                <div class="card-body">
                    Health Data Analyst for the Ministry of Health of Mexico,
                    focused on comparative epidemiology, vaccination impact,
                    and preparedness for future large scale outbreaks.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_stake:
        st.markdown("""
            <div class="card">
                <div class="card-title">Primary stakeholder</div>
                <div class="card-body">
                    <b>Dirección General de Epidemiología (DGE), Mexico</b>,
                    responsible for surveillance, early warning, and data informed
                    decision making in national health emergencies.
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ========= PURPOSE =========
    st.markdown("## Purpose of this dashboard")

    st.markdown("""
        <div class="card">
            <div class="card-body">
                This dashboard compares how Chile, Ireland, and Mexico experienced and managed
                the COVID-19 pandemic between 2020 and 2022.
                <ul>
                    <li>Understand how timing and speed of vaccination shaped each country's trajectory</li>
                    <li>Evaluate mortality pressure and case fatality under different variant eras</li>
                    <li>Identify where Mexico faced higher pressure and slower decoupling</li>
                    <li>Extract lessons for future pandemic preparedness</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ========= COUNTRY CARDS =========
    st.markdown("## Countries in scope and population context")

    chile_b64 = img_to_base64("assets/chile_outline.png")
    ireland_b64 = img_to_base64("assets/ireland_outline.png")
    mexico_b64 = img_to_base64("assets/mexico_outline.png")

    col_c1, col_c2, col_c3 = st.columns(3)

    def country_card(b64_img, title, text):
        return f"""
        <div style="
            background-color:#F7F9FC;
            border:1px solid #E5E5E5;
            border-radius:0.9rem;
            padding:1.2rem;
            text-align:center;
        ">
            <img src="data:image/png;base64,{b64_img}" style="width:160px; margin-bottom:1rem;">
            <div style="font-family:Montserrat; font-size:22px; font-weight:600; margin-bottom:0.3rem;">
                {title}
            </div>
            <div style="font-size:17px; color:#444;">
                {text}
            </div>
        </div>
        """

    with col_c1:
        st.markdown(country_card(
            chile_b64,
            "Chile",
            "Population: 19.2 million<br>Fast vaccination rollout and strong coverage before Delta and Omicron."
        ), unsafe_allow_html=True)

    with col_c2:
        st.markdown(country_card(
            ireland_b64,
            "Ireland",
            "Population: 5.0 million<br>High resilience and very low CFR in late phases."
        ), unsafe_allow_html=True)

    with col_c3:
        st.markdown(country_card(
            mexico_b64,
            "Mexico",
            "Population: 126.7 million<br>Early start but slower coverage, sustained mortality pressure across waves."
        ), unsafe_allow_html=True)

    st.markdown("""
    <p class="small-text" style="margin-top:0.8rem;">
    All metrics are expressed per million inhabitants to enable fair cross-country comparisons.
    </p>
    """, unsafe_allow_html=True)

    # ========= VARIANT ERA CARDS =========
    st.markdown("## Variant eras considered")

    st.markdown("""
        <div class="small-text">
        These eras help interpret how vaccination and health system resilience interacted with each wave.
        </div>
    """, unsafe_allow_html=True)

    col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)

    for col, title, body in [
        (col_v1, "Pre Alpha", "Before Jan 2021.<br>No vaccination, high uncertainty."),
        (col_v2, "Alpha", "Jan 2021 to Jun 2021.<br>Early vaccination rollout."),
        (col_v3, "Delta", "Jul 2021 to Nov 2021.<br>High severity & mortality."),
        (col_v4, "Omicron", "Dec 2021 to Jun 2022.<br>High transmission, decoupling visible."),
        (col_v5, "Post Omicron", "From Jul 2022 onward.<br>Toward endemic patterns.")
    ]:
        col.markdown(f"""
            <div class="card">
                <div class="card-title">{title}</div>
                <div class="card-body">{body}</div>
            </div>
        """, unsafe_allow_html=True)

    # ========= DATA SOURCES =========
    st.markdown("## Data sources")

    col_ds, _ = st.columns([2, 1])

    with col_ds:
        st.markdown("""
            <div class="card">
                <div class="card-body small-text">
                    Uses official WHO data:
                    <ul>
                        <li>WHO COVID-19 Global Daily Dataset</li>
                        <li>WHO Vaccine Uptake Dataset</li>
                        <li>WHO Vaccine Introduction Database</li>
                    </ul>
                    Analyses restricted to Chile, Ireland, Mexico (2020–2022).
                </div>
            </div>
        """, unsafe_allow_html=True)
