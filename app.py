import streamlit as st
import pandas as pd

# 1. Configuración de Seguridad
def calculate_kelly(prob, odds, bankroll, risk_factor=0.25):
    if prob is None or odds <= 1: return 0, 0, 0
    edge = (prob * odds) - 1
    if edge <= 0: return 0, 0, 0
    
    # Criterio de Kelly Fraccionado
    kelly_stake = (edge / (odds - 1)) * risk_factor
    # Cap de seguridad del 5%
    stake_final = min(kelly_stake, 0.05) * bankroll
    return round(stake_final, 2), round(edge * 100, 2), round(kelly_stake * 100, 2)

def main():
    st.set_page_config(page_title="IA Betting PRO", layout="wide")
    st.title("⚽ Panel de Control de Bankroll")

    # 2. Sidebar - Gestión de Dinero
    st.sidebar.header("Configuración")
    if 'bank' not in st.session_state:
        st.session_state.bank = 100.0
    
    st.session_state.bank = st.sidebar.number_input("Bankroll Actual (€)", value=float(st.session_state.bank))
    risk = st.sidebar.slider("Nivel de Riesgo (Kelly)", 0.1, 0.5, 0.25)

    # 3. Partidos de Prueba (Datos limpios)
    st.subheader("Oportunidades de Hoy")
    partidos = [
        {"liga": "LaLiga 2", "partido": "Real Oviedo vs Sporting", "cuota": 2.30, "prob": 0.52},
        {"liga": "Premier", "partido": "Arsenal vs Chelsea", "cuota": 1.95, "prob": 0.62},
        {"liga": "LaLiga", "partido": "Sevilla vs Betis", "cuota": 3.20, "prob": 0.35}
    ]

    for p in partidos:
        stake, edge, k_pct = calculate_kelly(p['prob'], p['cuota'], st.session_state.bank, risk)
        
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            col1.write(f"**{p['partido']}**")
            col2.write(f"Cuota: {p['cuota']}")
            col3.write(f"Edge: {edge}%")
            
            if stake > 0:
                if col4.button(f"Apostar {stake}€", key=p['partido']):
                    st.session_state.bank -= stake
                    st.success(f"Apuesta registrada. Nuevo Bank: {st.session_state.bank}€")
                    st.rerun()
            else:
                col4.write("Sin valor")

    if st.sidebar.button("Resetear a 100€"):
        st.session_state.bank = 100.0
        st.rerun()

if __name__ == "__main__":
    main()
