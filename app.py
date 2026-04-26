import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IA Betting Pro - Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- ESTILO PERSONALIZADO (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445b; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    .bet-card { background-color: #161b22; padding: 20px; border-radius: 15px; border-left: 5px solid #238636; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA FINANCIERA ---
def calcular_stake_profesional(prob, cuota, bankroll, riesgo):
    edge = (prob * cuota) - 1
    if edge <= 0: return 0, 0
    kelly_pct = (edge / (cuota - 1)) * riesgo
    stake = min(kelly_pct, 0.05) * bankroll  # Nunca más del 5%
    return round(stake, 2), round(edge * 100, 1)

# --- ESTADO DE LA APP ---
if 'bank' not in st.session_state: st.session_state.bank = 100.0
if 'historial' not in st.session_state: st.session_state.historial = []

# --- SIDEBAR PROFESIONAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3408/3408506.png", width=100)
    st.title("Gestión de Bankroll")
    st.metric("Saldo Disponible", f"{st.session_state.bank:.2f} €", delta_color="normal")
    riesgo = st.select_slider("Perfil de Riesgo", options=[0.1, 0.2, 0.3, 0.4, 0.5], value=0.2, help="0.1 = Conservador, 0.5 = Agresivo")
    if st.button("🔄 Resetear Sistema"):
        st.session_state.bank = 100.0
        st.session_state.historial = []
        st.rerun()

# --- CUERPO PRINCIPAL ---
t1, t2 = st.tabs(["🎯 Oportunidades del Día", "📈 Mi Rendimiento"])

with t1:
    st.subheader("Predicciones de la IA")
    
    # Simulación de una base de datos más amplia
    datos_partidos = [
        {"liga": "🇪🇸 LaLiga Hypermotion", "local": "Real Oviedo", "visitante": "Sporting", "cuota": 2.45, "prob": 0.55},
        {"liga": "🇪🇸 LaLiga Hypermotion", "local": "Zaragoza", "visitante": "Levante", "cuota": 2.10, "prob": 0.52},
        {"liga": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "local": "Arsenal", "visitante": "Chelsea", "cuota": 1.85, "prob": 0.68},
        {"liga": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "local": "Liverpool", "visitante": "Everton", "cuota": 1.45, "prob": 0.75},
        {"liga": "🇪🇸 LaLiga", "local": "Sevilla", "visitante": "Betis", "cuota": 3.40, "prob": 0.38},
        {"liga": "🇪🇸 LaLiga", "local": "Real Madrid", "visitante": "Barcelona", "cuota": 2.15, "prob": 0.51}
    ]

    for p in datos_partidos:
        stake, edge = calcular_stake_profesional(p['prob'], p['cuota'], st.session_state.bank, riesgo)
        
        with st.container():
            st.markdown(f"""<div class="bet-card">
                <small>{p['liga']}</small><br>
                <strong>{p['local']} vs {p['visitante']}</strong>
                </div>""", unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Cuota", p['cuota'])
            c2.metric("Prob. IA", f"{int(p['prob']*100)}%")
            c3.metric("Valor (Edge)", f"{edge}%")
            
            if stake > 0:
                if c4.button(f"Invertir {stake}€", key=p['local']):
                    st.session_state.bank -= stake
                    st.session_state.historial.append({
                        "Fecha": datetime.datetime.now().strftime("%H:%M:%S"),
                        "Evento": f"{p['local']} vs {p['visitante']}",
                        "Inversión": stake
                    })
                    st.toast(f"¡Orden ejecutada! -{stake}€")
                    st.rerun()
            else:
                c4.warning("Sin valor")

with t2:
    st.subheader("Historial de Movimientos")
    if st.session_state.historial:
        df = pd.DataFrame(st.session_state.historial)
        st.table(df)
    else:
        st.info("Aún no has realizado operaciones hoy.")
