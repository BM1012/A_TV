import streamlit as st
import pandas as pd
import unicodedata
import datetime

dfusuarios = pd.read_csv('/mount/src/a_tv/WEB/PASS-ST.csv')

usuarios_permitidos = ['lfortunato', 'clopez', 'bsanabria',
                       'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']

hoy = datetime.datetime.now()


def validar_usuario(usuario, clave):

    if len(dfusuarios[(dfusuarios['User'] == usuario) & (dfusuarios['Password'] == clave)]) > 0:
        return True
    else:
        return False


def generarMenu(usuario):
    url = 'https://raw.githubusercontent.com/BM1012/AsistenciasTV/main/PERMISOS.csv'
    url2 = 'https://raw.githubusercontent.com/BM1012/AsistenciasTV/main/Vacaciones.csv'
    url3 = 'https://raw.githubusercontent.com/BM1012/AsistenciasTV/main/Home_Office.csv'

    df_filtered = pd.read_csv(url, encoding='latin-1')
    df_filtered2 = pd.read_csv(url2, encoding='latin-1')
    df_filtered3 = pd.read_csv(url3, encoding='utf-8-sig')

    # Inicializar variables
    num_coincidencias_gerentes = 0
    num_coincidencias_directores = 0
    num_coincidencias_gerentesVC = 0
    num_coincidencias_directoresVC = 0

    # ARREGLO POR ACENTOS ------------------------------
    if st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        df_filtered['AREA'] = df_filtered['AREA'].replace(
            'Tesoreria', 'Tesorería')
        df_filtered['AREA'] = df_filtered['AREA'].replace(
            "Atencion a clientes", 'Atención a clientes')
        df_filtered['AREA'] = df_filtered['AREA'].replace(
            "Nominas", 'Nóminas')
        df_filtered['AREA'] = df_filtered['AREA'].replace(
            "Administracion y servicios", 'Administración y servicios')
        df_filtered2['AREA'] = df_filtered2['AREA'].replace(
            "Atencion a clientes", 'Atención a clientes')
        df_filtered2['AREA'] = df_filtered2['AREA'].replace(
            'Tesoreria', 'Tesorería')
        df_filtered2['AREA'] = df_filtered2['AREA'].replace(
            "Nominas", 'Nóminas')
        df_filtered2['AREA'] = df_filtered2['AREA'].replace(
            "Administracion y servicios", 'Administración y servicios')
        df_filtered3['AREA'] = df_filtered3['AREA'].replace(
            "Atencion a clientes", 'Atención a clientes')
        df_filtered3['AREA'] = df_filtered3['AREA'].replace(
            'Tesoreria', 'Tesorería')
        df_filtered3['AREA'] = df_filtered3['AREA'].replace(
            "Nominas", 'Nóminas')
        df_filtered3['AREA'] = df_filtered3['AREA'].replace(
            "Administracion y servicios", 'Administración y servicios')

        df_filtered = df_filtered[df_filtered['AREA']
                                  == st.session_state['area']]
        df_filtered2 = df_filtered2[df_filtered2['AREA']
                                    == st.session_state['area']]
        df_filtered3 = df_filtered3[df_filtered3['AREA']
                                    == st.session_state['area']]
        num_coincidencias_gerentes = (df_filtered['ID'] == 0).sum()
        num_coincidencias_gerentesVC = (df_filtered2['ID'] == 0).sum()
        num_coincidencias_gerentesHO = (df_filtered3['ID'] == 0).sum()

    if st.session_state['usuario'] in ['clopez', 'lfortunato', 'bsanabria']:
        df_filteredG = df_filtered[df_filtered['AREA']
                                   == st.session_state['area']]
        df_filtered2G = df_filtered2[df_filtered2['AREA']
                                     == st.session_state['area']]
        df_filtered3G = df_filtered3[df_filtered3['AREA']
                                     == st.session_state['area']]
        num_coincidencias_gerentes = (df_filteredG['ID'] == 0).sum()
        num_coincidencias_gerentesVC = (df_filtered2G['ID'] == 0).sum()
        num_coincidencias_gerentesHO = (df_filtered3G['ID'] == 0).sum()
        num_coincidencias_directores = (df_filtered['ID'] == 2).sum()
        num_coincidencias_directoresVC = (df_filtered2['ID'] == 2).sum()
        num_coincidencias_directoresHO = (df_filtered3['ID'] == 2).sum()

    with st.sidebar:
        st.image(
            "/mount/src/a_tv/WEB/Captura de pantalla 2025-02-14 171552.png", use_container_width=True)
        usuario_df = dfusuarios[(dfusuarios['User'] == usuario)]
        nombre = usuario_df['Ejecutivo'].iloc[0]
        st.write(f'Usuario: **:blue-background[{nombre}]** ')
        st.write(f"Fecha: **:blue-background[{hoy.strftime('%d/%m/%Y')}]** ")
        if st.session_state['usuario'] in usuarios_permitidos:
            st.page_link('Inicio.py', label='Inicio', icon="🏠")
        st.subheader("Asistencia")
        st.page_link('pages/1_Asistencia.py', label="Dashboard", icon="📊")
        if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
            if (num_coincidencias_directoresHO > 0) or (num_coincidencias_gerentesHO > 0):
                st.page_link('pages/2_AsistenciaHO.py',
                             label=f":red[Home Office ({int(num_coincidencias_directoresHO) + int(num_coincidencias_gerentesHO)})]", icon="❗")
            else:
                st.page_link('pages/2_AsistenciaHO.py',
                             label="Home Office", icon="💻")
        elif st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
            if num_coincidencias_gerentesHO > 0:
                st.page_link('pages/2_AsistenciaHO.py',
                             label=f":red[Home Office ({num_coincidencias_gerentesHO})]", icon="❗")
            else:
                st.page_link('pages/2_AsistenciaHO.py',
                             label="Home Office", icon="💻")
        else:
            st.page_link('pages/2_AsistenciaHO.py',
                         label="Home Office", icon="💻")
        if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
            if (num_coincidencias_directoresVC > 0) or (num_coincidencias_gerentesVC > 0):
                st.page_link('pages/3_AsistenciaVC.py',
                             label=f":red[Vacaciones ({int(num_coincidencias_directoresVC) + int(num_coincidencias_gerentesVC)})]", icon="❗")
            else:
                st.page_link('pages/3_AsistenciaVC.py',
                             label="Vacaciones", icon="🏖️")
        elif st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
            if num_coincidencias_gerentesVC > 0:
                st.page_link('pages/3_AsistenciaVC.py',
                             label=f":red[Vacaciones ({num_coincidencias_gerentesVC})]", icon="❗")
            else:
                st.page_link('pages/3_AsistenciaVC.py',
                             label="Vacaciones", icon="🏖️")
        else:
            st.page_link('pages/3_AsistenciaVC.py',
                         label="Vacaciones", icon="🏖️")

        if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
            if (num_coincidencias_directores > 0) or (num_coincidencias_gerentes > 0):
                st.page_link('pages/5_AsistenciaDemo.py',
                             label=f":red[Incidencias ({int(num_coincidencias_directores) + int(num_coincidencias_gerentes)})]", icon="❗")
            else:
                st.page_link('pages/5_AsistenciaDemo.py',
                             label="Incidencias", icon="😷")
        elif st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
            if num_coincidencias_gerentes > 0:
                st.page_link('pages/5_AsistenciaDemo.py',
                             label=f":red[Incidencias ({num_coincidencias_gerentes})]", icon="❗")
            else:
                st.page_link('pages/5_AsistenciaDemo.py',
                             label="Incidencias", icon="😷")
        else:
            st.page_link('pages/5_AsistenciaDemo.py',
                         label="Incidencias", icon="😷")
        # st.subheader("Evaluaciones")
        btn_salir = st.button("Salir")
        if btn_salir:
            st.session_state.clear()
            st.rerun()


def generarLogin():

    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario'])
    else:
        with st.form('frmLogin'):
            st.title("TRUST :grey[VALUE]")
            parUsuario = st.text_input('Usuario')
            parPassword = st.text_input('Password', type="password")
            btnLogin = st.form_submit_button('Ingresar', type="primary")
            if btnLogin:
                usuario_df = dfusuarios[dfusuarios['User'] == parUsuario]
                if usuario_df.empty:
                    st.error('Usuario no encontrado',
                             icon=':material/gpp_maybe:')
                else:
                    usuario_df = dfusuarios[(dfusuarios['User'] == parUsuario)]
                    area = usuario_df['Area'].iloc[0]
                    colab = usuario_df['Ejecutivo'].iloc[0]
                    nombre = usuario_df['Ejecutivo'].iloc[0]
                    if validar_usuario(parUsuario, parPassword):
                        st.session_state['usuario'] = parUsuario
                        st.session_state['colab'] = colab
                        st.session_state['area'] = area
                        st.session_state['Nombre'] = nombre
                        usuario_df = dfusuarios[dfusuarios['User']
                                                == parUsuario]
                        st.session_state['Ingreso'] = usuario_df['Ingreso'].iloc[0]
                        st.session_state['Tomados'] = usuario_df['Tomados'].iloc[0]
                        if parUsuario not in usuarios_permitidos:
                            st.switch_page("pages/1_Asistencia.py")
                        else:
                            st.switch_page("Inicio.py")
                    else:
                        st.error('Usuario o clave incorrecto',
                                 icon=':material/gpp_maybe:')
