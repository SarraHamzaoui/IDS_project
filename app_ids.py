import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import matplotlib.pyplot as plt

st.set_page_config(
    page_title=" IDS Intelligent - Dashboard SOC",
    page_icon="🛡️",
    layout="wide"
)

@st.cache_resource
def load_models():
    try:
        model = joblib.load('IDS_RandomForest_v1.pkl')
        scaler = joblib.load('IDS_Scaler_v1.pkl')
        return model, scaler
    except FileNotFoundError:
        st.error("ERREUR : Les fichiers .pkl sont introuvables. Vérifie qu'ils sont dans le même dossier que ce script.")
        return None, None

model, scaler = load_models()

st.title("Dashboard de Détection d'Intrusions (IDS)")
st.markdown("""
**Statut du système :** 🟢 ACTIF | **Modèle chargé :** Random Forest | **Seuil d'alerte :** 50%
""")
st.divider()

st.sidebar.header("Paramètres de Simulation")
speed = st.sidebar.slider("Vitesse du flux (paquets/sec)", 0.1, 2.0, 1.0)
run_simulation = st.sidebar.button("▶️ DÉMARRER LA SURVEILLANCE")

col1, col2, col3 = st.columns(3)
kpi_total = col1.empty()
kpi_normal = col2.empty()
kpi_attack = col3.empty()

st.subheader("📊 Monitoring du Trafic Réseau (Temps Réel)")
chart_placeholder = st.empty()

st.subheader("🚨 Journal des Alertes de Sécurité")
logs_placeholder = st.empty()

if run_simulation and model is not None:
    history_data = []
    history_labels = []
    logs = []
    
    count_total = 0
    count_attacks = 0
    
    for i in range(100): 
        time.sleep(1 / speed) 
        
        fake_packet = np.random.rand(1, 196) 
        
        if np.random.random() > 0.8: 
            fake_packet = fake_packet * 5
        
       
        packet_scaled = scaler.transform(fake_packet)
        prediction = model.predict(packet_scaled)[0]
        score_anomalie = model.predict_proba(packet_scaled)[0][1] 
        
        count_total += 1
        timestamp = time.strftime("%H:%M:%S")
        
        status = "Normal"
        color = "green"
        
        if prediction == 1:
            count_attacks += 1
            status = "🚨 ATTAQUE"
            color = "red"
            logs.insert(0, { 
                "Heure": timestamp,
                "ID Paquet": f"PKT-{1000+i}",
                "Score Anomalie": f"{score_anomalie*100:.2f}%",
                "Type Détecté": "Malveillant",
                "Action": "BLOQUÉ"
            })

        kpi_total.metric("Paquets Analysés", count_total)
        kpi_normal.metric("Trafic Légitime", count_total - count_attacks)
        kpi_attack.metric("Intrusions Détectées", count_attacks, delta_color="inverse")

        history_data.append(score_anomalie)
        if len(history_data) > 50:
            history_data.pop(0)
            
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(history_data, color='#00aaff', linewidth=2)
        ax.axhline(y=0.5, color='r', linestyle='--', label="Seuil d'alerte")  
        ax.set_ylim(0, 1)
        ax.set_title("Score d'Anomalie du Flux Actuel")
        ax.set_ylabel("Probabilité d'Attaque")
        ax.grid(True, alpha=0.3)
        chart_placeholder.pyplot(fig)
        plt.close(fig)

        if logs:
            df_logs = pd.DataFrame(logs)
            logs_placeholder.dataframe(df_logs.head(10), use_container_width=True)

    st.success("Simulation terminée. Le système IDS est en veille")

else:
    st.info("Cliquez sur 'DÉMARRER LA SURVEILLANCE' dans la barre latérale pour lancer le SIEM")