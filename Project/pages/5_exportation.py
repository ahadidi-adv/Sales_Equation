import streamlit as st
import pymysql
import pandas as pd
import io

# Set page layout to wide
st.set_page_config(layout="wide")
hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Database connection settings
DB_HOST = "bjjvcnkquh3rdkwnqviv-mysql.services.clever-cloud.com"
DB_USER = "usbidjmhwyxcuar4"
DB_PASSWORD = "tQemqKFD6orQ1DLz4Xrl"
DB_PORT = 3306
DB_NAME = "bjjvcnkquh3rdkwnqviv"

# Establish a connection to MySQL Server
try:
    mydb = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        database=DB_NAME
    )
    mycursor = mydb.cursor()
    st.success("✅ Connection Established")

    # Fetch all distinct commercial names
    mycursor.execute("SELECT DISTINCT Nom_Commercial FROM commercial")
    all_commercials = mycursor.fetchall()
    commercial_list = [i[0] for i in all_commercials]

    # Multiselect widget for choosing commercials
    selected_commercials = st.multiselect('Choisir les commerciaux', commercial_list)

    # SQL query to fetch data based on selected commercials
    query = """
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

    # Convert query results to a Pandas DataFrame
    df = pd.DataFrame(result, columns=[
        'Nom_Commercial', 'Solde_visite_terrain_client_par_an(Possibles)',
        'Solde_visite_terrain_prospects_par_an(Possibles)', 'Nom_Client',
        'Nombre_de_visites_par_an', 'Code_Client', 'Region_Client',
        'Code_Postal', 'Ville_Client', 'Pays_Client', 'Circuit_Client',
        'Activite_Client', 'Potentiel_Client', 'Fidelisation_Client',
        'CA_Client', 'Couche', 'Regle_Prod'
    ])

    # Display DataFrame
    st.write(df)

    # Create Excel output for download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
        writer.close()

    # Download button for Excel file
    st.download_button(
        label="📥 Télécharger le fichier Excel",
        data=output.getvalue(),
        file_name="Output_calibrage.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

except pymysql.MySQLError as e:
    st.error(f"❌ Error connecting to MySQL Server: {e}")

finally:
    if 'mydb' in locals() and mydb.open:
        mydb.close()
