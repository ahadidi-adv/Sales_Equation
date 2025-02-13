import streamlit as st
import pymysql
import pandas as pd
from streamlit_option_menu import option_menu
import streamlit_shadcn_ui as ui
import plost
import matplotlib.pyplot as plt 
import time

# Set up the layout
st.set_page_config(layout="wide")


#logo
st.logo("Africa.png", icon_image="Logo.png")

# Establish a connection to MySQL Server
try:
    mydb = pymysql.connect(
    host='bjjvcnkquh3rdkwnqviv-mysql.services.clever-cloud.com',
            user='usbidjmhwyxcuar4',
            password='tQemqKFD6orQ1DLz4Xrl',
            port=3306,
            database='bjjvcnkquh3rdkwnqviv'
    )
    #Create a cursor object
    mycursor = mydb.cursor()
    print("Connection Established")
except:
    st.error("cONNECTION ERROR")



navbar=st.container()

with navbar:
    selected = option_menu(
        menu_title=None,
        options=["Détermination des jours","Détermination des visites possibles","Commercial"],
        icons=["house","book"], menu_icon="cast", default_index=0, orientation="horizontal"
    )

    if selected == "Détermination des jours":
        #Les fonctions
        def get_field_value(field_name_in_database,valeur_par_defaut):
            # Exécuter une requête SQL pour récupérer la valeur du champ spécifique du premier commercial
            # attention: il a la requete madaztch bghito y afficher la valeur par deafut
            mycursor.execute(f'''SELECT {field_name_in_database}, COUNT(*) AS count 
                            FROM commercial 
                            GROUP BY {field_name_in_database} 
                            ORDER BY count DESC LIMIT 1''')
            field_value = mycursor.fetchone()[0]  # Récupérer la valeur du champ spécifique du premier commercial
            return field_value if field_value is not None else valeur_par_defaut  # Utiliser valeur par défaut si la valeur est nulle




        # Containers for the different sections
        conteneur_de_jours_de_travail = st.container()
        st.divider()

        conteneur_de_jours_non_travailles = st.container()
        st.divider()

        balance_conteneur_de_jours_de_travail = st.container()
        st.divider()

        Proratisation_en_mois = st.container()
        st.divider()


        conteneur_de_jours_de_mission = st.container()
        convertisseur_des_jours = st.container()
        st.divider()


        conteneur_de_stats = st.container()

        Solde_jours_de_travail_par_semaine = 4.33
        Semaine_par_mois=4.33
        #4.33 weeks per month (52 weeks per year divided by 12 months)
        Jours_travaillees_par_semaine=5




        with conteneur_de_jours_de_travail:
            st.header('Jours de travail par an hors weekend')
            def is_leap_year(year):
                """Return True if year is a leap year, otherwise False."""
                return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                # L'utilisateur choisit l'année
                Jour_par_an = st.number_input('Année', min_value=365, max_value=366, value=365)
                p="""
                year = st.number_input('Année', min_value=2023, max_value=2030, value=2024)
                # Calcul du nombre de jours selon si l'année est bissextile
                Jour_par_an = 365 if is_leap_year(year) else 365
                """
            with col2:
                Weekends_par_an=st.number_input('Weekends', value=get_field_value('Weekends_par_an',104))
            with col3:
                Potentiel_jour_travailles_par_an = (Jour_par_an - Weekends_par_an)
                st.metric(label="Potentiel de jours de travail par an", value=Potentiel_jour_travailles_par_an)
                #ui.metric_card(title="Potentiel de jours de travail par an", content=Potentiel_jour_travailles_par_an)

            def update_non_working_days():
                try:
                    # Assuming you have a table `commercial_profile` with columns for each day type
                    query = """
                    UPDATE commercial
                    SET Jour_par_an = %s, Weekends_par_an = %s
                    """
                    # Values to be updated; these should be fetched from the user inputs in Streamlit
                    values = (Jour_par_an , Weekends_par_an)
                    
                    mycursor.execute(query, values)
                    mydb.commit()
                    st.success(f"Updated {mycursor.rowcount} rows.")
                except Exception as e:
                    st.error(f"Failed to update database: {e}")


            if st.button("Enregistrer"):
                update_non_working_days()   








        with conteneur_de_jours_non_travailles:
            st.header('Jours non travaillés par an')
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                Jour_Conges=st.number_input('Congés', step=0.5 ,value=get_field_value('Jour_Conges',25))
            with col2:
                RTT=st.number_input('RTT', step=0.5 ,value=get_field_value('RTT',10))
            with col3:
                Recuperation=st.number_input('Récupération', step=0.5 ,value=get_field_value('Recuperation',1.00))
            with col4:
                Jour_Feries=st.number_input('Jour Féries', step=0.5 ,value=get_field_value('Jour_Feries',9))
            with col5:
                Autres_jours_non_travailles=st.number_input('Autres', step=0.5 ,value=get_field_value('Autres_jours_non_travailles',0)) #attention khas tzad lfct get_field_value hna
            with col6:
            # Use a separate container for the total if necessary
                Jours_non_travailles_par_an_hors_weekend=(Jour_Conges+RTT+Recuperation+Jour_Feries+Autres_jours_non_travailles)
                st.metric(label="Total Jours non travailles (Hors Weekend)", value=Jours_non_travailles_par_an_hors_weekend)
            
                #Khas kola type de calcul b7alh hado ydaro fw7d 2 fcts w ktwli dir rir l'affichage des clculs lt7t
                #hadi blastha l2aslia f 232
                Jours_non_travailles_par_an=Weekends_par_an+Jours_non_travailles_par_an_hors_weekend
                print(Jours_non_travailles_par_an)
                print(Jours_non_travailles_par_an_hors_weekend)
                print(Weekends_par_an)
                #hadi blastha l2aslia f 233
                Solde_jours_de_travail_par_an=Jour_par_an-Jours_non_travailles_par_an
            


            # Function to update non-working days for all commercial profiles
            def update_non_working_days():
                try:
                    # Assuming you have a table `commercial_profile` with columns for each day type
                    query = """
                    UPDATE commercial
                    SET Jour_par_an = %s, Weekends_par_an = %s, Jour_Conges = %s, RTT = %s, Recuperation = %s, Jour_Feries = %s, Autres_jours_non_travailles = %s, Solde_jours_de_travail_par_an = %s
                    """
                    # Values to be updated; these should be fetched from the user inputs in Streamlit
                    values = (Jour_par_an , Weekends_par_an, Jour_Conges, RTT, Recuperation, Jour_Feries, Autres_jours_non_travailles, Solde_jours_de_travail_par_an)
                    
                    mycursor.execute(query, values)
                    mydb.commit()
                    st.success(f"Updated {mycursor.rowcount} rows.")
                except Exception as e:
                    st.error(f"Failed to update database: {e}")
            
            
            if st.button("Cliquez ici pour Enregistrer", key=2):
                update_non_working_days()






        with balance_conteneur_de_jours_de_travail:
            st.header('Solde jours de travail')
            col1, col2, col3 = st.columns(3)
            with col1:
                #Jours_non_travailles_par_an=Weekends_par_an+Jours_non_travailles_par_an_hors_weekend
                # 232
                st.metric(label="Total Jours non travailles + Week-end", value=Jours_non_travailles_par_an)
            with col2:
                #khas Solde_jours_de_travail_par_an tbedel l Solde_jours_travailles_par_an fkolchi w ta flabse de données 
                #Solde_jours_de_travail_par_an=Jour_par_an-Jours_non_travailles_par_an
                # 233
                st.metric(label="Solde jours travailles par an", value=Solde_jours_de_travail_par_an)
            with col3:
                st.metric(label="Jour de travail par semaine",value=Jours_travaillees_par_semaine)


        #cv



        with Proratisation_en_mois:
            st.header('Proratisation en mois')
            col1, col2, col3 = st.columns(3)
            with col1:
                # attention à verifierrrrrrrrrr mafhmtch 3lach madaroch directement le nombre dyl jours par an / 12 
                Total_semaine_non_travaillée=Jours_non_travailles_par_an_hors_weekend / Jours_travaillees_par_semaine#=5
                
                Total_mois_non_travailles=Total_semaine_non_travaillée/Semaine_par_mois#=4.33 #4.33 weeks per month (52 weeks per year divided by 12 months)
                #Total_mois_non_travailles=(Jours_non_travailles_par_an_hors_weekend/5)/4.33 #NOrmalement je ne dois pas donner le choix à l'utilisateur
                st.metric(label="Total mois non travailles", value=round(Total_mois_non_travailles, 2))
            with col2:
                Solde_mois_de_travail=12-Total_mois_non_travailles
                st.metric(label="Solde mois de travail", value=round(Solde_mois_de_travail,2))
            with col3:
                Solde_jours_de_travail_par_mois=(Solde_jours_de_travail_par_an/Solde_mois_de_travail)
                st.metric(label="Solde Jours de travail par mois", value=round(Solde_jours_de_travail_par_mois,2))





        with conteneur_de_jours_de_mission:
            #st.header('Nombre de jours de missions hors visites terrain')
            st.header('Nombre de jours des activités statiques')
            st.write("Choisir le nombre de jours pour chaque type de missions. (Nombre de jour par an)")    
            
            # Layout for the statistics at the bottom
            col1, col2, col3,col4, col5, col6, col7 = st.columns(7)
            with col1:
                Administratif=st.number_input('Administratif', value=get_field_value('Administration_Commercial',45.50))
            with col2:
                Supervision_Management=st.number_input('Supervision/Management', value=get_field_value('Supervision', 0.50))
            with col3:
                Convention=st.number_input('Convention', value=get_field_value('Convention', 11.00))
            with col4:
                TA_Hors_Secteur=st.number_input('TA Hors Secteur', value=get_field_value('TA_Hors_Secteur', 9.00))
            with col5:
                Event_Salon=st.number_input('Event Salon', value=get_field_value('Event_Salon', 0.25))
            with col6:
                Formations=st.number_input('Formation', value=get_field_value('Formations', 0.00))
            with col7:
                Autres_jours_mission_hors_visite=st.number_input('Autres', value=get_field_value('Autres_jours_mission_hors_visite_Commercial', 0.00))
            # ... and so on for other stats

                #hadi blastha f 433
                # Calcul du nombre de jours travailles par semaine pour chaque catégorie
                Solde_jours_statiques_par_an = (Administratif + Supervision_Management + Convention + TA_Hors_Secteur + Event_Salon + Formations + Autres_jours_mission_hors_visite)

            def update_jours_statiques():
                try:
                    # Assuming you have a table `commercial_profile` with columns for each day type
                    query = """
                    UPDATE commercial
                    SET Administration_Commercial = %s, Supervision = %s, Convention = %s, TA_Hors_Secteur = %s,
                    Event_Salon = %s, Formations = %s, Autres_jours_mission_hors_visite_Commercial = %s, Solde_jours_statiques_par_an =%s
                    """

                    # Values to be updated; these should be fetched from the user inputs in Streamlit
                    values = (Administratif, Supervision_Management, Convention, TA_Hors_Secteur, Event_Salon, Formations, Autres_jours_mission_hors_visite,Solde_jours_statiques_par_an)
                    
                    mycursor.execute(query, values)
                    mydb.commit()
                    st.success(f"Updated {mycursor.rowcount} rows.")
                except Exception as e:
                    st.error(f"Failed to update database: {e}")
            
            
            if st.button("Cliquez ici pour Enregistrer"):
                update_jours_statiques()
        with convertisseur_des_jours :
            # Définition des fonctions de conversion
            def semaine_to_an():
                st.session_state.jr_par_an_semaine = st.session_state.jr_par_semaine * round(4.33 * Solde_mois_de_travail, 2)

            def an_to_semaine():
                st.session_state.jr_par_semaine = st.session_state.jr_par_an_semaine / round(4.33 * Solde_mois_de_travail, 2)

            def mois_to_an():
                st.session_state.jr_par_an_mois = st.session_state.jr_par_mois * round(Solde_mois_de_travail, 2)

            def an_to_mois():
                st.session_state.jr_par_mois = st.session_state.jr_par_an_mois / round(Solde_mois_de_travail, 2)


            # Configuration de la grille pour positionner l'expander sur la moitié gauche
            cols = st.columns([1, 2])  # Crée 4 colonnes mais utilise seulement les deux premières pour les widgets
            with cols[0]:  # Utilise la première colonne large pour l'expander
                st.write("Note: Pour faire une conversion:")
                st.write("- Nb de jr/semaine * ", round(4.33 * Solde_mois_de_travail,2) ,'= Nb de jr/an')
                st.write("- Nb de jr/mois * ", round(Solde_mois_de_travail,2) ,'= Nb de jr/an')
            with cols[1]:
                with st.expander("Cliquez ici pour ajuster les conversions des jours", expanded=False):
                    col1, col2 = st.columns(2)  # Crée des sous-colonnes pour les entrées à l'intérieur de l'expander

                    with col1:
                        semaine = st.number_input("Entrez les jours statiques/semaine", key="jr_par_semaine", step=1.00, on_change=semaine_to_an)
                        st.markdown("---")  # Ajoute une ligne de séparation horizontale
                        mois = st.number_input("Entrez les jours statiques/mois", key="jr_par_mois", step=1.00, on_change=mois_to_an)

                    with col2:
                        an_semaine = st.number_input("Jours / an à partir de jours/semaine", key="jr_par_an_semaine", step=1.00, on_change=an_to_semaine)
                        st.markdown("---")  # Ajoute une ligne de séparation horizontale
                        an_mois = st.number_input("Jours / an à partir de jours/mois", key="jr_par_an_mois", step=1.00, on_change=an_to_mois)

            


        with conteneur_de_stats:
            # Set up columns for mission types
            col1, col2, col3= st.columns(3)
            with col1:
                
                st.metric(label="Total jours statiques par an", value=round(Solde_jours_statiques_par_an,2))

                #433
                
                Solde_jours_statiques_par_mois= Solde_jours_statiques_par_an/ (Solde_jours_de_travail_par_an/Solde_jours_de_travail_par_mois)
                st.metric(label="Total Jours Statiques par mois", value=round(Solde_jours_statiques_par_mois,2))
            
                #Solde_jours_statiques_par_semaine= Solde_jours_statiques_par_mois/(4.33)
                Solde_jours_statiques_par_semaine= Solde_jours_statiques_par_mois/(Solde_jours_de_travail_par_mois/4.33)
                
                st.metric(label="Total Jours Statiques par semaine", value=round(Solde_jours_statiques_par_semaine,2))
            
                
            with col2:    
                
                
                #attention normalement hna khas ykhrjo b7al b7al mni kdir round(....., 2)
                Solde_jours_NON_terrain_pourcent_par_an = (Solde_jours_statiques_par_an / Solde_jours_de_travail_par_an )*100  #Pourcentage
                st.metric(label="Solde jours NON terrain % par an", value=f"{round(Solde_jours_NON_terrain_pourcent_par_an, 2)} %")

                Solde_jours_NON_terrain_pourcent_par_mois = (Solde_jours_statiques_par_mois / Solde_jours_de_travail_par_mois)*100
                st.metric(label="Solde jours NON terrain % par mois", value=f"{round(Solde_jours_NON_terrain_pourcent_par_mois, 2)} %")

                #Solde_jours_NON_terrain_pourcent_par_semaine = (Solde_jours_statiques_par_semaine / 5 )*100 
                Solde_jours_NON_terrain_pourcent_par_semaine = (Solde_jours_statiques_par_semaine / 4.33 )*100 
                st.metric(label="Solde jours NON terrain % par semaine", value=f"{round(Solde_jours_NON_terrain_pourcent_par_semaine, 2)} %")
            with col3:
                Reste_solde_jours_terrain_pourcent_par_mois = 100 - Solde_jours_NON_terrain_pourcent_par_mois #Pourcentage
                st.metric(label="Reste Solde Jour Terrain % / mois", value=f"{round(Reste_solde_jours_terrain_pourcent_par_mois, 2)} %")
                #Attention Pourquoi ici j'affiche moins
            
        
        if 'ma_variable' not in st.session_state:
            st.session_state.Reste_solde_jours_terrain_pourcent_par_mois = Reste_solde_jours_terrain_pourcent_par_mois


        _ ="""
        "st.session_state object:", st.session_state
        # Run this using `streamlit run your_script.py`
        """


    if selected == "Détermination des visites possibles":
        #Les fonctions
        def get_field_value(field_name_in_database,valeur_par_defaut):
            # Exécuter une requête SQL pour récupérer la valeur du champ spécifique du premier commercial
            # attention: il a la requete madaztch bghito y afficher la valeur par deafut
            mycursor.execute(f'''SELECT `{field_name_in_database}`, COUNT(*) AS count 
                            FROM commercial 
                            GROUP BY `{field_name_in_database}`
                            ORDER BY count DESC LIMIT 1''')
            field_value = mycursor.fetchone()[0]  # Récupérer la valeur du champ spécifique du premier commercial
            return field_value if field_value is not None else valeur_par_defaut  # Utiliser valeur par défaut si la valeur est nulle


        # Top-level containers
        stats_container = st.container()



        # The layout with columns
        with stats_container:
            # You can adjust the ratios to match the Power BI layout
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                st.markdown('**CLIENTS**')

                _ ="""  mycursor.execute('''SELECT AVG(Solde_jours_de_travail_par_an) AS moyenne_jours_de_travail,
                                            AVG(Solde_jours_statiques_par_an) AS moyenne_jours_statiques
                                            FROM commercial''')
                        rows = mycursor.fetchall()
                        # Check if any rows are returned
                        if rows:
                            # Iterate through each row
                            for row in rows:
                                # Retrieve Solde_jours_de_travail_par_an and Solde_jours_statiques_par_an from the row
                                Solde_jours_de_travail_par_an = float(row[0])
                                Solde_jours_statiques_par_an = float(row[1])
                """    

                #hna ki9der ykoun Solde_jours_de_travail_par_an mkhtalf, lrequete katakhod directement valeur li kt3wd wa9ila  
                mycursor.execute('''SELECT Solde_jours_de_travail_par_an, Solde_jours_statiques_par_an
                                    FROM commercial''')
                rows = mycursor.fetchall()
                # Check if any rows are returned
                if rows:
                    # Iterate through each row
                    for row in rows:
                        # Retrieve Solde_jours_de_travail_par_an and Solde_jours_statiques_par_an from the row
                        Solde_jours_de_travail_par_an = float(row[0])
                        Solde_jours_statiques_par_an = float(row[1])
            
                Solde_jours_visite_terrain_par_an = Solde_jours_de_travail_par_an - Solde_jours_statiques_par_an
                print(Solde_jours_de_travail_par_an)
                print(Solde_jours_statiques_par_an)
                #Solde_jours_visite_terrain_par_an = 151.75
                st.metric(label="Solde jours terrain", value=round(Solde_jours_visite_terrain_par_an))
                Nombre_de_visite_client_par_jour = st.number_input("Nombre de Visite par jour", value=float(get_field_value('Nombre_de_visite_client_par_jour', 5.00)), step=1.00)

                Solde_visite_terrain_client_par_an = round(Nombre_de_visite_client_par_jour * Solde_jours_visite_terrain_par_an)
                st.metric(label="Visite terrain client par an", value=Solde_visite_terrain_client_par_an)

            with col2:
                st.markdown('**PROSPECTS**')
                Nombre_de_visite_prospects_par_jour = st.number_input('Visites Terrain Prospects par jour', value=float(get_field_value('Nombre_de_visite_prospects_par_jour',1.00)), step=0.25)
                
                Solde_visite_terrain_prospects_par_an = round(Solde_jours_visite_terrain_par_an * Nombre_de_visite_prospects_par_jour)
                st.metric(label="Visites terrain prospects par an", value=Solde_visite_terrain_prospects_par_an)
                #Pourcentage_des_visites_prospects = Solde_visite_terrain_prospects_par_an / Solde_visite_terrain_clients_et_prospects_par_an
                Pourcentage_des_visites_prospects = (Solde_visite_terrain_prospects_par_an / (Solde_visite_terrain_client_par_an+Solde_visite_terrain_prospects_par_an))*100
                st.metric(label="% Visites Prospects", value=f"{round(Pourcentage_des_visites_prospects,2)} %")

            with col3:
                st.markdown('**TOTAL VISITES CLIENTS/PROSPECTS**')
                Solde_visite_terrain_clients_et_prospects_par_an= round(Solde_visite_terrain_client_par_an+Solde_visite_terrain_prospects_par_an)
                st.metric(label="Totales Visites Clients + Prospects", value=Solde_visite_terrain_clients_et_prospects_par_an)
                
                

        # Define the function to save data to the database
        def save_to_database(Nombre_de_visite_client_par_jour,Nombre_de_visite_prospects_par_jour, client_visits, prospect_visits, percentage_prospects, total_visits):
            try:
                supprimer ="""  A Supprimer
                # Update the `calculs` table
                query_calculs = '''
                    UPDATE calculs
                    SET Solde_visite_terrain_client_par_an = %s, 
                        Solde_visite_terrain_prospects_par_an = %s,
                        Pourcentage_des_visites_prospects = %s,
                        Solde_visite_terrain_clients_et_prospects_par_an = %s
                    WHERE ID_Calculs = 1
                '''
                mycursor.execute(query_calculs, (client_visits, prospect_visits, percentage_prospects, total_visits))
                """
                query_commercial = '''
                    UPDATE commercial
                    SET `Nombre_de_visite_client_par_jour` = %s,
                        `Nombre_de_visite_prospects_par_jour` = %s,
                        `Solde_visite_terrain_client_par_an(Possibles)` = %s,
                        `Pourcentage_des_visites_prospects` = %s,
                        `Solde_visite_terrain_prospects_par_an(Possibles)` = %s,
                        `Nombres_de_visite_Commercial_par_an_(Possibles)` = %s,
                        `Statut_Commercial` = 0
                '''
                mycursor.execute(query_commercial, (Nombre_de_visite_client_par_jour,Nombre_de_visite_prospects_par_jour, client_visits, percentage_prospects, Solde_visite_terrain_prospects_par_an,total_visits))

                mydb.commit()
                if mycursor.rowcount > 0:
                    st.success(f"Data successfully updated in both tables for {mycursor.rowcount} commercial records!")
                else:
                    st.warning("No changes were made. The data provided might be the same as existing data.")
            except pymysql.Error as e:
                st.error(f"Failed to update data due to a database error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")


        # Assuming you've calculated these values somewhere above in the code
        Nombre_de_visite_client_par_jour = Nombre_de_visite_client_par_jour
        client_visits = Solde_visite_terrain_client_par_an
        prospect_visits = Solde_visite_terrain_prospects_par_an
        percentage_prospects = round(Pourcentage_des_visites_prospects, 2)
        total_visits = Solde_visite_terrain_clients_et_prospects_par_an







        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:

            # Add a button to save data
            if st.button('Enregistrer'):
                save_to_database(Nombre_de_visite_client_par_jour,Nombre_de_visite_prospects_par_jour, client_visits, prospect_visits, percentage_prospects, total_visits)

        with col2:
            # Données pour le diagramme
            my_labels = ['Clients', 'Prospects']
            sizes = [Solde_visite_terrain_client_par_an, Solde_visite_terrain_prospects_par_an]
            my_colors = ['#66b3ff', '#ff9999']  # Vous pouvez choisir des couleurs
            explode = (0.01, 0)  # "explode" un segment pour le mettre en évidence

            fig1, ax1 = plt.subplots(figsize=(2, 2))
            ax1.pie(sizes, labels=my_labels, explode=explode, colors=my_colors, autopct='%1.1f%%', startangle=90,textprops={'fontsize':8 , 'color': '#2e2c2c'} )
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            ax1.set_title('Répartition des visites clients/prospects' , loc='center',fontdict={'fontsize': 10})

            st.pyplot(fig1)

        p="""
        with col2:
            # Préparer les données pour plost
            df = pd.DataFrame({
                'category': ['Clients', 'Prospects'],
                'value': [Solde_visite_terrain_client_par_an, Solde_visite_terrain_prospects_par_an],
                'colors': ['#66b3ff', '#ff9999']
            })

            # Diagramme circulaire avec plost
            plost.pie_chart(
                data=df,
                theta='value',
                color='category',
                title='Répartition des visites (Clients vs Prospects)',
                legend='right',  # Position of the legend
                use_container_width=True  # Use the full width of the container
            )
        """

    
    if selected == "Commercial":
        
        st.header('Individualisation de remplissage des données pour les commerciaux')

        # Execute SQL query
        mycursor.execute("SELECT `Id_Commercial`, `Nom_Commercial`, `Jour_Conges`, `RTT`, `Recuperation`, `Jour_Feries`, `Autres_jours_non_travailles`, `Administration_Commercial`, `Supervision`, `Convention`, `TA_Hors_Secteur`, `Event_Salon`, `Formations`, `Autres_jours_mission_hors_visite_Commercial`  FROM `commercial`")
        result = mycursor.fetchall()

        # Create a DataFrame from the results
        df = pd.DataFrame(result, columns=['Id', 'Nom Commercial', 'Jour Conges', 'RTT', 'Récuperation', 'Jour Féries', 'Autres jours non travailles', 'Administration Commercial', 'Supervision/Management', 'Convention', 'TA Hors Secteur', 'Event Salon', 'Formations', 'Autres jours mission hors visite Commercial'])

        # Add a new column "is_widget" with default value False at the beginning of the DataFrame
        df.insert(0, "Checkbox", False)

        # Display using data editor
        st.write("", unsafe_allow_html=True)
        edited_df = st.data_editor(df, column_config={"Id_Commercial": st.column_config.NumberColumn(disabled=True),
                                                    "Nom Commercial": st.column_config.Column(disabled=True),
                                                    "Jour Conges": st.column_config.Column(disabled=True),
                                                    "RTT": st.column_config.Column(disabled=True),
                                                    "Jour Féries": st.column_config.Column(disabled=True),
                                                    "Autres jours non travailles": st.column_config.Column(disabled=True),
                                                    "Administration Commercial": st.column_config.Column(disabled=True),
                                                    "Supervision/Management": st.column_config.Column(disabled=True),
                                                    "Convention": st.column_config.Column(disabled=True),
                                                    "TA Hors Secteur": st.column_config.Column(disabled=True),
                                                    "Event Salon": st.column_config.Column(disabled=True),
                                                    "Formations": st.column_config.Column(disabled=True),
                                                    "Autres jours mission hors visite Commercial": st.column_config.Column(disabled=True),
                                                    },hide_index=True)

        #initialise variable to handle the problem of when you edit something on the 2nd table. The page rerun and all is gone
        if "button_modifier_state" not in st.session_state:
            st.session_state.button_modifier_state = False

        Modifier= st.button("Modifier")
        # Add a button to modify
        if Modifier or st.session_state.button_modifier_state:
            st.session_state.button_modifier_state = True
            
            # Get the selected commercial names
            selected_commercials = edited_df[edited_df["Checkbox"]]["Nom Commercial"].tolist()
            
            # Filter the DataFrame to display only selected commercials
            selected_df = df[df["Nom Commercial"].isin(selected_commercials)]
            # Remove the Checkbox column from the selected_df
            selected_df = selected_df.drop(columns=["Checkbox"])

            # Display another data editor with selected commercials
            st.write("<h2>Commerciaux sélectionnés :</h2>", unsafe_allow_html=True)
            edited_selected_df = st.data_editor(selected_df,hide_index=True,disabled=["Id"])


            Enregistrer= st.button("Enregistrer")
            if Enregistrer:
                try:
                    for index, row in edited_selected_df.iterrows():
                        # Perform calculations to get the updated values for Solde_jours_de_travail_par_an and Solde_jours_statiques_par_an
                        Jours_non_travailles_par_an = (row['Jour Conges'] + row['RTT'] + row['Récuperation'] + row['Jour Féries'] + row['Autres jours non travailles']) + 104
                        Solde_jours_de_travail_par_an = 365 - Jours_non_travailles_par_an
                        Solde_jours_statiques_par_an = (row['Administration Commercial'] + row['Supervision/Management'] + row['Convention'] + row['TA Hors Secteur'] + row['Event Salon'] + row['Formations'] + row['Autres jours mission hors visite Commercial'])


                        # Exécutez la requête UPDATE seulement pour les colonnes modifiées
                        query = """UPDATE commercial 
                                    SET Jour_Conges=%s, RTT=%s, Recuperation=%s, Jour_Feries=%s, Autres_jours_non_travailles=%s, Administration_Commercial=%s, Supervision=%s, Convention=%s, TA_Hors_Secteur=%s, Event_Salon=%s, Formations=%s, Autres_jours_mission_hors_visite_Commercial=%s, Solde_jours_de_travail_par_an=%s, Solde_jours_statiques_par_an=%s, Statut_Commercial=1
                                    WHERE Id_Commercial=%s""" 
                        values=(row['Jour Conges'], row['RTT'], row['Récuperation'], row['Jour Féries'], row['Autres jours non travailles'], row['Administration Commercial'], row['Supervision/Management'], row['Convention'], row['TA Hors Secteur'], row['Event Salon'], row['Formations'], row['Autres jours mission hors visite Commercial'], Solde_jours_de_travail_par_an, Solde_jours_statiques_par_an, row['Id'])
                        mycursor.execute(query, values)
                    # Validez les modifications dans la base de données
                    mydb.commit()
                    
                    # Affichez un message de succès
                    st.success(f"Updated {mycursor.rowcount} rows.")
                    if mycursor.rowcount >= 1:
                        st.success("Données modifiées avec succès dans la base de données.")
                        time.sleep(5)
                
                        # Actualisez la page
                        st.session_state.button_modifier_state = False
                        st.rerun()
                except Exception as e:
                    # En cas d'erreur, affichez un message d'erreur
                    st.error("Erreur lors de la modification des données dans la base de données: {}".format(e))

            Annuler= st.button("Annuler")
            if Annuler:
                st.session_state.button_modifier_state = False
                st.rerun()
                