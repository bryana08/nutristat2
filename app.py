import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NutriStat — Habitudes Alimentaires",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --primary: #2D6A4F;
    --secondary: #52B788;
    --accent: #F4A261;
    --bg: #F8F5F0;
    --card: #FFFFFF;
    --text: #1B1B1B;
    --muted: #6B7280;
    --border: #E5E0D8;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.main { background-color: var(--bg); }

/* Hero Header */
.hero {
    background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 50%, #40916C 100%);
    padding: 3rem 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(82,183,136,0.3) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 900;
    color: #FFFFFF;
    margin: 0;
    line-height: 1.1;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.8);
    margin-top: 0.5rem;
    font-weight: 300;
}
.hero-badge {
    display: inline-block;
    background: rgba(244,162,97,0.9);
    color: white;
    padding: 0.3rem 1rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 1rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Cards */
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--primary);
    line-height: 1;
}
.stat-label {
    font-size: 0.85rem;
    color: var(--muted);
    margin-top: 0.3rem;
    font-weight: 500;
}

/* Section titles */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--primary);
    border-left: 4px solid var(--accent);
    padding-left: 1rem;
    margin: 2rem 0 1rem 0;
}

/* Form styling */
.form-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

/* Success / warning banners */
.success-banner {
    background: linear-gradient(135deg, #D8F3DC, #B7E4C7);
    border: 1px solid #52B788;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #1B4332;
    font-weight: 500;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B4332 0%, #2D6A4F 100%);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: white !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2D6A4F, #40916C);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 2rem;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(45,106,79,0.3);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(45,106,79,0.4);
}

/* Metric override */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
}

.footer {
    text-align: center;
    padding: 2rem;
    color: var(--muted);
    font-size: 0.85rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA STORAGE (Google Sheets or local CSV fallback) ───────────────────────
DATA_FILE = "nutristat_data.csv"

COLUMNS = [
    "timestamp", "age", "sexe", "poids_kg", "taille_cm", "imc",
    "activite_physique", "nb_repas_jour", "petit_dejeuner",
    "consommation_fruits_legumes", "consommation_eau_litres",
    "consommation_fastfood_semaine", "consommation_sucre",
    "consommation_alcool", "allergies", "regime_alimentaire",
    "satisfaction_alimentation", "problemes_sante", "ville", "niveau_etudes"
]

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        return df
    else:
        return pd.DataFrame(columns=COLUMNS)

def save_data(new_row: dict):
    df = load_data()
    new_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def compute_imc(poids, taille_cm):
    taille_m = taille_cm / 100
    return round(poids / (taille_m ** 2), 1)

def imc_categorie(imc):
    if imc < 18.5:
        return "Insuffisance pondérale", "#3B82F6"
    elif imc < 25:
        return "Poids normal", "#10B981"
    elif imc < 30:
        return "Surpoids", "#F59E0B"
    else:
        return "Obésité", "#EF4444"

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥗 NutriStat")
    st.markdown("*Analyse des Habitudes Alimentaires*")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Accueil", "📋 Formulaire de collecte", "📊 Tableau de bord analytique", "📥 Export des données"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    df_sidebar = load_data()
    st.markdown(f"**{len(df_sidebar)}** réponses collectées")
    st.markdown("---")
    st.markdown("**INF 232 — EC2**")
    st.markdown("Analyse de données")
    st.markdown("*TP N°1 — 2026*")

# ─── PAGE: ACCUEIL ─────────────────────────────────────────────────────────────
if page == "🏠 Accueil":
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">🎓 INF 232 EC2 — TP N°1</div>
        <h1 class="hero-title">NutriStat</h1>
        <p class="hero-subtitle">Collecte & Analyse Descriptive des Habitudes Alimentaires</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    df = load_data()
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(df)}</div>
            <div class="stat-label">Réponses collectées</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        moy_imc = round(df["imc"].mean(), 1) if len(df) > 0 and "imc" in df.columns and not df["imc"].isna().all() else "—"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{moy_imc}</div>
            <div class="stat-label">IMC moyen</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        moy_age = round(df["age"].mean(), 1) if len(df) > 0 and "age" in df.columns and not df["age"].isna().all() else "—"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{moy_age}</div>
            <div class="stat-label">Âge moyen</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title">À propos de NutriStat</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **NutriStat** est une application web de collecte et d'analyse descriptive
        des habitudes alimentaires. Elle permet de :

        - 📋 **Collecter** des données nutritionnelles via un formulaire structuré
        - 📊 **Analyser** statistiquement les données recueillies
        - 📈 **Visualiser** les tendances et distributions
        - 📥 **Exporter** les données pour analyses avancées

        > Développée dans le cadre du **TP N°1 d'INF 232 EC2** — Analyse de données.
        """)

    with col2:
        st.markdown("""
        **Données collectées :**

        | Catégorie | Variables |
        |-----------|-----------|
        | 👤 Profil | Âge, sexe, poids, taille, IMC |
        | 🥦 Alimentation | Repas, fruits, eau, fast-food |
        | 🏃 Mode de vie | Activité physique, régime |
        | 🏥 Santé | Problèmes, allergies |
        | 📍 Contexte | Ville, niveau d'études |
        """)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #D8F3DC, #B7E4C7); border-radius: 12px; padding: 1.2rem 1.5rem; border-left: 4px solid #2D6A4F; margin-top: 1rem;">
        <strong>👈 Commencez par remplir le formulaire</strong> dans la barre latérale gauche,
        puis consultez le tableau de bord pour voir les analyses en temps réel !
    </div>
    """, unsafe_allow_html=True)

# ─── PAGE: FORMULAIRE ──────────────────────────────────────────────────────────
elif page == "📋 Formulaire de collecte":
    st.markdown('<div class="section-title">📋 Formulaire de Collecte</div>', unsafe_allow_html=True)
    st.markdown("Remplissez ce formulaire pour contribuer à l'étude sur les habitudes alimentaires.")

    with st.form("collecte_form", clear_on_submit=True):
        st.markdown("#### 👤 Informations personnelles")
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Âge (ans)", min_value=10, max_value=100, value=22)
        with col2:
            sexe = st.selectbox("Sexe", ["Masculin", "Féminin", "Autre / Préfère ne pas répondre"])
        with col3:
            niveau_etudes = st.selectbox("Niveau d'études", [
                "Primaire", "Secondaire", "Baccalauréat", "Licence", "Master", "Doctorat", "Autre"
            ])

        col1, col2, col3 = st.columns(3)
        with col1:
            poids = st.number_input("Poids (kg)", min_value=30.0, max_value=200.0, value=65.0, step=0.5)
        with col2:
            taille = st.number_input("Taille (cm)", min_value=100, max_value=220, value=170)
        with col3:
            ville = st.text_input("Ville de résidence", placeholder="ex: Kinshasa")

        imc_val = compute_imc(poids, taille)
        imc_cat, imc_color = imc_categorie(imc_val)
        st.markdown(f"**IMC calculé :** `{imc_val}` — <span style='color:{imc_color};font-weight:600'>{imc_cat}</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🥦 Habitudes alimentaires")

        col1, col2 = st.columns(2)
        with col1:
            nb_repas = st.selectbox("Nombre de repas par jour", [1, 2, 3, 4, 5, "Plus de 5"])
            petit_dej = st.selectbox("Prenez-vous le petit-déjeuner ?", [
                "Toujours", "Souvent", "Parfois", "Rarement", "Jamais"
            ])
            fruits_legumes = st.selectbox("Consommation de fruits & légumes / jour", [
                "0 portion", "1 portion", "2 portions", "3 portions", "4 portions", "5 portions et plus"
            ])
            eau = st.slider("Consommation d'eau (litres/jour)", 0.0, 5.0, 1.5, 0.25)

        with col2:
            fastfood = st.selectbox("Fast-food / semaine", [
                "Jamais", "1 fois", "2-3 fois", "4-5 fois", "Tous les jours"
            ])
            sucre = st.selectbox("Consommation de sucre", [
                "Très faible", "Faible", "Modérée", "Élevée", "Très élevée"
            ])
            alcool = st.selectbox("Consommation d'alcool", [
                "Jamais", "Occasionnellement", "1-2 fois/semaine", "Tous les jours"
            ])
            regime = st.selectbox("Régime alimentaire", [
                "Omnivore", "Végétarien", "Végétalien", "Sans gluten", "Halal", "Autre"
            ])

        st.markdown("---")
        st.markdown("#### 🏃 Mode de vie & Santé")

        col1, col2 = st.columns(2)
        with col1:
            activite = st.selectbox("Activité physique", [
                "Sédentaire (aucune)", "Légère (1-2 fois/semaine)",
                "Modérée (3-4 fois/semaine)", "Intense (5+ fois/semaine)"
            ])
            satisfaction = st.slider("Satisfaction envers votre alimentation (1-10)", 1, 10, 6)

        with col2:
            problemes = st.multiselect("Problèmes de santé liés à l'alimentation", [
                "Diabète", "Hypertension", "Cholestérol élevé", "Anémie",
                "Troubles digestifs", "Allergies alimentaires", "Aucun"
            ], default=["Aucun"])
            allergies = st.text_input("Allergies alimentaires", placeholder="ex: arachides, lactose...")

        st.markdown("---")
        submitted = st.form_submit_button("✅ Soumettre mes données", use_container_width=True)

        if submitted:
            row = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "age": age,
                "sexe": sexe,
                "poids_kg": poids,
                "taille_cm": taille,
                "imc": imc_val,
                "activite_physique": activite,
                "nb_repas_jour": str(nb_repas),
                "petit_dejeuner": petit_dej,
                "consommation_fruits_legumes": fruits_legumes,
                "consommation_eau_litres": eau,
                "consommation_fastfood_semaine": fastfood,
                "consommation_sucre": sucre,
                "consommation_alcool": alcool,
                "allergies": allergies if allergies else "Aucune",
                "regime_alimentaire": regime,
                "satisfaction_alimentation": satisfaction,
                "problemes_sante": ", ".join(problemes) if problemes else "Aucun",
                "ville": ville if ville else "Non renseignée",
                "niveau_etudes": niveau_etudes
            }
            save_data(row)
            st.success("✅ Merci ! Vos données ont été enregistrées avec succès.")
            st.balloons()

# ─── PAGE: TABLEAU DE BORD ─────────────────────────────────────────────────────
elif page == "📊 Tableau de bord analytique":
    st.markdown('<div class="section-title">📊 Tableau de Bord Analytique</div>', unsafe_allow_html=True)

    df = load_data()

    if len(df) == 0:
        st.warning("⚠️ Aucune donnée disponible. Remplissez d'abord le formulaire de collecte.")
        st.stop()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Répondants", len(df))
    with col2:
        st.metric("📊 Âge moyen", f"{df['age'].mean():.1f} ans")
    with col3:
        st.metric("⚖️ IMC moyen", f"{df['imc'].mean():.1f}")
    with col4:
        st.metric("💧 Eau/jour (moy.)", f"{df['consommation_eau_litres'].mean():.1f} L")

    st.markdown("---")

    # ── Section 1 : Profil démographique ──────────────────────────────────────
    st.markdown("### 👤 Profil Démographique")
    col1, col2 = st.columns(2)

    with col1:
        fig_sexe = px.pie(
            df, names="sexe", title="Répartition par sexe",
            color_discrete_sequence=["#2D6A4F", "#52B788", "#B7E4C7"],
            hole=0.45
        )
        fig_sexe.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_sexe, use_container_width=True)

    with col2:
        fig_age = px.histogram(
            df, x="age", nbins=15, title="Distribution de l'âge",
            color_discrete_sequence=["#40916C"]
        )
        fig_age.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               xaxis_title="Âge", yaxis_title="Fréquence")
        st.plotly_chart(fig_age, use_container_width=True)

    # ── Section 2 : IMC & Santé ────────────────────────────────────────────────
    st.markdown("### ⚖️ IMC & Santé")
    col1, col2 = st.columns(2)

    with col1:
        # IMC categories
        df["categorie_imc"] = df["imc"].apply(lambda x: imc_categorie(x)[0])
        imc_counts = df["categorie_imc"].value_counts().reset_index()
        imc_counts.columns = ["Catégorie", "Nombre"]
        color_map = {
            "Insuffisance pondérale": "#3B82F6",
            "Poids normal": "#10B981",
            "Surpoids": "#F59E0B",
            "Obésité": "#EF4444"
        }
        fig_imc = px.bar(
            imc_counts, x="Catégorie", y="Nombre",
            title="Répartition IMC",
            color="Catégorie",
            color_discrete_map=color_map
        )
        fig_imc.update_layout(paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig_imc, use_container_width=True)

    with col2:
        fig_scatter = px.scatter(
            df, x="taille_cm", y="poids_kg", color="sexe",
            title="Relation Taille / Poids",
            size="imc", hover_data=["age", "imc"],
            color_discrete_sequence=["#2D6A4F", "#F4A261", "#94A3B8"]
        )
        fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Section 3 : Habitudes alimentaires ────────────────────────────────────
    st.markdown("### 🥦 Habitudes Alimentaires")
    col1, col2 = st.columns(2)

    with col1:
        ff_counts = df["consommation_fastfood_semaine"].value_counts().reset_index()
        ff_counts.columns = ["Fréquence", "Nombre"]
        fig_ff = px.bar(
            ff_counts, x="Fréquence", y="Nombre",
            title="Consommation de Fast-Food",
            color_discrete_sequence=["#F4A261"]
        )
        fig_ff.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_ff, use_container_width=True)

    with col2:
        fig_eau = px.histogram(
            df, x="consommation_eau_litres", nbins=10,
            title="Distribution Consommation d'Eau (L/jour)",
            color_discrete_sequence=["#4CC9F0"]
        )
        fig_eau.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_eau, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig_petitdej = px.pie(
            df, names="petit_dejeuner",
            title="Fréquence du Petit-Déjeuner",
            color_discrete_sequence=px.colors.sequential.Greens_r,
            hole=0.4
        )
        fig_petitdej.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_petitdej, use_container_width=True)

    with col2:
        fig_regime = px.pie(
            df, names="regime_alimentaire",
            title="Types de Régimes Alimentaires",
            color_discrete_sequence=["#2D6A4F","#40916C","#52B788","#74C69D","#95D5B2","#B7E4C7"],
            hole=0.4
        )
        fig_regime.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_regime, use_container_width=True)

    # ── Section 4 : Mode de vie ────────────────────────────────────────────────
    st.markdown("### 🏃 Mode de Vie")
    col1, col2 = st.columns(2)

    with col1:
        act_counts = df["activite_physique"].value_counts().reset_index()
        act_counts.columns = ["Activité", "Nombre"]
        fig_act = px.bar(
            act_counts, x="Nombre", y="Activité", orientation="h",
            title="Niveaux d'Activité Physique",
            color_discrete_sequence=["#2D6A4F"]
        )
        fig_act.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_act, use_container_width=True)

    with col2:
        fig_sat = px.histogram(
            df, x="satisfaction_alimentation", nbins=10,
            title="Satisfaction envers l'Alimentation",
            color_discrete_sequence=["#52B788"]
        )
        fig_sat.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                               xaxis_title="Score (1-10)", yaxis_title="Fréquence")
        st.plotly_chart(fig_sat, use_container_width=True)

    # ── Section 5 : Statistiques descriptives ─────────────────────────────────
    st.markdown("### 📐 Statistiques Descriptives")
    num_cols = ["age", "poids_kg", "taille_cm", "imc", "consommation_eau_litres",
                "satisfaction_alimentation"]
    desc = df[num_cols].describe().round(2)
    desc.index = ["Effectif", "Moyenne", "Écart-type", "Min", "Q1 (25%)", "Médiane", "Q3 (75%)", "Max"]
    st.dataframe(desc, use_container_width=True)

    # Corrélation
    st.markdown("#### 🔗 Matrice de Corrélation")
    corr = df[num_cols].corr().round(2)
    fig_corr = px.imshow(
        corr, text_auto=True, aspect="auto",
        color_continuous_scale="RdYlGn",
        title="Corrélations entre variables numériques"
    )
    fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_corr, use_container_width=True)

# ─── PAGE: EXPORT ──────────────────────────────────────────────────────────────
elif page == "📥 Export des données":
    st.markdown('<div class="section-title">📥 Export des Données</div>', unsafe_allow_html=True)

    df = load_data()

    if len(df) == 0:
        st.warning("⚠️ Aucune donnée à exporter. Remplissez d'abord le formulaire.")
    else:
        st.success(f"✅ **{len(df)} entrées** disponibles pour l'export.")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Télécharger les données (CSV)",
            data=csv,
            file_name=f"nutristat_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("#### 📊 Résumé rapide")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"- **Répondants total :** {len(df)}")
            st.markdown(f"- **Âge moyen :** {df['age'].mean():.1f} ans")
            st.markdown(f"- **IMC moyen :** {df['imc'].mean():.1f}")
            st.markdown(f"- **% Femmes :** {(df['sexe']=='Féminin').mean()*100:.1f}%")
        with col2:
            st.markdown(f"- **Eau/jour moy. :** {df['consommation_eau_litres'].mean():.1f} L")
            st.markdown(f"- **Satisfaction moy. :** {df['satisfaction_alimentation'].mean():.1f}/10")
            st.markdown(f"- **% Petit-déj. toujours :** {(df['petit_dejeuner']=='Toujours').mean()*100:.1f}%")
            st.markdown(f"- **Première réponse :** {df['timestamp'].min()[:10] if len(df) > 0 else '—'}")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    🥗 <strong>NutriStat</strong> — Application de Collecte & Analyse Descriptive des Habitudes Alimentaires<br>
    INF 232 EC2 · TP N°1 · 2026 · Développé avec Python & Streamlit
</div>
""", unsafe_allow_html=True)
