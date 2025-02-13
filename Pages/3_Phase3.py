import streamlit as st
import mysql.connector
import pandas as pd
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import numpy as np
import seaborn

# Configuration de la page
st.set_page_config(layout="wide")
st.logo("Africa.png", icon_image="Logo.png")

# Connexion à la base de données
try:
    mydb = mysql.connector.connect(
        host='bjjvcnkquh3rdkwnqviv-mysql.services.clever-cloud.com',
            user='usbidjmhwyxcuar4',
            password='tQemqKFD6orQ1DLz4Xrl',
            port=3306,
            database='bjjvcnkquh3rdkwnqviv'
    )
    mycursor = mydb.cursor(buffered=True)
except mysql.connector.Error as e:
    st.error(f"Erreur de connexion à la base de données: {e}")

navbar=st.container()

with navbar:
    selected = option_menu(
        menu_title=None,
        options=["Analyse des résultats","Analyse par chef de marché"],
        icons=["house","book"], menu_icon="cast", default_index=0, orientation="horizontal"
    )

    if selected == "Analyse des résultats":
        #Faire un update des visites necessaires pour chaque commercial dans la base de données
        try:
            update_query = """
            UPDATE commercial c 
            JOIN chef_de_marche cdm ON c.ID_Chef_de_Marche = cdm.ID_Chef_de_Marche
            SET c.`Solde_visite_terrain_client_par_an(Necessaire)` = (
                SELECT SUM(cl.Nombre_de_visites_par_an)
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

            
        st.header("Analyse des résultats")
        # Charger tous les commerciaux pour le menu déroulant
        try:
            mycursor.execute("SELECT Nom_Commercial FROM commercial")
            all_commercials = [row[0] for row in mycursor.fetchall()]
            commercial_choices = st.multiselect("Choisir un ou plusieurs Commerciaux", all_commercials)
        except Exception as e:
            st.error(f"Erreur lors de la récupération des commerciaux: {e}")


        # Première requête SQL avec condition facultative pour le premier tableau
        #attention hna mzl n9ed nkhtasr kter par exemple n7yd les tables client w visite w ndir blast(cl.Nombre_de_visites_par_an) hadi (Solde_visite_terrain_client_par_an(Necessaire))
        query1 = """
        SELECT c.Nom_Commercial, 
            COUNT(distinct v.ID_Client) as Nombre_de_clients,
            SUM(cl.Nombre_de_visites_par_an) as Nombre_de_visites_necessaires,
            c.`Solde_visite_terrain_client_par_an(Possibles)` as Nombre_de_visites_possibles,
            SUM(cl.Nombre_de_visites_par_an) / NULLIF(c.`Solde_visite_terrain_client_par_an(Possibles)`, 0) as ETP
        FROM commercial c
        JOIN visite v ON c.Id_Commercial = v.Id_Commercial
        JOIN client cl ON v.ID_Client = cl.ID_Client
        """

        # Seconde requête SQL pour le tableau avec prospection
        query2 = """
        SELECT c.Nom_Commercial,
            SUM(cl.Nombre_de_visites_par_an) + c.`Solde_visite_terrain_prospects_par_an(Possibles)` AS Nombre_visites_avec_prospection,
            (SUM(cl.Nombre_de_visites_par_an) + c.`Solde_visite_terrain_prospects_par_an(Possibles)`) / c.`Nombres_de_visite_Commercial_par_an_(Possibles)` AS Nb_ETP_avec_Prospection
        FROM commercial c
        JOIN visite v ON c.Id_Commercial = v.Id_Commercial
        JOIN client cl ON v.ID_Client = cl.ID_Client
        """


        #filtrer selon le choix
        if commercial_choices:
            placeholders = ', '.join(['%s'] * len(commercial_choices))
            query1 += f" WHERE c.Nom_Commercial IN ({placeholders})"
            query2 += f" WHERE c.Nom_Commercial IN ({placeholders})"

        query1 += " GROUP BY c.Id_Commercial, c.Nom_Commercial, c.`Solde_visite_terrain_client_par_an(Possibles)`"
        query2 += " GROUP BY c.Id_Commercial, c.Nom_Commercial"


        #Totales_visites_possibles commande dyalha s7i7a w maktkhrjch
        # Requête pour récupérer les totaux supplémentaires
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
        # attention needs updates 
        if commercial_choices and "Tous les commerciaux" not in commercial_choices:
            query3 += f" WHERE c.Nom_Commercial IN ({placeholders})"
            query4 += f" WHERE c.Nom_Commercial IN ({placeholders})"

        # Exécution des requêtes et affichage des tableaux
        try:
            if commercial_choices:
                mycursor.execute(query1, commercial_choices)
                data1 = mycursor.fetchall()
                mycursor.execute(query2, commercial_choices)
                data2 = mycursor.fetchall()
                mycursor.execute(query3, commercial_choices)
                data3 = mycursor.fetchone()
                mycursor.execute(query4, commercial_choices)
                data4 = mycursor.fetchone()
                mycursor.execute(query_etp_count)
                count_etp_sup_1 = mycursor.fetchone()[0]  # Récupération du résultat
            else:
                mycursor.execute(query1)
                data1 = mycursor.fetchall()
                mycursor.execute(query2)
                data2 = mycursor.fetchall()
                mycursor.execute(query3)
                data3 = mycursor.fetchone()
                mycursor.execute(query4)
                data4 = mycursor.fetchone()
                mycursor.execute(query_etp_count)
                count_etp_sup_1 = mycursor.fetchone()[0]  # Récupération du résultat


            df1 = pd.DataFrame(data1, columns=["Nom Commercial", "Nombre de Clients", "Nombre de Visites Nécessaires", "Nombre de Visites Possibles", "ETP avant Prospection"])
            df1['KPI 1'] = df1['ETP avant Prospection'].apply(lambda x: "🟢" if 0.7 <= x <= 1 else "🔴")
            #st.write("Tableau des Commerciaux", df1)


            df2 = pd.DataFrame(data2, columns=['Nom Commercial', 'Nombre Visites avec Prospection', 'Nb ETP avec Prospection'])
            df2['KPI 2'] = df2['Nb ETP avec Prospection'].apply(lambda x: "🟢" if 0.7 <= x <= 1 else "🔴")
            #st.write("Tableau des Commerciaux avec Prospection", df2)


            # Fusion des dataframes sur la colonne 'Nom Commercial'
            combined_df = pd.merge(df1, df2, on='Nom Commercial', how='left')
            # Trier le DataFrame combiné par 'ETP avant Prospection' en ordre décroissant
            combined_df = combined_df.sort_values(by='ETP avant Prospection', ascending=False)

            st.write("Tableau Combiné", combined_df)



            col1, col2, col3 = st.columns(3)
            with col1:

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
                





            with col2:
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
                st.header("Visualisation des résultats")
                chart_choice = st.selectbox("Sélectionnez le graphique à afficher", ["Comparaison des Visites Nécessaires et Possibles" , "Distribution des ETP avant et après Prospection"], index=0)
                if chart_choice == "Distribution des ETP avant et après Prospection":
                    fig, ax = plt.subplots(figsize=(7, 3.5))
                    combined_df[['ETP avant Prospection', 'Nb ETP avec Prospection']].plot(kind='hist', bins=20, alpha=0.5, ax=ax)
                    ax.set_title('Distribution des ETP avant et après Prospection')
                    ax.set_xlabel('ETP')
                    ax.set_ylabel('Nombre de Commerciaux')
                    st.pyplot(fig)
                elif chart_choice == "Comparaison des Visites Nécessaires et Possibles":
                    fig, ax = plt.subplots(figsize=(7, 3.5))
                    ax.bar(['Visites Nécessaires', 'Visites Possibles'], [totales_visites_necessaires, totales_visites_possibles], color=['#4a4aff', '#ff6666'])
                    ax.set_title('Comparaison des Visites Nécessaires et Possibles')
                    ax.set_ylabel('Nombre de Visites')
                    st.pyplot(fig)


            # Graphique pour le Portefeuille Clients - Visites Nécessaires vs. Visites Possibles
            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.bar(df1['Nom Commercial'], df1['Nombre de Visites Nécessaires'], label='Visites Nécessaires', color='#4a4aff')
            ax.bar(df1['Nom Commercial'], df1['Nombre de Visites Possibles'], label='Visites Possibles', color='r', alpha=0.6)
            ax.set_xticklabels(df1['Nom Commercial'], rotation=70, ha='right', fontsize=4)
            ax.set_title('Nombre de Visites Nécessaires vs. Visites Possibles par Commercial', fontsize=8)
            ax.set_ylabel('Nombre de Visites', fontsize=8)
            ax.set_xlabel('Nom Commercial', fontsize=8)
            ax.legend(fontsize=5)
            plt.tight_layout()
            st.pyplot(fig)



            #TOP 5
            df1['ETP avant Prospection'] = pd.to_numeric(df1['ETP avant Prospection'], errors='coerce')  # convertit les valeurs non convertibles en NaN

            # Trier les données pour obtenir le top 5 avec les ETP avant prospection les plus hauts
            df_top_high = df1.nlargest(5, 'ETP avant Prospection')
            st.header("Top 5 - ETP avant Prospection les plus élevés:")
            df_top_high

            # Trier les données pour obtenir le top 5 avec les ETP avant prospection les plus bas
            df_top_low = df1.nsmallest(5, 'ETP avant Prospection')
            st.header("Top 5 - ETP avant Prospection les plus bas:")
            df_top_low


        except Exception as e:
            st.error(f"Erreur lors de l'exécution de la requête SQL: {e}")

        # Fermeture de la connexion
        mycursor.close()
        mydb.close()

        
    if selected == "Analyse par chef de marché":
        st.image("Africa.png", use_container_width=True)
        st.header("Comparatif par chefs de marchés")
        #Faire un update des visites necessaires pour chaque commercial dans la base de données
        try:
            update_query = """
            UPDATE commercial c 
            JOIN chef_de_marche cdm ON c.ID_Chef_de_Marche = cdm.ID_Chef_de_Marche
            SET c.`Solde_visite_terrain_client_par_an(Necessaire)` = (
                SELECT SUM(cl.Nombre_de_visites_par_an)
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

        # Modifier les requêtes pour inclure les chefs de marché
        query1 = """
        SELECT ch.Chef_de_Marche, c.Nom_Commercial, 
            COUNT(distinct v.ID_Client) as Nombre_de_clients,
            SUM(cl.Nombre_de_visites_par_an) as Nombre_de_visites_necessaires,
            c.`Solde_visite_terrain_client_par_an(Possibles)` as Nombre_de_visites_possibles,
            SUM(cl.Nombre_de_visites_par_an) / NULLIF(c.`Solde_visite_terrain_client_par_an(Possibles)`, 0) as ETP
        FROM commercial c
        JOIN visite v ON c.Id_Commercial = v.Id_Commercial
        JOIN client cl ON v.ID_Client = cl.ID_Client
        JOIN chef_de_marche ch ON c.ID_Chef_de_Marche = ch.ID_Chef_de_Marche
        GROUP BY ch.Chef_de_Marche, c.Nom_Commercial, c.`Solde_visite_terrain_client_par_an(Possibles)`
        ORDER BY ch.Chef_de_Marche, ETP DESC
        """

        query2 = """
        SELECT ch.Chef_de_Marche, c.Nom_Commercial,

            SUM(cl.Nombre_de_visites_par_an) + c.`Solde_visite_terrain_prospects_par_an(Possibles)` AS Nombre_visites_avec_prospection,
            (SUM(cl.Nombre_de_visites_par_an) + c.`Solde_visite_terrain_prospects_par_an(Possibles)`) / c.`Nombres_de_visite_Commercial_par_an_(Possibles)` AS Nb_ETP_avec_Prospection
        FROM commercial c
        JOIN visite v ON c.Id_Commercial = v.Id_Commercial
        JOIN client cl ON v.ID_Client = cl.ID_Client
        JOIN chef_de_marche ch ON c.ID_Chef_de_Marche = ch.ID_Chef_de_Marche
        GROUP BY ch.Chef_de_Marche, c.Nom_Commercial
        ORDER BY ch.Chef_de_Marche, c.Nom_Commercial
        """

        # Exécution des requêtes et traitement pour affichage par chef de marché
        try:
            mycursor.execute(query1)
            data1 = mycursor.fetchall()
            df1 = pd.DataFrame(data1, columns=["Chef de Marché", "Nom Commercial", "Nombre de Clients", "Nombre de Visites Nécessaires", "Nombre de Visites Possibles", "ETP avant Prospection"])
            df1['KPI 1'] = df1['ETP avant Prospection'].apply(lambda x: "🟢" if 0.7 <= x <= 1 else "🔴")

            mycursor.execute(query2)
            data2 = mycursor.fetchall()
            df2 = pd.DataFrame(data2, columns=["Chef de Marché", "Nom Commercial", "Nombre Visites avec Prospection", "Nb ETP avec Prospection"])
            df2['KPI 2'] = df2['Nb ETP avec Prospection'].apply(lambda x: "🟢" if 0.7 <= x <= 1 else "🔴")

            # Fusionner les DataFrames
            combined_df = pd.merge(df1, df2, on=["Chef de Marché", "Nom Commercial"], how='left')
            grouped_df = combined_df.groupby('Chef de Marché')

            for name, group in grouped_df:
                st.subheader(name)
                
                # Calculer les totaux et moyennes spécifiques
                totals = pd.DataFrame({
                    'Chef de Marché': ['Total'],
                    'Nom Commercial': [''],
                    'Nombre de Clients': [group['Nombre de Clients'].sum()],
                    'Nombre de Visites Nécessaires': [group['Nombre de Visites Nécessaires'].sum()],
                    'Nombre de Visites Possibles': [group['Nombre de Visites Possibles'].sum()],
                    'ETP avant Prospection': [group['ETP avant Prospection'].sum() / len(group)],
                    'Nombre Visites avec Prospection': [group['Nombre Visites avec Prospection'].sum()],
                    'Nb ETP avec Prospection': [group['Nb ETP avec Prospection'].sum() / len(group)]
                })
                
                # Calculer KPI 1 et KPI 2 pour les totaux
                totals['KPI 1'] = '🟢' if totals['ETP avant Prospection'].values[0] <= 1 else '🔴'
                totals['KPI 2'] = '🟢' if totals['Nb ETP avec Prospection'].values[0] <= 1 else '🔴'
                
                # Ajouter la ligne de totaux au groupe
                group_with_totals = pd.concat([group, totals]).reset_index(drop=True)
                
                st.write(group_with_totals)

        except Exception as e:
            st.error(f"Erreur lors de l'exécution de la requête SQL: {e}")
        finally:
            # Fermeture de la connexion
            mycursor.close()
            mydb.close()