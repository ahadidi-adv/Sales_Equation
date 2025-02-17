import streamlit as st
import pymysql
import pandas as pd
import io
import sshtunnel
import MySQLdb

# ✅ Set page layout to wide
st.set_page_config(layout="wide")

# ✅ Hide Streamlit UI elements
hide_streamlit_style = """
    <style>
    [data-testid="stToolbar"] {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ✅ Function to create SSH tunnel and connect to MySQL
def create_ssh_tunnel():
    """Creates an SSH tunnel and connects to MySQL."""
    try:
        sshtunnel.SSH_TIMEOUT = 15.0
        sshtunnel.TUNNEL_TIMEOUT = 15.0

        tunnel = sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='DataAdventAfrica',
            ssh_password='DataAdventPlusAfrica2025.',
            remote_bind_address=('DataAdventAfrica.mysql.pythonanywhere-services.com', 3306)
        )

        tunnel.start()

        mydb = MySQLdb.connect(
            user='DataAdventAfrica',
            passwd='advent2025admin',
            host='127.0.0.1',  # ✅ Localhost because of SSH tunneling
            port=tunnel.local_bind_port,  # ✅ Port forwarded through SSH
            db='DataAdventAfrica$calibrage120',
        )

        st.success("✅ Connected to MySQL successfully!")
        return mydb, tunnel  # ✅ Now properly inside a function

    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None, None  # ✅ Now properly inside a function

# ✅ Connect to MySQL via SSH Tunnel
try:
    mydb, tunnel = create_ssh_tunnel()
    if mydb:
        mycursor = mydb.cursor()

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

        # ✅ Display DataFrame
        st.write(df)

        # ✅ Create Excel output for download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
            writer.close()

        # ✅ Download button for Excel file
        st.download_button(
            label="📥 Télécharger le fichier Excel",
            data=output.getvalue(),
            file_name="Output_calibrage.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

except pymysql.MySQLError as e:
    st.error(f"❌ MySQL Error: {e}")

finally:
    # ✅ Close MySQL connection and SSH Tunnel properly
    if 'mydb' in locals() and mydb:
        mydb.close()
    if 'tunnel' in locals() and tunnel:
        tunnel.close()
    #st.success("🔴 MySQL and SSH Tunnel Closed.")
