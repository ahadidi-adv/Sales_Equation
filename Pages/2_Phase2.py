"""
Code ba9i mafahmoch mezian 7it men chatgpt
visualisation -> b7al power bi t9riban


Dans SQL de ctte partie j'ai ajouter 3 triggers qui fait un update automatique de total_visits_segmentation dans la table calculs
"""

import streamlit as st
import mysql.connector
import pandas as pd

# Configuration de la page Streamlit
st.set_page_config(layout="wide")
st.title("Gestion des Visites Clients (Nécessaires)")
st.logo("Africa.png", icon_image="Logo.png")


# Tentative de connexion à la base de données MySQL
try:
    mydb = mysql.connector.connect(
        host='bjjvcnkquh3rdkwnqviv-mysql.services.clever-cloud.com',
            user='usbidjmhwyxcuar4',
            password='tQemqKFD6orQ1DLz4Xrl',
            port=3306,
            database='bjjvcnkquh3rdkwnqviv'
    )
    mycursor = mydb.cursor()
except mysql.connector.Error as err:
    st.error(f"Erreur de connexion : {err}")




col1, col2 = st.columns(2)
with col1:
    segmentation_des_clients=st.container()
with col2:
    visualisation_des_segmentations=st.container()

with segmentation_des_clients:
    st.subheader("Filtres de Bornage")
    # Fonction pour récupérer les noms des colonnes de la table client
    def get_column_names():
        mycursor.execute("SHOW COLUMNS FROM client")
        return [col[0] for col in mycursor.fetchall() if col[0] not in ['ID_Client', 'Nombre_de_visites_par_an']]

    # Sélection dynamique des filtres par l'utilisateur
    columns = get_column_names()
    selected_filters = st.multiselect("Choisissez jusqu'à trois filtres pour les clients:", columns, default=columns[12], key="filter_selection")

    # Fonction pour récupérer les combinaisons uniques basées sur les filtres sélectionnés
    def fetch_unique_combinations_and_visits(filters):
        if filters:
            query = f"SELECT {', '.join(filters)}, Nombre_de_visites_par_an FROM client GROUP BY {', '.join(filters)} ORDER BY {', '.join(filters)}"
            mycursor.execute(query)
            return mycursor.fetchall()
        return []

    # Récupération des combinaisons uniques et initialisation des valeurs d'entrée
    unique_combinations = fetch_unique_combinations_and_visits(selected_filters)
    visits_input = {}
    current_visits = {}
    for combo in unique_combinations:
        key = "_".join(str(x) for x in combo[:-1])
        current_visits[key] = combo[-1]
        visits_input[key] = st.number_input(f"Nombre de visites pour {' & '.join(str(x) for x in combo[:-1])}", min_value=0, value=combo[-1], key=f"input_{key}")

    # Fonction pour mettre à jour le nombre de visites
    def update_visits_bulk(filters, updates, current_visits):
        success_messages = []
        for key, new_visits in updates.items():
            if new_visits != current_visits[key]:
                combo = key.split('_')
                conditions = " AND ".join(f"{filt} = '{val}'" for filt, val in zip(filters, combo))
                update_query = f"UPDATE client SET Nombre_de_visites_par_an = {new_visits} WHERE {conditions}"
                mycursor.execute(update_query)
                success_messages.append(f"Mise à jour réussie pour {' - '.join(combo)} avec {new_visits} visites/année")
        mydb.commit()
        return success_messages

    #Faire un update des visites necessaires pour chaque commercial dans la base de données
    # Mise à jour des soldes de visites nécessaires pour chaque commercial
    def update_table_commercial():
        try:
            update_query = """
            UPDATE commercial c SET c.`Solde_visite_terrain_client_par_an(Necessaire)` = (
                SELECT SUM(cl.Nombre_de_visites_par_an)
                FROM client cl
                JOIN visite v ON cl.ID_Client = v.ID_Client
                WHERE v.Id_Commercial = c.Id_Commercial
            )
            """
            mycursor.execute(update_query)
            mydb.commit()
            st.success("Mise à jour des soldes de visites nécessaires réussie.")
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour des soldes de visites: {e}")

    # Bouton global pour enregistrer toutes les modifications
    if st.button("Enregistrer Tout"):
        updates = {key: visits_input[key] for key in visits_input}
        success_messages = update_visits_bulk(selected_filters, updates, current_visits)
        for message in success_messages:
            st.success(message)
        update_table_commercial()






_="""
Hna katbda partie dyl tableau

"""



with visualisation_des_segmentations:
    st.subheader("Visualisation des segmentations")
    # Fonction pour récupérer les données pour le DataFrame avec comptage de clients et calcul du produit
    def fetch_data_for_dataframe(filters):
        if filters:
            # Inclure COUNT(*) pour compter les clients par combinaison
            query = f"SELECT {', '.join(filters)}, COUNT(*) as Nombre_de_Clients, Nombre_de_visites_par_an FROM client GROUP BY {', '.join(filters)}, Nombre_de_visites_par_an ORDER BY {', '.join(filters)}"
            mycursor.execute(query)
            rows = mycursor.fetchall()
            # Création du DataFrame
            df = pd.DataFrame(rows, columns=filters + ["Nombre_de_Clients", "Nombre_de_visites/an"])
            # Ajout de la colonne Nb visites*Nb clients
            df['Nb visites*Nb clients'] = df['Nombre_de_Clients'] * df['Nombre_de_visites/an']
            return df
        return pd.DataFrame(columns=filters + ["Nombre_de_Clients", "Nombre_de_visites_par_an", "Nb visites*Nb clients"])

    # Récupération des données et affichage du DataFrame
    df = fetch_data_for_dataframe(selected_filters)
    st.dataframe(df)





    _="""
    les cartes
    """


    st.subheader("Cartes de synthese")
    # Calcul des métriques totales
    total_clients = df['Nombre_de_Clients'].sum()
    total_visits_segmentation = df['Nb visites*Nb clients'].sum()

    # Création d'une ligne avec deux colonnes pour afficher les métriques
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Nombre total des clients", value=total_clients)
    with col2:
        st.metric(label="Nombre total des visites", value=total_visits_segmentation)




