import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(
    page_title="NutriStat",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #F8F5F0; }
.hero { background: linear-gradient(135deg, #1B4332, #2D6A4F, #40916C); padding: 2.5rem 2rem; border-radius: 20px; margin-bottom: 2rem; }
.hero-title { font-family: 'Playfair Display', serif; font-size: 2.8rem; font-weight: 900; color: white; margin: 0; }
.hero-sub { color: rgba(255,255,255,0.8); margin-top: 0.5rem; }
.hero-badge { background: rgba(244,162,97,0.9); color: white; padding: 0.3rem 1rem; border-radius: 50px; font-size: 0.8rem; font-weight: 600; margin-bottom: 1rem; display: inline-block; text-transform: uppercase; }
.card { background: white; border-radius: 16px; padding: 1.5rem; text-align: center; border: 1px solid #E5E0D8; }
.card-num { font-family: 'Playfair Display', serif; font-size: 2.5rem; font-weight: 700; color: #2D6A4F; }
.card-lab { font-size: 0.85rem; color: #6B7280; margin-top: 0.3rem; }
.stButton > button { background: linear-gradient(135deg, #2D6A4F, #40916C); color: white; border: none; border-radius: 10px; font-weight: 600; font-size: 1rem; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1B4332, #2D6A4F); }
[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "data.csv"
COLS = ["timestamp","age","sexe","poids_kg","taille_cm","imc","activite",
        "nb_repas","petit_dej","fruits_legumes","eau_litres","fastfood",
        "sucre","alcool","allergies","regime","satisfaction","problemes",
        "ville","niveau_etudes"]

def load():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=COLS)

def save(row):
    df = load()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def imc(p, t): return round(p / (t/100)**2, 1)

def imc_cat(v):
    if v < 18.5: return "Insuffisance pondérale", "#3B82F6"
    elif v < 25: return "Poids normal", "#10B981"
    elif v < 30: return "Surpoids", "#F59E0B"
    else: return "Obésité", "#EF4444"

with st.sidebar:
    st.markdown("## 🥗 NutriStat")
    st.markdown("*Habitudes Alimentaires*")
    st.markdown("---")
    page = st.radio("", ["🏠 Accueil","📋 Formulaire","📊 Dashboard","📥 Export"])
    st.markdown("---")
    df0 = load()
    st.markdown(f"**{len(df0)}** réponses")
    st.markdown("---")
    st.markdown("**INF 232 EC2 · TP N°1**")

if page == "🏠 Accueil":
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">🎓 INF 232 EC2 — TP N°1</div>
        <div class="hero-title">NutriStat</div>
        <div class="hero-sub">Collecte & Analyse des Habitudes Alimentaires</div>
    </div>
    """, unsafe_allow_html=True)
    df = load()
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(f'<div class="card"><div class="card-num">{len(df)}</div><div class="card-lab">Réponses</div></div>', unsafe_allow_html=True)
    with c2:
        v = round(df["imc"].mean(),1) if len(df)>0 else "—"
        st.markdown(f'<div class="card"><div class="card-num">{v}</div><div class="card-lab">IMC moyen</div></div>', unsafe_allow_html=True)
    with c3:
        v = round(df["age"].mean(),1) if len(df)>0 else "—"
        st.markdown(f'<div class="card"><div class="card-num">{v}</div><div class="card-lab">Âge moyen</div></div>', unsafe_allow_html=True)
    st.markdown("### À propos")
    st.markdown("**NutriStat** collecte et analyse les habitudes alimentaires via un formulaire structuré et génère des statistiques descriptives en temps réel.")

elif page == "📋 Formulaire":
    st.markdown("## 📋 Formulaire de Collecte")
    with st.form("f", clear_on_submit=True):
        st.markdown("#### 👤 Profil")
        c1,c2,c3 = st.columns(3)
        with c1: age = st.number_input("Âge", 10, 100, 22)
        with c2: sexe = st.selectbox("Sexe", ["Masculin","Féminin","Autre"])
        with c3: niveau = st.selectbox("Niveau d'études", ["Primaire","Secondaire","Baccalauréat","Licence","Master","Doctorat","Autre"])
        c1,c2,c3 = st.columns(3)
        with c1: poids = st.number_input("Poids (kg)", 30.0, 200.0, 65.0, 0.5)
        with c2: taille = st.number_input("Taille (cm)", 100, 220, 170)
        with c3: ville = st.text_input("Ville", placeholder="ex: Kinshasa")
        v_imc = imc(poids, taille)
        cat, col = imc_cat(v_imc)
        st.markdown(f"**IMC:** `{v_imc}` — <span style='color:{col};font-weight:600'>{cat}</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### 🥦 Alimentation")
        c1,c2 = st.columns(2)
        with c1:
            nb = st.selectbox("Repas/jour", [1,2,3,4,5,"5+"])
            pdej = st.selectbox("Petit-déjeuner", ["Toujours","Souvent","Parfois","Rarement","Jamais"])
            fruits = st.selectbox("Fruits & légumes/jour", ["0","1 portion","2 portions","3 portions","4 portions","5+"])
            eau = st.slider("Eau (L/jour)", 0.0, 5.0, 1.5, 0.25)
        with c2:
            ff = st.selectbox("Fast-food/semaine", ["Jamais","1 fois","2-3 fois","4-5 fois","Tous les jours"])
            sucre = st.selectbox("Sucre", ["Très faible","Faible","Modérée","Élevée","Très élevée"])
            alcool = st.selectbox("Alcool", ["Jamais","Occasionnellement","1-2x/semaine","Tous les jours"])
            regime = st.selectbox("Régime", ["Omnivore","Végétarien","Végétalien","Sans gluten","Halal","Autre"])
        st.markdown("---")
        st.markdown("#### 🏃 Mode de vie")
        c1,c2 = st.columns(2)
        with c1:
            act = st.selectbox("Activité physique", ["Sédentaire","Légère","Modérée","Intense"])
            sat = st.slider("Satisfaction alimentation (1-10)", 1, 10, 6)
        with c2:
            prob = st.multiselect("Problèmes de santé", ["Diabète","Hypertension","Cholestérol","Anémie","Troubles digestifs","Aucun"], default=["Aucun"])
            allerg = st.text_input("Allergies", placeholder="ex: lactose")
        submitted = st.form_submit_button("✅ Soumettre", use_container_width=True)
        if submitted:
            save({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  "age": age, "sexe": sexe, "poids_kg": poids, "taille_cm": taille,
                  "imc": v_imc, "activite": act, "nb_repas": str(nb),
                  "petit_dej": pdej, "fruits_legumes": fruits, "eau_litres": eau,
                  "fastfood": ff, "sucre": sucre, "alcool": alcool,
                  "allergies": allerg or "Aucune", "regime": regime,
                  "satisfaction": sat, "problemes": ", ".join(prob),
                  "ville": ville or "—", "niveau_etudes": niveau})
            st.success("✅ Données enregistrées !")
            st.balloons()

elif page == "📊 Dashboard":
    st.markdown("## 📊 Tableau de Bord")
    df = load()
    if len(df) == 0:
        st.warning("Aucune donnée. Remplissez le formulaire d'abord.")
        st.stop()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("👥 Répondants", len(df))
    c2.metric("📊 Âge moyen", f"{df['age'].mean():.1f} ans")
    c3.metric("⚖️ IMC moyen", f"{df['imc'].mean():.1f}")
    c4.metric("💧 Eau/jour", f"{df['eau_litres'].mean():.1f} L")
    st.markdown("---")
    st.markdown("### 👤 Démographie")
    c1,c2 = st.columns(2)
    with c1:
        fig = px.pie(df, names="sexe", title="Répartition par sexe", hole=0.45, color_discrete_sequence=["#2D6A4F","#52B788","#B7E4C7"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(df, x="age", nbins=15, title="Distribution de l'âge", color_discrete_sequence=["#40916C"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### ⚖️ IMC")
    c1,c2 = st.columns(2)
    with c1:
        df["cat_imc"] = df["imc"].apply(lambda x: imc_cat(x)[0])
        cnt = df["cat_imc"].value_counts().reset_index()
        cnt.columns = ["Catégorie","Nombre"]
        fig = px.bar(cnt, x="Catégorie", y="Nombre", title="Catégories IMC", color="Catégorie",
                     color_discrete_map={"Insuffisance pondérale":"#3B82F6","Poids normal":"#10B981","Surpoids":"#F59E0B","Obésité":"#EF4444"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.scatter(df, x="taille_cm", y="poids_kg", color="sexe", size="imc", title="Taille vs Poids")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### 🥦 Alimentation")
    c1,c2 = st.columns(2)
    with c1:
        fig = px.pie(df, names="petit_dej", title="Petit-Déjeuner", hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(df, x="eau_litres", nbins=10, title="Eau (L/jour)", color_discrete_sequence=["#4CC9F0"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### 📐 Statistiques Descriptives")
    num = ["age","poids_kg","taille_cm","imc","eau_litres","satisfaction"]
    desc = df[num].describe().round(2)
    desc.index = ["Effectif","Moyenne","Écart-type","Min","Q1","Médiane","Q3","Max"]
    st.dataframe(desc, use_container_width=True)
    st.markdown("### 🔗 Corrélations")
    fig = px.imshow(df[num].corr().round(2), text_auto=True, color_continuous_scale="RdYlGn")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif page == "📥 Export":
    st.markdown("## 📥 Export des Données")
    df = load()
    if len(df) == 0:
        st.warning("Aucune donnée à exporter.")
    else:
        st.success(f"✅ {len(df)} entrées disponibles.")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Télécharger CSV", csv, f"nutristat_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)

st.markdown("---")
st.markdown("<center>🥗 <b>NutriStat</b> · INF 232 EC2 · TP N°1 · 2026</center>", unsafe_allow_html=True)

