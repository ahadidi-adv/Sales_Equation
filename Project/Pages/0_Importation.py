import streamlit as st
import pandas as pd
import pymysql
from pymysql import Error
import io
st.set_page_config(page_title="Importation", page_icon="🔗")
st.logo("Africa.png", icon_image="Logo.png")

def create_connection():
    """Create a database connection to a MySQL database."""
    connection = None
    try:
        connection = pymysql.connect(
            host='bjjvcnkquh3rdkwnqviv-mysql.services.clever-cloud.com',
            user='usbidjmhwyxcuar4',
            password='tQemqKFD6orQ1DLz4Xrl',
            port=3306,
            database='bjjvcnkquh3rdkwnqviv',
            #connection_timeout=600,  # Timeout de 10 minutes
            #autocommit=True          # Active la reconnexion automatique
        )
        if connection.is_connected():
            st.success("Connected to the database")
    except Error as e:
        st.error(f"The error '{e}' occurred")
    return connection

def get_existing_ids(connection, table_name, id_column):
    cursor = connection.cursor()
    query = f"SELECT {id_column} FROM {table_name}"
    cursor.execute(query)
    existing_ids = set(row[0] for row in cursor.fetchall())
    cursor.close()
    return existing_ids

def clear_all_data(connection):
    """Supprime toutes les données des tables pour un nouvel import."""
    cursor = connection.cursor()
    tables = ['visite', 'client', 'commercial', 'chef_de_marche']
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    connection.commit()
    cursor.close()
    st.success("Toutes les données existantes ont été supprimées.")
 
def insert_data(connection, df, batch_size=1000):
    cursor = connection.cursor()

    def replace_nan(value):
        return None if pd.isna(value) else value

    # Insertion des chefs de marché
    existing_chefs = get_existing_ids(connection, 'chef_de_marche', 'ID_Chef_de_Marche')
    chef_de_marche_query = """
    INSERT IGNORE INTO chef_de_marche (ID_Chef_de_Marche, Chef_de_Marche)
    VALUES (%s, %s)
    """
    chef_de_marche_data = [
        (replace_nan(row['Code Chef de marché']), replace_nan(row['4-Chef de marché']))
        for _, row in df.drop_duplicates(subset=['Code Chef de marché']).iterrows()
        if replace_nan(row['Code Chef de marché']) not in existing_chefs
    ]

    for i in range(0, len(chef_de_marche_data), batch_size):
        cursor.executemany(chef_de_marche_query, chef_de_marche_data[i:i + batch_size])
    st.success(f"{len(chef_de_marche_data)} nouveaux chefs de marché insérés.")

    # Insertion dans commercial
    commercial_query = """
    INSERT IGNORE INTO commercial (
        Id_Commercial, Nom_Commercial, ID_Chef_de_Marche,
        Statut_Commercial, Jour_par_an, Weekends_par_an, Jour_Conges, RTT, Recuperation,
        Jour_Feries, Autres_jours_non_travailles, Administration_Commercial, Supervision,
        Convention, TA_Hors_Secteur, Event_Salon, Formations,
        Autres_jours_mission_hors_visite_Commercial, Solde_jours_de_travail_par_an,
        Solde_jours_statiques_par_an, Nombre_de_visite_client_par_jour,
        `Solde_visite_terrain_client_par_an(Possibles)`, Nombre_de_visite_prospects_par_jour,
        Pourcentage_des_visites_prospects, `Solde_visite_terrain_prospects_par_an(Possibles)`,
        `Solde_visite_terrain_client_par_an(Necessaire)`,
        `Solde_visite_terrain_client_par_an_necessaire(simulee)`,
        `Nombres_de_visite_Commercial_par_an_(Possibles)`
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    commercial_data = [
        (row['Code Commercial'], row['Nom Commercial'], row['Code Chef de marché'],
         0, 365, 104, 25.0, 10.0, 0.0, 9.0, 0.0, 43.39, 5.43, 8.13, 2.71, 5.43, 0.01, 0.0,
         217.0, 65.105, 5, 759, 1.25, 20.02, 190.0, 0, 0, 949.0)
        for _, row in df.drop_duplicates(subset=['Code Commercial']).iterrows()
        if pd.notna(row['Code Commercial']) and pd.notna(row['Nom Commercial']) and pd.notna(row['Code Chef de marché'])
    ]
    for i in range(0, len(commercial_data), batch_size):
        cursor.executemany(commercial_query, commercial_data[i:i + batch_size])
    st.success(f"{len(commercial_data)} commerciaux insérés ou mis à jour.")

    # Insertion des clients
    existing_clients = get_existing_ids(connection, 'client', 'ID_Client')
    # Requête modifiée pour l'insertion des clients
    client_query = """
    INSERT IGNORE INTO client (
        ID_Client, Code_Client, Nom_Client, Region_Client, Code_Postal, Ville_Client, 
        Pays_Client, Circuit_Client, Activite_Client, Potentiel_Client, 
        Fidelisation_Client, CA_Client, Couche, Regle_Prod, Nombre_de_visites_par_an
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Vérifiez si la colonne 'Nombre_de_visites_par_an' existe dans le fichier Excel
    if 'Nombre_de_visites_par_an' in df.columns:
        st.info("Colonne 'Nombre_de_visites_par_an' trouvée dans l'Excel, valeurs existantes utilisées.")
    else:
        st.info("Colonne 'Nombre_de_visites_par_an' non trouvée, valeurs par défaut (1) seront utilisées.")

    # Génération des données pour l'insertion
    client_data = [
        (replace_nan(row['Code client']), replace_nan(row['Code client']), replace_nan(row['Nom Client']),
        replace_nan(row['Région/Département Client']), replace_nan(row['Code postal Client']),
        replace_nan(row['Ville Client']), replace_nan(row['Pays Client']),
        replace_nan(row['Circuit Client']), replace_nan(row['Activité Client']),
        replace_nan(row['Potentiel Client']), replace_nan(row['Fidélisation Client']),
        replace_nan(row['CA Client']), replace_nan(row['Couche']),
        replace_nan(row['RegleProd Client']),
        replace_nan(row['Nombre_de_visites_par_an']) if 'Nombre_de_visites_par_an' in df.columns 
        and pd.notna(row['Nombre_de_visites_par_an']) else 1)  # Valeur par défaut = 1 si colonne absente ou vide
        for _, row in df.iterrows()
        if replace_nan(row['Code client']) not in existing_clients
    ]


    for i in range(0, len(client_data), batch_size):
        cursor.executemany(client_query, client_data[i:i + batch_size])
    st.success(f"{len(client_data)} nouveaux clients insérés.")

    # Insertion des visites
    existing_visites = get_existing_ids(connection, 'visite', 'ID_Visite')
    visite_query = """
    INSERT IGNORE INTO visite (ID_Visite, ID_Client, Id_Commercial, Date_Visite, Type_Visite)
    VALUES (%s, %s, %s, %s, %s)
    """
    visite_data = [
        (replace_nan(row['Code Visite']), replace_nan(row['Code client']), replace_nan(row['Code Commercial']),
         replace_nan(row.get('Date Visite')), replace_nan(row.get('Type Visite')))
        for _, row in df.iterrows()
        if replace_nan(row['Code Visite']) not in existing_visites
    ]

    for i in range(0, len(visite_data), batch_size):
        cursor.executemany(visite_query, visite_data[i:i + batch_size])
    st.success(f"{len(visite_data)} nouvelles visites insérées.")

    connection.commit()
    cursor.close()

def create_template():
    template_data = {
        'Code Visite': [''],
        'Nom Commercial': [''],
        'Nom Client': [''],
        'Activité Client': [''],
        'Potentiel Client': [''],
        'CA Client': [''],
        'Couche': [''],
        'RegleProd Client': [''],
        '4-Chef de marché': [''],
        'Code Chef de marché': [''],
        'Région/Département Client': [''],
        'Code postal Client': [''],
        'Ville Client': [''],
        'Code client': [''],
        'Code Commercial': [''],
        'Fidélisation Client': [''],
        'Pays Client': [''],
        'Circuit Client': [''],
        'Date Visite': [''],
        'Type Visite': [''],
        'Nombre_de_visites_par_an': ['']
    }
    return pd.DataFrame(template_data)

def main():
    st.title("Importation de données Excel vers MySQL")

    # Bouton pour télécharger le modèle
    template = create_template()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        template.to_excel(writer, index=False, sheet_name='Template')
    st.download_button(
        label="Télécharger le modèle Excel",
        data=buffer,
        file_name="template_import.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_file = st.file_uploader("Choisissez un fichier Excel", type="xlsx")
    
    if uploaded_file is not None:
        df_sheets = pd.read_excel(uploaded_file, sheet_name=None)
        sheet_names = list(df_sheets.keys())
        selected_sheet = st.selectbox("Choisissez la feuille à utiliser", sheet_names)
        
        if selected_sheet:
            df = df_sheets[selected_sheet]
            st.write("Aperçu des données:")
            st.dataframe(df.head())
            
            if st.button("Importer les données"):
                connection = create_connection()
                if connection is not None:
                    clear_all_data(connection)
                    
                    insert_data(connection, df)
                    st.success("Processus d'importation terminé!")
                    connection.close()
                else:
                    st.error("Impossible de se connecter à la base de données.")

if __name__ == "__main__":
    main()
