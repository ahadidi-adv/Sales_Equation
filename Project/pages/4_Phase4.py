import streamlit as st
import pymysql
import pandas as pd
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration de la page Streamlit
st.set_page_config(layout="wide")
st.logo("Africa.png", icon_image="Logo.png")
hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
    


navbar=st.container()

with navbar:
    selected = option_menu(
        menu_title=None,
        options=["Simulation","Comparaison"],
        icons=["house","book"], menu_icon="cast", default_index=0, orientation="horizontal"
    )

    if selected == "Simulation":
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("Simulation des visites clients (Nécessaires)")
        col1, col2 = st.columns(2)
        with col1:
            segmentation_des_clients=st.container()
        with col2:
            visualisation_des_segmentations=st.container()

        with segmentation_des_clients:
            st.subheader("Segmentation des clients")
            # Fonction pour récupérer les noms des colonnes de la table client
            def get_column_names():
                mycursor.execute("SHOW COLUMNS FROM client")
                return [col[0] for col in mycursor.fetchall() if col[0] not in ['ID_Client', '`Nombre_de_visites_par_an(simulee)`']]

            # Sélection dynamique des filtres par l'utilisateur
            columns = get_column_names()
            selected_filters = st.multiselect("Choisissez jusqu'à trois filtres pour les clients:", columns, default=columns[12], key="filter_selection")

            # Fonction pour récupérer les combinaisons uniques basées sur les filtres sélectionnés
            def fetch_unique_combinations_and_visits(filters):
                if filters:
                    query = f"SELECT {', '.join(filters)}, `Nombre_de_visites_par_an(simulee)` FROM client GROUP BY {', '.join(filters)} ORDER BY {', '.join(filters)}"
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
                        update_query = f"UPDATE client SET `Nombre_de_visites_par_an(simulee)` = {new_visits} WHERE {conditions}"
                        mycursor.execute(update_query)
                        success_messages.append(f"Mise à jour réussie pour les clients: {' && '.join(combo)} avec {new_visits} visites/année")
                mydb.commit()
                return success_messages


            #Faire un update des visites necessaires pour chaque commercial dans la base de données
            # Mise à jour des soldes de visites nécessaires pour chaque commercial
            def update_table_commercial():
                try:
                    update_query = """
                    UPDATE commercial c SET c.`Solde_visite_terrain_client_par_an_necessaire(simulee)` = (
                        SELECT SUM(cl.`Nombre_de_visites_par_an(simulee)`)
                        FROM client cl
                        JOIN visite v ON cl.ID_Client = v.ID_Client
                        WHERE v.Id_Commercial = c.Id_Commercial
                    )
                    """
                    mycursor.execute(update_query)
                    mydb.commit()
                    #st.success("Mise à jour des soldes de visites nécessaires réussie.")
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
                    query = f"SELECT {', '.join(filters)}, COUNT(*) as Nombre_de_Clients, `Nombre_de_visites_par_an(simulee)` FROM client GROUP BY {', '.join(filters)}, `Nombre_de_visites_par_an(simulee)` ORDER BY {', '.join(filters)}"
                    mycursor.execute(query)
                    rows = mycursor.fetchall()
                    # Création du DataFrame
                    df = pd.DataFrame(rows, columns=filters + ["Nombre_de_Clients", "Nombre_de_visites/an"])
                    # Ajout de la colonne Nb visites*Nb clients
                    df['Nb visites*Nb clients'] = df['Nombre_de_Clients'] * df['Nombre_de_visites/an']
                    return df
                return pd.DataFrame(columns=filters + ["Nombre_de_Clients", "`Nombre_de_visites_par_an(simulee)`", "Nb visites*Nb clients"])

            # Récupération des données et affichage du DataFrame
            df = fetch_data_for_dataframe(selected_filters)
            st.dataframe(df)





            _="""
            les cartes
            """


            st.subheader("Les cartes de synthese")
            # Calcul des métriques totales
            total_clients = df['Nombre_de_Clients'].sum()
            total_visits_segmentation = df['Nb visites*Nb clients'].sum()

            # Création d'une ligne avec deux colonnes pour afficher les métriques
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Nombre total des clients", value=total_clients)
            with col2:
                st.metric(label="Nombre total des visites", value=total_visits_segmentation)

        
    if selected == "Comparaison":
        st.title("Comparaison de la simulation des visites clients (Nécessaires)")
        # Charger tous les commerciaux pour le menu déroulant
        try:
            mycursor.execute("SELECT Nom_Commercial FROM commercial")
            all_commercials = [row[0] for row in mycursor.fetchall()]
            all_commercials.insert(0, "Tous les commerciaux")
            commercial_choice = st.selectbox("Choisir un Commercial", all_commercials)
        except Exception as e:
            st.error(f"Erreur lors de la récupération des commerciaux: {e}")
        p="""
        commercial_choice="Tous les commerciaux"
        """






        #Totales_visites_possibles commande dyalha s7i7a w maktkhrjch
        # Requête pour récupérer les totaux supplémentaires
        query3_simulee = """
        SELECT
            SUM(c.`Solde_visite_terrain_client_par_an_necessaire(simulee)`) AS Totales_visites_Necessaires,
            SUM(c.`Solde_visite_terrain_client_par_an(Possibles)`) AS Totales_visites_possibles, 
            SUM(c.`Solde_visite_terrain_client_par_an_necessaire(simulee)` / NULLIF(c.`Solde_visite_terrain_client_par_an(Possibles)`, 0)) AS Nombre_ETP_Etalon,
            (SELECT c.`Solde_visite_terrain_client_par_an(Possibles)`
            FROM commercial c
            WHERE c.`statut_commercial` = 0
            LIMIT 1) AS Visites_equivalent_a_1_ETP_etalon
        FROM
            commercial c
        """

        query4_simulee = """
        SELECT
            IF(COUNT(c.`Nom_Commercial`) = 1, c.`Pourcentage_des_visites_prospects`, 
            (SELECT c2.`Pourcentage_des_visites_prospects` FROM `commercial` c2 WHERE c2.`Statut_Commercial` = 0 GROUP BY c2.`Pourcentage_des_visites_prospects` ORDER BY COUNT(c2.`Pourcentage_des_visites_prospects`) DESC LIMIT 1)) AS Pourcentage_des_visites_prospects,
            IF(COUNT(c.`Nom_Commercial`) = 1, c.`Solde_visite_terrain_prospects_par_an(Possibles)`, 
            (SELECT c2.`Solde_visite_terrain_prospects_par_an(Possibles)` FROM `commercial` c2 WHERE c2.`Statut_Commercial` = 0 GROUP BY c2.`Solde_visite_terrain_prospects_par_an(Possibles)` ORDER BY COUNT(c2.`Solde_visite_terrain_prospects_par_an(Possibles)`) DESC LIMIT 1)) AS Visites_terrain_prospects_par_an,
            
            IF(COUNT(c.`Nom_Commercial`) = 1, (c.`Solde_visite_terrain_prospects_par_an(Possibles)` + c.`Solde_visite_terrain_client_par_an(Possibles)`), 
                (SELECT c2.`Solde_visite_terrain_prospects_par_an(Possibles)` + c2.`Solde_visite_terrain_client_par_an(Possibles)` FROM `commercial` c2 WHERE c2.`Statut_Commercial` = 0 GROUP BY c2.`Solde_visite_terrain_prospects_par_an(Possibles)` + c2.`Solde_visite_terrain_client_par_an(Possibles)` ORDER BY COUNT(*) DESC LIMIT 1)) AS `Totales_visites_clients_prospects`,
            
            SUM(c.`Solde_visite_terrain_client_par_an_necessaire(simulee)` + c.`Solde_visite_terrain_prospects_par_an(Possibles)`) AS Totales_visites_clients_prospects_P2,
            SUM((c.`Solde_visite_terrain_client_par_an_necessaire(simulee)` + c.`Solde_visite_terrain_prospects_par_an(Possibles)`) / (c.`Solde_visite_terrain_prospects_par_an(Possibles)` + c.`Solde_visite_terrain_client_par_an(Possibles)`)) AS Nombres_ETP_Clients_Prospects,
            COUNT(c.`Nom_Commercial`) AS Nombre_de_commerciaux
        FROM
            commercial c
        """

        query_etp_count_simulee = """
                        SELECT COUNT(*) AS Commerciaux_avec_ETP_sup_1
                        FROM (
                            SELECT c.Id_Commercial,
                                SUM(cl.`Nombre_de_visites_par_an(simulee)`) / NULLIF(c.`Solde_visite_terrain_client_par_an(Possibles)`, 0) as ETP_avant_Prospection
                            FROM commercial c
                            JOIN visite v ON c.Id_Commercial = v.Id_Commercial
                            JOIN client cl ON v.ID_Client = cl.ID_Client
                            GROUP BY c.Id_Commercial
                            HAVING ETP_avant_Prospection > 1
                        ) AS Commerciaux_avec_ETP
                        """




        #Les requetes dyl dekchi l9dim (Phase2)
        query3 = """
        SELECT
            SUM(c.`Solde_visite_terrain_client_par_an(Necessaire)`) AS Totales_visites_Necessaires,
            SUM(c.`Solde_visite_terrain_client_par_an(Possibles)`) AS Totales_visites_possibles, 
            SUM(c.`Solde_visite_terrain_client_par_an(Necessaire)` / NULLIF(c.`Solde_visite_terrain_client_par_an(Possibles)`, 0)) AS Nombre_ETP_Etalon,
            (SELECT c.`Solde_visite_terrain_client_par_an(Possibles)`
            FROM commercial c
            WHERE c.`statut_commercial` = 0
            LIMIT 1) AS Visites_equivalent_a_1_ETP_etalon
        FROM
            commercial c
        """

        query4 = """
        SELECT
            IF(COUNT(c.`Nom_Commercial`) = 1, c.`Pourcentage_des_visites_prospects`, 
            (SELECT c2.`Pourcentage_des_visites_prospects` FROM `commercial` c2 WHERE c2.`Statut_Commercial` = 0 GROUP BY c2.`Pourcentage_des_visites_prospects` ORDER BY COUNT(c2.`Pourcentage_des_visites_prospects`) DESC LIMIT 1)) AS Pourcentage_des_visites_prospects,
            IF(COUNT(c.`Nom_Commercial`) = 1, c.`Solde_visite_terrain_prospects_par_an(Possibles)`, 
            (SELECT c2.`Solde_visite_terrain_prospects_par_an(Possibles)` FROM `commercial` c2 WHERE c2.`Statut_Commercial` = 0 GROUP BY c2.`Solde_visite_terrain_prospects_par_an(Possibles)` ORDER BY COUNT(c2.`Solde_visite_terrain_prospects_par_an(Possibles)`) DESC LIMIT 1)) AS Visites_terrain_prospects_par_an,
            
            IF(COUNT(c.`Nom_Commercial`) = 1, (c.`Solde_visite_terrain_prospects_par_an(Possibles)` + c.`Solde_visite_terrain_client_par_an(Possibles)`), 
                (SELECT c2.`Solde_visite_terrain_prospects_par_an(Possibles)` + c2.`Solde_visite_terrain_client_par_an(Possibles)` FROM `commercial` c2 WHERE c2.`Statut_Commercial` = 0 GROUP BY c2.`Solde_visite_terrain_prospects_par_an(Possibles)` + c2.`Solde_visite_terrain_client_par_an(Possibles)` ORDER BY COUNT(*) DESC LIMIT 1)) AS `Totales_visites_clients_prospects`,
            
            SUM(c.`Solde_visite_terrain_client_par_an(Necessaire)` + c.`Solde_visite_terrain_prospects_par_an(Possibles)`) AS Totales_visites_clients_prospects_P2,
            SUM((c.`Solde_visite_terrain_client_par_an(Necessaire)` + c.`Solde_visite_terrain_prospects_par_an(Possibles)`) / (c.`Solde_visite_terrain_prospects_par_an(Possibles)` + c.`Solde_visite_terrain_client_par_an(Possibles)`)) AS Nombres_ETP_Clients_Prospects,
            COUNT(c.`Nom_Commercial`) AS Nombre_de_commerciaux
        FROM
            commercial c
        """

        query_etp_count = """
        SELECT COUNT(*) AS Commerciaux_avec_ETP_sup_1
        FROM (
            SELECT c.Id_Commercial,
                SUM(cl.`Nombre_de_visites_par_an`) / NULLIF(c.`Solde_visite_terrain_client_par_an(Possibles)`, 0) as ETP_avant_Prospection
            FROM commercial c
            JOIN visite v ON c.Id_Commercial = v.Id_Commercial
            JOIN client cl ON v.ID_Client = cl.ID_Client
            GROUP BY c.Id_Commercial
            HAVING ETP_avant_Prospection > 1
        ) AS Commerciaux_avec_ETP
        """

        # Ajouter une condition pour filtrer selon le choix du commercial
        if commercial_choice != "Tous les commerciaux":
            query3_simulee += " WHERE c.Nom_Commercial = %s"
            query4_simulee += " WHERE c.Nom_Commercial = %s"
            query3 += " WHERE c.Nom_Commercial = %s"
            query4 += " WHERE c.Nom_Commercial = %s"


        # Exécution des requêtes et affichage des tableaux
        try:
            if commercial_choice == "Tous les commerciaux":
                mycursor.execute(query3_simulee)
                data3_simulee = mycursor.fetchone()
                mycursor.execute(query4_simulee)
                data4_simulee = mycursor.fetchone()
                mycursor.execute(query_etp_count_simulee)
                count_etp_sup_1_simulee = mycursor.fetchone()[0]
                mycursor.execute(query3)
                data3 = mycursor.fetchone()
                mycursor.execute(query4)
                data4 = mycursor.fetchone()
                mycursor.execute(query_etp_count)
                count_etp_sup_1 = mycursor.fetchone()[0]  # Récupération du résultat
            else:
                mycursor.execute(query3_simulee, (commercial_choice,))
                data3_simulee = mycursor.fetchone()
                mycursor.execute(query4_simulee, (commercial_choice,))
                data4_simulee = mycursor.fetchone()
                mycursor.execute(query_etp_count_simulee)
                count_etp_sup_1_simulee = mycursor.fetchone()[0]
                mycursor.execute(query3, (commercial_choice,))
                data3 = mycursor.fetchone()
                mycursor.execute(query4, (commercial_choice,))
                data4 = mycursor.fetchone()
                mycursor.execute(query_etp_count)
                count_etp_sup_1 = mycursor.fetchone()[0]  # Récupération du résultat



            

            col1, col2, col3 = st.columns(3)
            with col1:

                st.header("Portefeuille Clients (Simulation)")
                # Conversion des valeurs en entiers ou en flottants
                totales_visites_necessaires_simulee = int(data3_simulee[0])
                nombre_etp_etalon_simulee = round(float(data3_simulee[2]),2)
                visites_equivalent_1_etp_simulee = int(data3_simulee[3])
                totales_visites_possibles_simulee = int(data3_simulee[1])

                st.metric("Totales visites Nécessaires", totales_visites_necessaires_simulee)
                st.metric("Nombre ETP Etalon", nombre_etp_etalon_simulee)
                st.metric("Visites équivalent à 1 ETP etalon", visites_equivalent_1_etp_simulee)
                st.metric("Totales visites possibles des commerciaux", totales_visites_possibles_simulee)
                st.metric("Nombre des commerciaux avec ETP avant Prospection > 1",count_etp_sup_1_simulee)
                

            with col2:
                st.header("Portefeuille Clients")
                # Conversion des valeurs en entiers ou en flottants
                totales_visites_necessaires = int(data3[0])
                nombre_etp_etalon = round(float(data3[2]),2)
                visites_equivalent_1_etp = int(data3[3])
                totales_visites_possibles = int(data3[1])

                st.metric("Totales visites Nécessaires", totales_visites_necessaires)
                st.metric("Nombre ETP Etalon", nombre_etp_etalon)
                st.metric("Visites équivalent à 1 ETP etalon", visites_equivalent_1_etp)
                st.metric("Totales visites possibles des commerciaux", totales_visites_possibles)
                st.metric("Nombre des commerciaux avec ETP avant Prospection > 1",count_etp_sup_1)

            with col3:
                st.subheader("Visualisation et comparaison des résultats")
                chart_choice = st.selectbox("Sélectionnez le graphique à afficher", options=["Comparaison des visites réel vs simulation", "Comparaison des Visites Nécessaires et Possibles"], index=1)
                if chart_choice == "Comparaison des visites réel vs simulation":
                    # Graphique en barres pour les visites nécessaires et possibles des commerciaux
                    # Graphique en barres : Ce graphique compare les visites nécessaires et possibles pour les commerciaux en simulation et en conditions réelles. Cela aide à identifier les écarts potentiels entre les besoins estimés et les capacités actuelles.
                
                    fig, ax = plt.subplots()

                    labels = ['Simulation', 'Réel']
                    visites_necessaires = [totales_visites_necessaires_simulee, totales_visites_necessaires]
                    visites_possibles = [totales_visites_possibles_simulee, totales_visites_possibles]

                    x = range(len(labels))

                    bar1 = ax.bar(x, visites_necessaires, width=0.4, label='Visites Nécessaires', align='center')
                    bar2 = ax.bar(x, visites_possibles, width=0.4, label='Visites Possibles', align='edge')

                    ax.set_ylabel('Nombre de visites')
                    ax.set_title('Comparaison des visites réel vs simulation')
                    ax.set_xticks(x)
                    ax.set_xticklabels(labels)
                    ax.legend()
                    # Ajout des valeurs à l'intérieur des barres
                    # Ajout des valeurs à l'intérieur des barres avec décalage pour bar1
                    def add_values_inside(bars, offset_text=(0, 0)):
                        for bar in bars:
                            height = bar.get_height()
                            ax.annotate('{}'.format(height),
                                        xy=(bar.get_x() + bar.get_width() / 2, height/2),  # Placer le texte à mi-hauteur
                                        xytext=offset_text,  # Appliquer le décalage spécifié
                                        textcoords="offset points",
                                        ha='center', va='center', color='white')

                    add_values_inside(bar1, offset_text=(-20, 0))  # Décalage de text spécifique pour bar1
                    add_values_inside(bar2)  # Pas de décalage de text pour bar2

                    st.pyplot(fig)
                    # Graphique en barres : Ce graphique compare les visites nécessaires et possibles pour les commerciaux en simulation et en conditions réelles. Cela aide à identifier les écarts potentiels entre les besoins estimés et les capacités actuelles.
                
                elif chart_choice == "Comparaison des Visites Nécessaires et Possibles":
                    #Graphiques à barres empilées: Ces graphiques montrent pour chaque cas (actuel et simulé) la proportion des visites nécessaires par rapport aux visites possibles, facilitant ainsi la visualisation de la capacité de couverture des visites.
                    #Graphiques à barres empilées pour les visites : Offrent une vue claire sur la capacité de chaque scénario à couvrir les besoins en visites, en montrant directement le déficit ou l'excès dans les visites possibles par rapport aux nécessaires.

                    # Données pour le graphique
                    categories = ['Actuel', 'Simulé']
                    necessaires = [totales_visites_necessaires, totales_visites_necessaires_simulee]
                    possibles = [totales_visites_possibles, totales_visites_possibles_simulee]

                    x = range(len(categories))  # l'axe des x

                    fig, ax = plt.subplots()
                    bars_possibles = ax.bar(x, possibles, width=0.4, label='Visites Possibles', color='green')
                    bars_necessaires = ax.bar(x, necessaires, width=0.4, label='Visites Nécessaires', color='red', bottom=possibles)

                    ax.set_xlabel('Catégorie')
                    ax.set_ylabel('Nombre de Visites')
                    ax.set_title('Comparaison des Visites Nécessaires et Possibles')
                    ax.set_xticks(x)
                    ax.set_xticklabels(categories)
                    ax.legend()

                    # Ajout des valeurs à l'intérieur des barres pour 'possibles'
                    def add_values_inside(bars):
                        for bar in bars:
                            height = bar.get_height()
                            ax.annotate('{}'.format(height),
                                        xy=(bar.get_x() + bar.get_width() / 2, height/2),  # Positionner le texte à mi-hauteur de la barre 'possibles'
                                        xytext=(0, 0),  # Pas de décalage
                                        textcoords="offset points",
                                        ha='center', va='center', color='white')

                    # Ajout des valeurs à l'intérieur des barres pour 'necessaires'
                    def add_values_inside_necessaires(bars, bottoms):
                        for bar, bottom in zip(bars, bottoms):
                            height = bar.get_height()
                            ax.annotate('{}'.format(height),
                                        xy=(bar.get_x() + bar.get_width() / 2, bottom + height/2),  # Positionner le texte au milieu de la partie 'necessaires'
                                        xytext=(0, 0),  # Pas de décalage
                                        textcoords="offset points",
                                        ha='center', va='center', color='white')

                    add_values_inside(bars_possibles)
                    add_values_inside_necessaires(bars_necessaires, possibles)

                    st.pyplot(fig)

        
            st.divider()
            
            
            #Portefeuille Clients - Prospects
            col1, col22,col3 = st.columns(3)
            with col1:
                st.header("Portefeuille Clients - Prospects (Simulation)")
                pourcentage_visites_prospects_simulee = round(data4_simulee[0], 2)
                visites_terrain_prospects_par_an_simulee = int(data4_simulee[1])
                totales_visites_clients_prospects_simulee = int(data4_simulee[2])
                totales_visites_clients_prospects_P2_simulee = int(data4_simulee[3])
                nombres_etp_clients_prospects_simulee = round(data4_simulee[4], 2)
                nombre_de_commerciaux_choisis_simulee = int(data4_simulee[5])

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("% Pourcentage des visites prospects", pourcentage_visites_prospects_simulee)
                    st.metric("Totales visites clients + Prospects (P1)", totales_visites_clients_prospects_simulee)
                    st.metric("Nombres ETP Clients + Prospects", nombres_etp_clients_prospects_simulee)
                    

                with col2:
                    st.metric("Visites terrain prospects par an (P1)", visites_terrain_prospects_par_an_simulee)
                    st.metric("Totales visites clients + Prospects (P2)", totales_visites_clients_prospects_P2_simulee) 
                    st.metric("Nombre de commerciaux", nombre_de_commerciaux_choisis_simulee)   

            with col22:
                st.header("Portefeuille Clients - Prospects")         
                pourcentage_visites_prospects = round(data4[0], 2)
                visites_terrain_prospects_par_an = int(data4[1])
                totales_visites_clients_prospects = int(data4[2])
                totales_visites_clients_prospects_P2 = int(data4[3])
                nombres_etp_clients_prospects = round(data4[4], 2)
                nombre_de_commerciaux_choisis = int(data4[5])

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("% Pourcentage des visites prospects", pourcentage_visites_prospects)
                    st.metric("Totales visites clients + Prospects (P1)", totales_visites_clients_prospects)
                    st.metric("Nombres ETP Clients + Prospects", nombres_etp_clients_prospects)
                    

                with col2:
                    st.metric("Visites terrain prospects par an (P1)", visites_terrain_prospects_par_an)
                    st.metric("Totales visites clients + Prospects (P2)", totales_visites_clients_prospects_P2) 
                    st.metric("Nombre de commerciaux", nombre_de_commerciaux_choisis)   

            with col3:
                # Graphique
                # Graphique en barres pour le nombre de commerciaux avec ETP > 1
                # Graphique en barres pour le nombre de commerciaux avec ETP > 1 : Ce graphique permettra de comparer directement le nombre de commerciaux avec un ETP supérieur à 1 entre les deux scénarios (actuel et simulé).
                st.subheader("Comparaison du nombre de commerciaux avec ETP > 1")

                fig, ax = plt.subplots(figsize=(7, 3.5))

                labels = ['Simulation', 'Réel']
                etp_counts = [count_etp_sup_1_simulee, count_etp_sup_1]

                ax.bar(labels, etp_counts, color=['blue', 'green'])

                ax.set_ylabel('Nombre de commerciaux')
                ax.set_title('Nombre de commerciaux avec ETP > 1')
                ax.set_ylim(0, max(etp_counts) + 1)

                for i, v in enumerate(etp_counts):
                    ax.text(i, v + 0.5, str(v), ha='center', va='bottom')

                st.pyplot(fig)

        # Enregistrement des nouveaux données
            if st.button("Mettre les résultats de simulation comme Résultat Réel 💾"):
                try:
                    update_clients_query = """
                        UPDATE client
                        SET `Nombre_de_visites_par_an` = `Nombre_de_visites_par_an(simulee)`
                        """
                    update_commercials_query ="""
                    UPDATE commercial c SET c.`Solde_visite_terrain_client_par_an(Necessaire)` = (
                            SELECT SUM(cl.Nombre_de_visites_par_an)
                            FROM client cl
                            JOIN visite v ON cl.ID_Client = v.ID_Client
                            WHERE v.Id_Commercial = c.Id_Commercial
                        )
                        """
                    mycursor.execute(update_clients_query)
                    mycursor.execute(update_commercials_query)
                    mydb.commit()  # Commit the changes to the database
                    st.success("Résultats de simulation appliqués avec succès comme résultats réels.")
                except Exception as e:
                    mydb.rollback()  # Roll back in case of error
                    st.error(f"Échec de la mise à jour de la base de données : {e}")


        except Exception as e:
            st.error(f"Erreur lors de l'exécution de la requête SQL: {e}")

        # Fermeture de la connexion
        mycursor.close()
        mydb.close()

