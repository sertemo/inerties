import streamlit as st
import numpy as np
import secciones as sc
import graficar as gf
import pandas as pd
import aux_functions as af
import db
import time

st.set_page_config(
    page_title="Calculer Sections Multiples",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="auto",
)

if __name__ == '__main__':    

    st.title("Sections Composées - Propriétés mécaniques")

    st.markdown(
        """
    <style>
        .texto-amarillo {
            font-size: 64px;
            color: #FFD700;
        }
    </style>
    <div class="texto-amarillo">
    <b>⚠️ Under construction ⚠️</b>
    </div>""",
    unsafe_allow_html=True
    )