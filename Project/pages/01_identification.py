import streamlit as st
import pandas as pd
import pymysql
import os
 
# Configuration de la page
st.set_page_config(page_title="Dashboard Global", layout="wide", page_icon="📊")
st.logo("Africa.png", icon_image="Logo.png")

 
# Injecter le style CSS
st.markdown("""
    <style>
        .title {
            font-family: 'Arial', sans-serif;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
       
        .card {
            background-color: #f9f9f9;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            margin: 10px;
        }
        .card h2 {
            font-size: 2rem;
            margin: 0;
            color: #007BFF;
        }
        .card p {
            margin: 5px 0;
            font-size: 1.2rem;
            color: #555;
        }
       
    </style>
""", unsafe_allow_html=True)
 
 
# Using environment variables for security (set these in deployment)
DB_HOST = os.getenv("DB_HOST", "bjjvcnkquh3rdkwnqviv-mysql.services.clever-cloud.com")
DB_USER = os.getenv("DB_USER", "usbidjmhwyxcuar4")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tQemqKFD6orQ1DLz4Xrl")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "bjjvcnkquh3rdkwnqviv")

# Connexion à la base de données
try:
    mydb = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        database=DB_NAME
    )
    mycursor = mydb.cursor()
    st.success("✅ Connexion à la base de données réussie!")
except pymysql.MySQLError as err:
    st.error(f"❌ Erreur de connexion : {err}")
    

database="calibrage120"
# --- Cartes globales ---
st.markdown("<div class='title'>📊 Tableau de bord - Vue Globale</div>", unsafe_allow_html=True)
 
st.header("KPI Cards:")
# Récupération des données globales
def get_global_data():
    mycursor.execute("SELECT SUM(CA_Client) AS total_ca, COUNT(DISTINCT ID_Client) AS total_clients FROM client")
    data = mycursor.fetchone()
    mycursor.execute("SELECT COUNT(DISTINCT Id_Commercial) AS total_commerciaux FROM commercial")
    commerciaux = mycursor.fetchone()[0]
    return {"total_ca": data[0], "total_clients": data[1], "total_commerciaux": commerciaux}
 
global_data = get_global_data()
# Affichage des métriques
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
   
    with col1:
        st.markdown(f"""
            <div class="card">
                <h2>{round(global_data['total_ca']):,} €</h2>
                <p>Chiffre d'affaires total</p>
            </div>
        """, unsafe_allow_html=True)
 
    with col2:
        st.markdown(f"""
            <div class="card">
                <h2>{global_data['total_clients']:,}</h2>
                <p>Nombre de clients</p>
            </div>
        """, unsafe_allow_html=True)
 
    with col3:
        st.markdown(f"""
            <div class="card">
                <h2>{global_data['total_commerciaux']}</h2>
                <p>Nombre de commerciaux</p>
            </div>
        """, unsafe_allow_html=True)
 
 
 
 
# Fetch integrated data
def fetch_integrated_data():
    query = """
    SELECT
        c.Code_Client,
        c.Nom_Client,
        c.Region_Client,
        c.Ville_Client,
        c.Circuit_Client,
        c.Activite_Client,
        c.Potentiel_Client,
        c.Fidelisation_Client,
        c.CA_Client,
        cm.Nom_Commercial AS Commercial,
        `Solde_visite_terrain_client_par_an(Possibles)` AS Visits_Possible
    FROM
        client c
    LEFT JOIN visite v ON c.ID_Client = v.ID_Client
    LEFT JOIN commercial cm ON v.Id_Commercial = cm.Id_Commercial;
    """
    mycursor.execute(query)
    columns = [column[0] for column in mycursor.description]
    data = mycursor.fetchall()
    return pd.DataFrame(data, columns=columns)
 
# Load and display the integrated data
if mydb and mydb.open:
    st.header("Integrated Global Data View")
    df = fetch_integrated_data()
    st.dataframe(df)
 
 
 
 
 
# Afficher les DataFrames pour chaque catégorie
st.header("Analyse des Clients par Catégorie")
 
# Fonction pour récupérer les données
def fetch_data_with_percentage(query):
    mycursor.execute(query)
    columns = [column[0] for column in mycursor.description]
    data = mycursor.fetchall()
    df = pd.DataFrame(data, columns=columns)

    # Calculer le pourcentage
    total_ca = df['Chiffre_d_Affaires'].sum()
    if total_ca > 0:
        df['Pourcentage'] = (df['Chiffre_d_Affaires'] / total_ca * 100).round(2)
        df['Pourcentage'] = df['Pourcentage'].apply(lambda x: f"{x} %")  # Ajout de l'icône %
    else:
        df['Pourcentage'] = "0 %"

    return df
 
 
# Colonnes pour afficher les données
col1, col2 = st.columns(2)
 
with col1:
    # 1. Nombre de clients par potentiel client
    query_potentiel = """
    SELECT
        c.Potentiel_Client,
        COUNT(c.ID_Client) AS Nombre_Clients,
        SUM(c.CA_Client) AS Chiffre_d_Affaires
    FROM client c
    LEFT JOIN visite v ON c.ID_Client = v.ID_Client
    GROUP BY c.Potentiel_Client
    """
    df_potentiel = fetch_data_with_percentage(query_potentiel)
    df_potentiel = df_potentiel.sort_values(by="Nombre_Clients", ascending=False)
    st.subheader("Nombre de clients par Potentiel Client")
    st.dataframe(df_potentiel)
 
with col2:
    # 2. Nombre de clients par CA Client (Couches)
    query_ca = """
    SELECT
        c.Couche,
        COUNT(c.ID_Client) AS Nombre_Clients,
        SUM(c.CA_Client) AS Chiffre_d_Affaires
    FROM client c
    LEFT JOIN visite v ON c.ID_Client = v.ID_Client
    GROUP BY c.Couche
    """
    df_ca = fetch_data_with_percentage(query_ca)
    df_ca = df_ca.sort_values(by="Couche", ascending=True)
    st.subheader("Nombre de clients par Couches")
    st.dataframe(df_ca)
 
col1, col2 = st.columns(2)
 
with col1:
    # 3. Nombre de clients par type de fidélisation client
    query_fidelisation = """
    SELECT
        c.Fidelisation_Client,
        COUNT(c.ID_Client) AS Nombre_Clients,
        SUM(c.CA_Client) AS Chiffre_d_Affaires
    FROM client c
    LEFT JOIN visite v ON c.ID_Client = v.ID_Client
    GROUP BY c.Fidelisation_Client
    """
    df_fidelisation = fetch_data_with_percentage(query_fidelisation)
    df_fidelisation = df_fidelisation.sort_values(by="Nombre_Clients", ascending=False)
    st.subheader("Nombre de clients par Type de Fidélisation")
    st.dataframe(df_fidelisation)
 
with col2:
    # 5. Nombre de clients par Circuit
    query_circuit = """
    SELECT
        c.Circuit_Client,
        COUNT(c.ID_Client) AS Nombre_Clients,
        SUM(c.CA_Client) AS Chiffre_d_Affaires
    FROM client c
    LEFT JOIN visite v ON c.ID_Client = v.ID_Client
    GROUP BY c.Circuit_Client
    """
    df_circuit = fetch_data_with_percentage(query_circuit)
    df_circuit = df_circuit.sort_values(by="Nombre_Clients", ascending=False)
    st.subheader("Nombre de clients par Circuit")
    st.dataframe(df_circuit)
 
 
# 4. Nombre de clients par Pays
query_pays = """
SELECT
    c.Pays_Client AS Pays,
    COUNT(c.ID_Client) AS Nombre_Clients,
    COUNT(DISTINCT v.Id_Commercial) AS Nombre_Commerciaux,
    SUM(c.CA_Client) AS Chiffre_d_Affaires
FROM client c
LEFT JOIN visite v ON c.ID_Client = v.ID_Client
GROUP BY c.Pays_Client
ORDER BY Nombre_Clients DESC
"""
df_pays = fetch_data_with_percentage(query_pays)
df_pays = df_pays.sort_values(by="Nombre_Clients", ascending=False)
 
# Ajouter le formatage pour "Chiffre_d_Affaires"
df_pays["Chiffre_d_Affaires"] = df_pays["Chiffre_d_Affaires"].apply(lambda x: f"{x:,.2f} €")
 
st.subheader("Distribution des Clients / Commerciaux / Chiffre d'affaires par Pays")
st.dataframe(df_pays)