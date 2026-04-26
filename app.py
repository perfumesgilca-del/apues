import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE TU LLAVE ---
API_KEY = '47e6003535bac841cd890537c4b2674e'

st.set_page_config(page_title="AI Betting Intelligence", layout="wide")

# --- ESTILO VISUAL DE ALTO VALOR ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }
    .premium-label {
        background-color: #d4af37;
        color: black;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
    }
    .pick-highlight { color: #00ff00; font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PARA OBTENER DATOS REALES ---
def get_live_odds(sport):
    url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds/'
    params = {
        'apiKey': API_KEY,
        'regions': 'eu',
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    try:
        response = requests.get(url, params=params)
        return response.json()
    except:
        return []

# --- INICIALIZACIÓN ---
if 'bank' not in st.session_state: st.session_state.bank = 100.0

# --- SIDEBAR ---
with st.sidebar:
    st.title("💎 AI Premium")
    st.metric("MI SALDO", f"{st.session_state.bank:.2f} €")
    liga = st.selectbox("Seleccionar Liga", 
                        ["soccer_spain_la_liga", "soccer_spain_la_liga_2", "soccer_epl"])
    riesgo = st.slider("Nivel de Riesgo (Kelly)", 0.1, 0.5, 0.2)
    if st.button("🔄 Sincronizar Mercados"):
        st.rerun()

# --- CUERPO PRINCIPAL ---
st.title("🎯 Señales Inteligentes en Tiempo Real")
st.write(f"Datos actualizados: {datetime.now().strftime('%H:%M:%S')}")

datos_api = get_live_odds(liga)

if not datos_api or "error" in str(datos_api):
    st.error("Error al conectar con la API. Revisa si has alcanzado el límite gratuito o si la llave es correcta.")
else:
    for partido in datos_api:
        # Extraer cuotas del primer bookmaker disponible
        try:
            home_team = partido['home_team']
            away_team = partido['away_team']
            bookie = partido['bookmakers'][0]
            market = bookie['markets'][0]
            
            # Cuotas: 0=Local, 1=Visitante, 2=Empate (depende de la API)
            outcomes = market['outcomes']
            c_local = next(o['price'] for o in outcomes if o['name'] == home_team)
            c_visit = next(o['price'] for o in outcomes if o['name'] == away_team)
            
            # --- SIMULACIÓN DE IA (Lógica de valor) ---
            # Aquí la IA detecta una probabilidad mayor a la de la cuota
            prob_ia = 1 / (c_local - 0.2) # Simulamos que la IA ve más probable al local
            edge = (prob_ia * c_local) - 1
            
            # --- RENDERIZADO DE TARJETA ---
            st.markdown(f"""
            <div class="card">
                <span class="premium-label">PREMIUM AI SIGNAL</span>
                <div style="margin-top:10px;">
                    <span style="font-size:20px;">{home_team} vs {away_team}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Cuota Casa", c_local)
            col2.metric("Prob. IA", f"{int(prob_ia*100)}%")
            
            if edge > 0.05:
                stake = round((edge / (c_local - 1)) * riesgo * st.session_state.bank, 2)
                col3.markdown(f"**APUESTA:** <br><span class='pick-highlight'>GANA {home_team.upper()}</span>", unsafe_allow_html=True)
                if col4.button(f"Invertir {stake}€", key=partido['id']):
                    st.session_state.bank -= stake
                    st.success("¡Apuesta añadida al historial!")
                    st.rerun()
            else:
                col3.write("Analizando...")
                col4.info("Sin valor claro")
            
            st.divider()
        except:
            continue
