import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
API_KEY = '47e6003535bac841cd890537c4b2674e'
st.set_page_config(page_title="AI BETTING PRO TERMINAL", layout="wide", initial_sidebar_state="expanded")

# --- 2. PERSISTENCIA DE DATOS (Database interna) ---
if 'balance' not in st.session_state: st.session_state.balance = 1000.0
if 'history_chart' not in st.session_state: st.session_state.history_chart = [1000.0]
if 'bets_log' not in st.session_state: st.session_state.bets_log = [] # Historial de todas las apuestas
if 'active_bets' not in st.session_state: st.session_state.active_bets = [] # Apuestas sin resolver

# --- 3. ESTILO CSS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    [data-testid="stSidebar"] { background-color: #0c0c0c; border-right: 1px solid #d4af37; }
    .card-valor { 
        background: linear-gradient(145deg, #0f1a0f 0%, #050505 100%); 
        padding: 20px; border-radius: 15px; border: 1px solid #00ff00; margin-bottom: 15px;
    }
    .metric-box {
        background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8962e);
        color: black !important; font-weight: bold; border-radius: 8px; border: none; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MOTOR DE DATOS ---
def fetch_odds(liga):
    url = f'https://api.the-odds-api.com/v4/sports/{liga}/odds/'
    params = {'apiKey': API_KEY, 'regions': 'eu', 'markets': 'h2h', 'oddsFormat': 'decimal'}
    try:
        r = requests.get(url, params=params)
        return r.json() if r.status_code == 200 else []
    except: return []

# --- 5. PANEL LATERAL (Control de Riesgo) ---
with st.sidebar:
    st.markdown("<h2 style='color:#d4af37;'>ELITE CONTROL</h2>", unsafe_allow_html=True)
    st.metric("BALANCE TOTAL", f"{st.session_state.balance:.2f} €")
    st.divider()
    liga_sel = st.selectbox("Mercado Objetivo", 
                            options=["soccer_spain_la_liga", "soccer_spain_segunda_division", "soccer_epl"],
                            format_func=lambda x: "LaLiga" if "la_liga" in x else ("Segunda Div." if "segunda" in x else "Premier League"))
    
    riesgo_kelly = st.slider("Agresividad (Kelly Fracc.)", 0.05, 0.30, 0.10, help="0.10 es lo recomendado para gestión profesional.")
    
    if st.button("BORRAR DATOS Y RESET"):
        st.session_state.balance = 1000.0
        st.session_state.history_chart = [1000.0]
        st.session_state.bets_log = []
        st
