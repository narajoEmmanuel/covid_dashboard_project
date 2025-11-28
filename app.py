from variant_waves import render_variant_waves
from vaccination import render_vaccination
from cases import render_cases
from home import render_home
import streamlit as st
from PIL import Image

st.set_page_config(layout="wide")

# =========================================================
# IMPORT PAGES (each as a function)
# =========================================================


# =========================================================
# UI TABS (SIMPLE, CLEAN, BEAUTIFUL)
# =========================================================

st.title("COVID-19 Comparative Dashboard 2020–2022")

tabs = st.tabs([
    "🏠 Home",
    "📊 Cases & Mortality",
    "💉 Vaccination Progress",
    "🧬 Variant Waves"
])

with tabs[0]:
    render_home()

with tabs[1]:
    render_cases()

with tabs[2]:
    render_vaccination()

with tabs[3]:
    render_variant_waves()
