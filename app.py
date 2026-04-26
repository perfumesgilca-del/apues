"""
Betting IA - App Completa Ready to Deploy
=======================================
Ejecutar: streamlit run app.py
Desplegar: Sube a GitHub + Streamlit Cloud

Funcionalidades:
- Bankroll 100€ con Kelly Criterion
- Simulación LaLiga + Premier + Segunda División
- Dashboard visual interactivo
"""

import streamlit as st
import random
import math
from datetime import datetime

st.set_page_config(
    page_title="Betting IA",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================
# CONFIGURACIÓN SIMPLE
# ================================================
class BettingApp:
    def __init__(self):
        self.risk_profiles = {
            "Conservador": {"kelly": 0.10, "max": 0.03},
            "Moderado": {"kelly": 0.25, "max": 0.05},
            "Agresivo": {"kelly": 0.50, "max": 0.08}
        }
        
        self.teams = {
            "Premier": [
                ("Arsenal", "ARS", 1825), ("Man City", "MCI", 1890), ("Liverpool", "LIV", 1850),
                ("Chelsea", "CHE", 1780), ("Man Utd", "MUN", 1765), ("Tottenham", "TOT", 1795),
                ("Newcastle", "NEW", 1745), ("West Ham", "WHU", 1710), ("Brighton", "BHA", 1745),
                ("Aston Villa", "AVL", 1710), ("Fulham", "FUL", 1715), ("Crystal Palace", "CRY", 1705)
            ],
            "LaLiga": [
                ("Real Madrid", "RMA", 1885), ("FC Barcelona", "FCB", 1850), ("Atlético Madrid", "ATM", 1800),
                ("Athletic Bilbao", "ATH", 1750), ("Real Sociedad", "RSO", 1720), ("Betis", "BET", 1700),
                ("Villarreal", "VLL", 1680), ("Sevilla", "SEV", 1720), ("Valencia", "VAL", 1650),
                ("Girona", "GIR", 1620), ("Celta Vigo", "CEL", 1600), ("Alavés", "ALV", 1580)
            ],
            "Segunda": [
                ("Leganés", "LEG", 1650), ("Eibar", "EIB", 1630), ("Espanyol", "ESP", 1680),
                ("Real Zaragoza", "ZAR", 1600), ("Burgos", "BUR", 1580), ("Levante", "LEV", 1620),
                ("Sporting Gijón", "SPO", 1550), ("Valladolid", "VAD", 1560), ("Albacete", "ALB", 1520),
                ("Racing Santander", "RAC", 1500), ("Málaga", "MAL", 1580), ("Mirandés", "MIR", 1540)
            ]
        }
        
        self.derbies = [
            ("Arsenal", "Tottenham"), ("Man City", "Man Utd"), ("Liverpool", "Everton"),
            ("Real Madrid", "FC Barcelona"), ("Sevilla", "Betis"), ("Atlético Madrid", "Real Madrid")
        ]
        
        self._init_session()
    
    def _init_session(self):
        if "bankroll" not in st.session_state:
            st.session_state.bankroll = 100.0
        if "initial_bankroll" not in st.session_state:
            st.session_state.initial_bankroll = 100.0
        if "risk_profile" not in st.session_state:
            st.session_state.risk_profile = "Moderado"
        if "bets" not in st.session_state:
            st.session_state.bets = []
        if "matches" not in st.session_state:
            st.session_state.matches = []
    
    def poisson(self, lamb, k):
        return (lamb ** k * math.exp(-lamb)) / math.factorial(k)
    
    def calculate_lambda(self, is_home, streak, injured, is_derby, league):
        base = random.uniform(1.2, 2.2)
        home_adv = 0.25 if league == "Segunda" else (0.15 if league == "LaLiga" else 0.12)
        lamb = (base + (home_adv if is_home else 0)) * (1.1 if is_home else 0.9)
        
        mult = 1.0
        if streak > 3: mult *= 1.10
        if injured: mult *= 0.85
        if is_derby: mult *= 0.95
        
        return lamb * mult
    
    def calculate_probs(self, lambda_home, lambda_away):
        home = draw = away = 0.0
        for h in range(6):
            for a in range(6):
                p = self.poisson(lambda_home, h) * self.poisson(lambda_away, a)
                if h > a: home += p
                elif h == a: draw += p
                else: away += p
        return {"home": home * 100, "draw": draw * 100, "away": away * 100}
    
    def calculate_kelly(self, probability, odds):
        profile = self.risk_profiles[st.session_state.risk_profile]
        kelly, max_pct = profile["kelly"], profile["max"]
        
        implied = (1 / odds) * 100
        edge = probability - implied
        
        if odds <= 1 or edge <= 0:
            return 0, edge, False, 0
        
        b = odds - 1
        p = probability / 100
        kelly_full = (b * p - (1 - p)) / b
        kelly_adj = kelly_full * kelly
        
        stake = st.session_state.bankroll * kelly_adj
        max_allowed = st.session_state.bankroll * max_pct
        
        cap = stake > max_allowed
        stake = min(stake, max_allowed)
        
        return stake, edge, cap, (stake / st.session_state.bankroll * 100) if st.session_state.bankroll > 0 else 0
    
    def simulate_match(self, league):
        teams = self.teams[league]
        team1, team2 = random.sample(teams, 2)
        
        streak1 = random.randint(0, 4)
        streak2 = random.randint(0, 4)
        injured1 = random.choice([True, False, False])
        injured2 = random.choice([True, False, False])
        is_derby = (team1[0], team2[0]) in self.derbies
        
        lambda1 = self.calculate_lambda(True, streak1, injured1, is_derby, league)
        lambda2 = self.calculate_lambda(False, streak2, injured2, is_derby, league)
        
        probs = self.calculate_probs(lambda1, lambda2)
        
        goals1 = int(sum([self.poisson(lambda1, i) * i for i in range(5)]))
        goals2 = int(sum([self.poisson(lambda2, i) * i for i in range(5)]))
        
        result = "home" if goals1 > goals2 else "away" if goals2 > goals1 else "draw"
        
        return {
            "league": league,
            "home": team1[0],
            "home_short": team1[1],
            "away": team2[0],
            "away_short": team2[1],
            "probs": probs,
            "result": result,
            "goals": f"{goals1}-{goals2}",
            "lambda_home": lambda1,
            "lambda_away": lambda2
        }
    
    def simulate_jornada(self):
        matches = []
        
        for _ in range(random.randint(3, 5)):
            league = random.choice(["Premier", "LaLiga", "Segunda"])
            matches.append(self.simulate_match(league))
        
        random.shuffle(matches)
        return matches
    
    def process_bets(self, matches):
        result_bets = []
        
        for match in matches:
            probs = match["probs"]
            pick = max(probs, key=probs.get)
            prob = probs[pick]
            
            base_odds = {"home": 2.1, "draw": 3.2, "away": 2.5}
            odds = base_odds[pick] + random.uniform(-0.4, 0.4)
            odds = round(max(1.4, min(odds, 5.0)), 2)
            
            stake, edge, cap, pct = self.calculate_kelly(prob[pick], odds)
            
            if stake > 1:
                won = match["result"] == pick
                profit = stake * (odds - 1) if won else -stake
                
                st.session_state.bankroll += profit
                
                bet = {
                    "id": len(st.session_state.bets) + 1,
                    "date": datetime.now().strftime("%H:%M"),
                    "league": match["league"],
                    "home": match["home_short"],
                    "away": match["away_short"],
                    "pick": pick,
                    "odds": odds,
                    "stake": stake,
                    "prob": prob,
                    "edge": edge,
                    "result": match["result"],
                    "profit": profit,
                    "won": won,
                    "cap": cap,
                    "pct": pct,
                    "goals": match["goals"]
                }
                
                result_bets.append(bet)
                st.session_state.bets.append(bet)
        
        return result_bets

app = BettingApp()

# ================================================
# INTERFAZ STREAMLIT
# ================================================
def main():
    st.title("⚽ Betting IA - Simulador")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Configuración")
        
        new_bankroll = st.number_input(
            "Bankroll Inicial (€)",
            value=float(st.session_state.initial_bankroll),
            min_value=10.0,
            step=50.0
        )
        
        if new_bankroll != st.session_state.initial_bankroll:
            st.session_state.initial_bankroll = new_bankroll
            st.session_state.bankroll = new_bankroll
            st.rerun()
        
        risk = st.selectbox(
            "Perfil de Riesgo",
            ["Conservador", "Moderado", "Agresivo"],
            index=["Conservador", "Moderado", "Agresivo"].index(st.session_state.risk_profile)
        )
        st.session_state.risk_profile = risk
        
        st.divider()
        
        st.metric(
            "💰 Bankroll Actual",
            f"€{st.session_state.bankroll:.2f}",
            f"{st.session_state.bankroll - st.session_state.initial_bankroll:+.2f}"
        )
        
        st.divider()
        
        if st.button("🎯 Simular Jornada", type="primary", use_container_width=True):
            matches = app.simulate_jornada()
            bets = app.process_bets(matches)
            st.session_state.matches = matches
            st.rerun()
        
        if st.button("🔄 Reiniciar Todo", use_container_width=True):
            st.session_state.bankroll = st.session_state.initial_bankroll
            st.session_state.bets = []
            st.session_state.matches = []
            st.rerun()
        
        st.divider()
        
        with st.expander("ℹ️ info"):
            st.markdown("""
            **Criterio de Kelly:**
            - Conservador: Kelly ×0.10 | Max 3%
            - Moderado: Kelly ×0.25 | Max 5%
            - Agresivo: Kelly ×0.50 | Max 8%
            
            **Ligas:**
            - Premier (12 equipos)
            - LaLiga (12 equipos)
            - Segunda (12 equipos)
            """)
    
    with col2:
        st.subheader("📋 Resultados")
        
        if st.session_state.bets:
            for i, bet in enumerate(reversed(st.session_state.bets[-10:])):
                emoji = "✅" if bet["won"] else "❌"
                cap_badge = " ⚠️" if bet["cap"] else ""
                
                with st.container():
                    c1, c2, c3 = st.columns([2, 2, 1])
                    
                    with c1:
                        st.markdown(f"**{bet['league'][:3]}** {bet['home']} vs {bet['away']}")
                        st.caption(f"{bet['date']} | {bet['goals']}")
                    
                    with c2:
                        st.markdown(f"**{bet['pick']}** @ {bet['odds']:.2f}{cap_badge}")
                        st.caption(f"{bet['prob']:.0f}% | Edge: {bet['edge']:.1f}%")
                    
                    with c3:
                        st.markdown(f"{emoji} **€{bet['profit']:+.2f}**")
                        st.caption(f"Stake: €{bet['stake']:.1f}")
                    
                    st.divider()
        else:
            st.info("👆 Pulsa 'Simular Jornada' para empezar")
    
    st.markdown("---")
    st.subheader("📈 Evolución")
    
    if st.session_state.bets:
        import pandas as pd
        
        df = pd.DataFrame(st.session_state.bets)
        df["cumulative"] = df["profit"].cumsum()
        df["bankroll"] = st.session_state.initial_bankroll + df["cumulative"]
        
        st.line_chart(df.set_index("id")["bankroll"])
        
        c1, c2, c3 = st.columns(3)
        
        total = len(df)
        wins = len(df[df["won"]])
        win_rate = (wins / total * 100) if total > 0 else 0
        profit = df["profit"].sum()
        
        with c1:
            st.metric("Apuestas", total)
        with c2:
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with c3:
            st.metric("Profit", f"€{profit:.2f}", delta=f"{profit:.2f}")
    
    else:
        st.info("No hay datos disponibles")
        
        st.subheader("📊 Guía rápida")
        
        st.markdown("""
        | Perfil | Kelly Frac | Max Stake | Riesgo |
        |--------|-----------|-----------|--------|
        | Conservador | 10% | 3% | Bajo |
        | Moderado | 25% | 5% | Medio |
        | Agresivo | 50% | 8% | Alto |
        """)
        
        st.markdown("""
        **Cómo funciona:**
        1. Pon tu bankroll inicial
        2. Selecciona tu perfil de riesgo  
        3. Pulsa "Simular Jornada"
        4. La IA genera partidos y calcula stakes
        5. ¡Observa tu profit en tiempo real!
        """)

if __name__ == "__main__":
    main()