import streamlit as st
import datetime as dt
import pandas as pd
import login as login

login.generarLogin()

if 'usuario' in st.session_state and 'area' in st.session_state:

    opcion = ['Aprobar', 'No aprobar', 'Pendiente'
              ]

    url = 'https://raw.githubusercontent.com/BM1012/AsistenciasTV/main/PERMISOS.csv'

    df_filtered = pd.read_csv(url, encoding='latin-1')
    filtro1 = pd.DataFrame(df_filtered)

    df_filtered = pd.read_csv(url, encoding='latin-1')

    filtro1['ID'] = filtro1['ID'].replace(
        0, 'EN ESPERA DE CONFIRMACIÓN DE GERENTE')
    filtro1['ID'] = filtro1['ID'].replace(
        1, 'EN ESPERA DE CONFIRMACIÓN DE DIRECCIÓN')
    filtro1['ID'] = filtro1['ID'].replace(2, 'APROBADO')
    filtro1 = filtro1[['COLABORADOR', 'FECHA', 'CONCEPTO', 'DETALLE', 'ID']]
    filtro1['AUTORIZACION'] = 'Pendiente'

    st.dataframe(filtro1, use_container_width=True, hide_index=True)

    # prueba = st.selectbox('Selecciona la opcion', options=filtro1['OPCIONES'])

    edited_df = st.data_editor(filtro1, column_config={"AUTORIZACION": st.column_config.SelectboxColumn(
        'AUTORIZACIÓN', options=opcion, help='Selecciona si autoriza la incidencia')})
