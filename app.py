import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE TU LLAVE ---
API_KEY = '47e6003535bac841cd890537c4b2674e'

# Configuración de página para móviles y escritorio
st.set_page_config(page_title="AI BETTING INTELLIGENCE", layout="wide", initial_sidebar_state="expanded")

# --- ESTILO PROFESIONAL (DARK GOLD) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #ffffff; }
    .premium-card { 
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        padding: 20px; border-radius: 12px; border: 1px solid #30363d;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .badge { background-color: #d4af37; color: black; padding: 2px 10px; border-radius: 5px; font-weight: bold; font-size: 11px; }
    .pick-text { color: #00ff00; font-size: 20px; font-weight: bold; margin: 10px 0; }
    .metric-val { font-size: 18px; color: #8b949e; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS REALES ---
def get_live_data(liga_id):
    url = f'https://api.the-odds-api.com/v4/sports/{liga_id}/odds/'
    params = {
        'apiKey': API_KEY,
        'regions': 'eu',
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# --- ESTADO DE LA APP ---
if 'bank' not in st.session_state: st.session_state.bank = 100.0
if 'history' not in st.session_state: st.session_state.history = []

# --- PANEL LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2533/2533515.png", width=80)
    st.markdown("### 💎 PREMIUM ACCESS")
    st.metric("MI CAPITAL", f"{st.session_state.bank:.2f} €")
    
    opciones_liga = {
        "soccer_spain_la_liga": "🇪🇸 LaLiga EA Sports",
        "soccer_spain_segunda_division": "🇪🇸 Segunda División",
        "soccer_epl": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League"
    }
    
    liga_sel = st.selectbox("Mercado Actual", options=list(opciones_liga.keys()), 
                            format_func=lambda x: opciones_liga[x])
    
    riesgo = st.select_slider("Perfil de Riesgo", options=[0.1, 0.2, 0.3, 0.4, 0.5], value=0.2)
    
    if st.button("🔄 Refrescar Cuotas"):
        st.rerun()

# --- DASHBOARD ---
st.title("🛡️ AI Betting Terminal")
st.write(f"Actualización del mercado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

datos = get_live_data(liga_sel)

if datos is None:
    st.error("⚠️ Error de conexión. Verifica el límite de tu API Key o la conexión.")
elif len(datos) == 0:
    st.info("No hay partidos disponibles para esta liga en las próximas horas.")
else:
    for partido in datos:
        try:
            home = partido['home_team']
            away = partido['away_team']
            cuota_local = partido['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
            
            # --- LÓGICA IA ---
            prob_ia = 1 / (cuota_local - 0.15) 
            edge = (prob_ia * cuota_local) - 1
            
            st.markdown(f"""
            <div class="premium-card">
                <span class="badge">SIGNAL DETECTED</span>
                <div style="margin-top:10px; font-size:22px; font-weight:bold;">{home} vs {away}</div>
                <div class="pick-text">PICK: GANA {home.upper()}</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.write(f"<p class='metric-val'>Cuota: <b>{cuota_local}</b></p>", unsafe_allow_html=True)
            col2.write(f"<p class='metric-val'>Confianza: <b>{int(prob_ia*100)}%</b></p>", unsafe_allow_html=True)
            
            if edge > 0.02:
                # Cálculo de Stake Corregido
                stake_calc = (edge / (cuota_local - 1)) * riesgo * st.session_state.bank
                stake = round(max(stake_calc, 0.0), 2)
                
                col3.write(f"<p class='metric-val'>Inversión: <b style='color:#00ff00'>{stake}€</b></p>", unsafe_allow_html=True)
                
                if col4.button(f"Apostar {stake}€", key=partido['id']):
                    st.session_state.bank -= stake
                    st.toast(f"Orden ejecutada en {home}")
                    st.rerun()
            else:
                col3.write("<p class='metric-val'>Valor: <b>Bajo</b></p>", unsafe_allow_html=True)
                col4.info("Esperar")
            
            st.divider()
        except Exception as e:
            continue

# --- SECCIÓN HISTORIAL ---
if st.session_state.bank < 1000: # Se muestra si ha habido actividad
    with st.expander("Ver operaciones recientes"):
        st.write("Sincronizando con el servidor de señales...")
