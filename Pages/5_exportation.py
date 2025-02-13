import streamlit as st
import mysql.connector
import pandas as pd
import io

# Set page layout to wide
st.set_page_config(layout="wide")

# Establish a connection to MySQL Server
try:
    mydb = mysql.connector.connect(
        host='bjjvcnkquh3rdkwnqviv-mysql.services.clever-cloud.com',
            user='usbidjmhwyxcuar4',
            password='tQemqKFD6orQ1DLz4Xrl',
            port=3306,
            database='bjjvcnkquh3rdkwnqviv'
    )
    mycursor = mydb.cursor(buffered=True)
    st.success("Connection Established")

    # Requête pour obtenir tous les commerciaux
    mycursor.execute("SELECT DISTINCT Nom_Commercial FROM commercial")
    all_commercials = mycursor.fetchall()
    commercial_list = [i[0] for i in all_commercials]

    # Widget multiselect pour choisir les commerciaux
    selected_commercials = st.multiselect('Choisir les commerciaux', commercial_list)

    # Requête SQL pour récupérer les données en fonction des commerciaux sélectionnés
    query = f"""
    SELECT 
        com.Nom_Commercial, 
        com.`Solde_visite_terrain_client_par_an(Possibles)`, 
        com.`Solde_visite_terrain_prospects_par_an(Possibles)`, 
        cli.Nom_Client, 
        cli.Nombre_de_visites_par_an, 
        cli.Code_Client, 
        cli.Region_Client, 
        cli.Code_Postal, 
        cli.Ville_Client, 
        cli.Pays_Client, 
        cli.Circuit_Client, 
        cli.Activite_Client, 
        cli.Potentiel_Client, 
        cli.Fidelisation_Client, 
        cli.CA_Client, 
        cli.Couche, 
        cli.Regle_Prod
    FROM commercial com
    JOIN visite vis ON com.Id_Commercial = vis.Id_Commercial
    JOIN client cli ON vis.ID_Client = cli.ID_Client
    """
    if selected_commercials:
        commercial_placeholders = ', '.join(['%s'] * len(selected_commercials))
        query += f" WHERE com.Nom_Commercial IN ({commercial_placeholders})"
        mycursor.execute(query, selected_commercials)
    else:
        mycursor.execute(query)

    result = mycursor.fetchall()
    
    # Convertir les résultats en DataFrame
    df = pd.DataFrame(result, columns=[
        'Nom_Commercial', 'Solde_visite_terrain_client_par_an(Possibles)',
        'Solde_visite_terrain_prospects_par_an(Possibles)', 'Nom_Client',
        'Nombre_de_visites_par_an', 'Code_Client', 'Region_Client',
        'Code_Postal', 'Ville_Client', 'Pays_Client', 'Circuit_Client',
        'Activite_Client', 'Potentiel_Client', 'Fidelisation_Client',
        'CA_k_Client', 'Couche', 'Regle_Prod'
    ])
    
    # Affichage du DataFrame
    st.write(df)

    # Bouton pour exporter en Excel
    output = io.BytesIO()
    xlsx_data = df.to_excel(output, index=False)
    st.download_button(
        label="Télécharger le fichier Excel",
        data=output.getvalue(),
        file_name="Output outil calibrage.xlsx",
        mime="application/vnd.ms-excel"
    )

except mysql.connector.Error as e:
    st.error(f"Error connecting to MySQL Server: {e}")