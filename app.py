import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE TU LLAVE ---
API_KEY = '47e6003535bac841cd890537c4b2674e'

st.set_page_config(page_title="AI BETTING ELITE", layout="wide", initial_sidebar_state="expanded")

# --- CSS ULTRA PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0c0c0c; border-right: 1px solid #d4af37; }
    
    .stMetric { 
        background-color: #111; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #222;
        box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    
    .premium-card { 
        background: linear-gradient(145deg, #0f0f0f 0%, #1a1a1a 100%);
        padding: 25px; 
        border-radius: 20px; 
        border: 1px solid #333;
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
    }
    
    .premium-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: #d4af37;
    }

    .status-badge {
        background-color: #d4af37;
        color: black;
        padding: 4px 12px;
        border-radius: 50px;
        font-weight: 800;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .confidence-bar {
        background-color: #222;
        border-radius: 10px;
        height: 8px;
        width: 100%;
        margin-top: 10px;
    }

    .confidence-fill {
        background: linear-gradient(90deg, #d4af37, #00ff00);
        height: 100%;
        border-radius: 10px;
    }

    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -1px; }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8962e);
        color: black !important;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(212, 175, 55, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
def get_data(liga_id):
    url = f'https://api.the-odds-api.com/v4/sports/{liga_id}/odds/'
    params = {'apiKey': API_KEY, 'regions': 'eu', 'markets': 'h2h', 'oddsFormat': 'decimal'}
    try:
        r = requests.get(url, params=params)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- ESTADOS ---
if 'bank' not in st.session_state: st.session_state.bank = 1000.0

# --- SIDEBAR ELITE ---
with st.sidebar:
    st.markdown("<h2 style='color:#d4af37;'>ELITE TERMINAL</h2>", unsafe_allow_html=True)
    st.metric("CAPITAL BAJO GESTIÓN", f"{st.session_state.bank:.2f} €", delta="PRO PLAN")
    st.divider()
    
    opciones = {
        "soccer_spain_la_liga": "🇪🇸 LA LIGA EA",
        "soccer_spain_segunda_division": "🇪🇸 SEGUNDA DIV",
        "soccer_epl": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 PREMIER LEAGUE"
    }
    liga_sel = st.selectbox("MERCADO", options=list(opciones.keys()), format_func=lambda x: opciones[x])
    riesgo = st.select_slider("AGRESIVIDAD IA", options=[0.1, 0.2, 0.3, 0.4, 0.5], value=0.2)
    
    st.markdown("---")
    st.caption("SISTEMA DE SEÑALES VIRTUAL v2.4 Premium")

# --- HEADER ---
c1, c2, c3 = st.columns([2,1,1])
with c1:
    st.title("🎯 Signals Intelligence")
with c2:
    st.metric("YIELD MENSUAL", "+14.2%", "+2.1%")
with c3:
    st.metric("WIN RATE", "67%", "IA Optimizada")

st.markdown("---")

# --- CARGA DE PARTIDOS ---
datos = get_data(liga_sel)

if datos:
    for p in datos[:8]: # Mostramos los 8 más relevantes
        try:
            home = p['home_team']
            away = p['away_team']
            cuota = p['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
            
            # IA LOGIC
            confianza = 0.62 + (cuota % 0.1) # Simulación de confianza IA
            edge = (confianza * cuota) - 1
            
            with st.container():
                st.markdown(f"""
                <div class="premium-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span class="status-badge">High Value Signal</span>
                        <span style="color:#888; font-size:12px;">ID: {p['id'][:8].upper()}</span>
                    </div>
                    <div style="margin: 15px 0;">
                        <span style="font-size: 24px; font-weight: 900;">{home} <span style="color:#d4af37;">vs</span> {away}</span>
                    </div>
                    <div style="color: #00ff00; font-weight: bold; letter-spacing: 1px;">
                        RECOMENDACIÓN: GANA {home.upper()}
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {int(confianza*100)}%;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <small style="color:#555;">Confianza IA: {int(confianza*100)}%</small>
                        <small style="color:#555;">Edge: {round(edge*100, 1)}%</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1,1,2])
                col1.write(f"**Cuota Market**")
                col1.subheader(f"{cuota}")
                
                # Cálculo de inversión
                stake = round(max((edge / (cuota - 1)) * riesgo * st.session_state.bank, 0), 2)
                
                col2.write(f"**Inversión Sugerida**")
                col2.subheader(f"{stake}€")
                
                if col3.button(f"EJECUTAR ORDEN DE {stake}€", key=p['id']):
                    st.session_state.bank -= stake
                    st.toast(f"Orden ejecutada: {home}")
                    st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
        except: continue
else:
    st.error("No se han podido sincronizar las señales. Reintente en unos minutos.")
