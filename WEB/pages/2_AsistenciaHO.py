import streamlit as st
import datetime as dt
import unicodedata
import time
import pandas as pd
from io import StringIO
from github import Github
from github.GithubException import BadCredentialsException
import login as login
import calendar

login.generarLogin()

if 'usuario' in st.session_state and 'area' in st.session_state:

    days = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miercoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes'
    }

    opcion = ['Aprobar', 'No aprobar', 'Pendiente']
    url = 'https://raw.githubusercontent.com/BM1012/AsistenciasTV/main/Home_Office.csv'

    def carga_datos(link):
        return pd.read_csv(link, encoding='utf-8-sig')

    def acceso():
        try:
            token = st.secrets["github"]["token"]
            # Autentícate con GitHub
            g = Github(token)
            repo = g.get_repo("BM1012/AsistenciasTV")
            st.success("Conexión exitosa con el repositorio.")
            return repo
        except BadCredentialsException:
            st.error("Error de autenticación: Token inválido o vencido.")
        except Exception as e:
            st.error(f"Error inesperado: {e}")

    def actualizar_csv(repo, nuevos_datos):
        while True:
            try:
                # Leer el archivo actual
                contenido = repo.get_contents("Home_Office.csv")
                contenido_decodificado = contenido.decoded_content.decode(
                    'utf-8-sig')

                # Usar StringIO para simular un archivo
                df = pd.read_csv(
                    StringIO(contenido_decodificado), encoding='utf-8-sig')

                # Actualizar registros existentes
                for index, nueva_fila in nuevos_datos.iterrows():
                    condicion = (df['COLABORADOR'] == nueva_fila['COLABORADOR']) & \
                                (df['MES'] == nueva_fila['MES'])
                    if not df.loc[condicion].empty:  # Si el registro existe
                        df.loc[condicion, 'ID'] = nueva_fila['ID']
                    else:
                        df = pd.concat(
                            [df, nueva_fila.to_frame().T], ignore_index=True)

                # Subir la nueva versión
                repo.update_file(
                    path='Home_Office.csv',
                    message='Actualización automática del archivo',
                    content=df.to_csv(
                        index=False, encoding='utf-8-sig'),
                    sha=contenido.sha
                )
                st.success("Datos guardados correctamente")
                break
            except Exception as e:
                # Si hay un conflicto, reintentar después de 5 segundos
                st.warning(f"Error: {e}. Reintentando en 5 segundos...")
                time.sleep(5)

    df_filtered = carga_datos(url)
    filtro1 = pd.DataFrame(df_filtered)
    print(f'Este es el filtro1: {filtro1}')
    filtro1['AREA'] = filtro1['AREA'].apply(lambda x: unicodedata.normalize(
        'NFKD', str(x)).encode('ASCII', 'ignore').decode('ASCII'))
    filtro2 = pd.DataFrame(df_filtered)
    filtro3 = pd.DataFrame(df_filtered)
    filtro2['AREA'] = filtro2['AREA'].replace(
        "AtenciÃ³n a clientes", 'Atencion a clientes')
    fecha_hora_actual = dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    days = []

    # BASE DE DATOS -----------------------------------------------------------------

    if st.session_state['usuario'] in ['amendoza']:
        filtro1 = filtro1[filtro1['AREA'] == st.session_state['area']]
    elif st.session_state['usuario'] in ['aherrera']:
        filtro1 = filtro1[filtro1['AREA'] == "Tesoreria"]
    elif st.session_state['usuario'] in 'omoctezuma':
        filtro1 = filtro1[filtro1['AREA'] == "Atencion a clientes"]
    elif st.session_state['usuario'] in ['jreyes']:
        filtro1 = filtro1[filtro1['AREA'] == "Nominas"]
    elif st.session_state['usuario'] in ['molguin']:
        filtro1 = filtro1[filtro1['AREA'] == "Administracion y servicios"]
    elif st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        pass  # No necesita modificación
    else:
        filtro1 = filtro1[filtro1['COLABORADOR'] == st.session_state['colab']]

    filtro1['ID'] = filtro1['ID'].replace(
        0, 'EN ESPERA DE CONFIRMACIÓN DE GERENTE')
    filtro1['ID'] = filtro1['ID'].replace(
        1, 'APROBADO')
    filtro1['ID'] = filtro1['ID'].replace(
        2, 'EN ESPERA DE AUTORIZACION DE DIRECCIÓN')
    filtro1['ID'] = filtro1['ID'].replace(
        3, 'NO APROBADO')
    filtro1 = filtro1[['COLABORADOR',
                       'DIA 1', 'DIA 2', 'MES', 'ID']]
    filtro1 = filtro1.drop_duplicates()  # Elimina filas duplicadas

    # SOLICITUDES GERENTES -----------------------------------------------------------
    if st.session_state['usuario'] in ['amendoza', 'clopez', 'lfortunato']:
        filtro2 = filtro2[filtro2['AREA'] == st.session_state['area']]
    elif st.session_state['usuario'] in ['aherrera']:
        filtro2 = filtro2[filtro2['AREA'] == "Tesoreria"]
    elif st.session_state['usuario'] in 'omoctezuma':
        filtro2 = filtro2[filtro2['AREA'] == "Atencion a clientes"]
    elif st.session_state['usuario'] in ['jreyes']:
        filtro2 = filtro2[filtro2['AREA'] == "Nominas"]
    elif st.session_state['usuario'] in ['molguin']:
        filtro2 = filtro2[filtro2['AREA'] == "Administracion y servicios"]      

    filtro2 = filtro2[filtro2['ID'] == 0]

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        filtro2 = filtro2[['COLABORADOR', 'AREA',
                           'DIA 1', 'DIA 2']]
    else:
        filtro2 = filtro2[['COLABORADOR', 'MES',
                           'DIA 1', 'DIA 2']]
    filtro2['AUTORIZACION'] = 'Pendiente'

    # SOLICITUDES DIRECCIÓN -----------------------------------------------------------

    filtro3 = filtro3[filtro3[
        'ID'] == 2]
    filtro3 = filtro3[['COLABORADOR', 'AREA',
                       'DIA 1', 'DIA 2']]
    filtro3['AUTORIZACION'] = 'Pendiente'

    # INTERFAZ -----------------------------------------------------------------------

    st.title("TRUST :grey[VALUE]")

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Home Office", "Estatus", 'Solicitudes Gerentes', 'Solicitudes a Dirección'])
    elif st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        tab1, tab2, tab3 = st.tabs(["Home Office", "Estatus", 'Solicitudes'])
    else:
        tab1, tab2 = st.tabs(["Home Office", "Estatus"])

    # SOLICITUD USUARIOS -------------------------------------------------------------

    with tab1:
        st.subheader("Solicitud de Home Office")

        # Expander para la selección de fechas
        with st.expander("Seleccionar días de Home Office", expanded=True):

            today = dt.datetime.now()
            next_year = today.year
            jan_1 = dt.date(today.year, today.month, today.day)
            dec_31 = dt.date(next_year, 12, 31)

            # Obtener el año y mes actual
            año_actual = today.year
            mes_actual = today.month

            def obtener_fechas_dia(dia_seleccionado, año, mes):
                # Obtener el número del día de la semana
                dias = {'LUNES': 0, 'MARTES': 1,
                        'MIERCOLES': 2, 'JUEVES': 3, 'VIERNES': 4}
                dia_numero = dias[dia_seleccionado]

                # Obtener todas las fechas del mes
                fechas = []
                for dia in range(1, calendar.monthrange(año, mes)[1] + 1):
                    fecha = dt.date(año, mes, dia)
                    if fecha.weekday() == dia_numero:
                        fechas.append(fecha)

                # Filtrar fechas que son un día antes o después del 15 y el último día del mes
                fechas_filtradas = []
                for fecha in fechas:
                    if fecha.day != 14 and fecha.day != 16 and fecha != dt.date(año, mes, calendar.monthrange(año, mes)[1]):
                        fechas_filtradas.append(fecha)

                return fechas_filtradas

            # Selección de fechas
            if st.session_state['usuario'] not in ['amendoza', 'omoctezuma', 'jreyes', 'molguin', 'clopez', 'aherrera', 'lfortunato']:
                d = st.selectbox("Selecciona tu día de Home", options=[
                    "LUNES", 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES'])
                e = st.selectbox("Selecciona tu segundo día de Home", options=[
                    "LUNES", 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES'])

                fechas_d = obtener_fechas_dia(d, año_actual, mes_actual)
                fechas_e = obtener_fechas_dia(e, año_actual, mes_actual)
                fechas_correspondientes = fechas_d + fechas_e
                # Convertir las fechas a formato string para mostrar
                fechas_formateadas = [fecha.strftime(
                    "%d/%m/%Y") for fecha in fechas_correspondientes]

            else:
                d = st.selectbox("Selecciona tu día de Home", options=[
                    "LUNES", 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES'])
                e = ""
                fechas_correspondientes = obtener_fechas_dia(
                    d, año_actual, mes_actual)

            meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
                     "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
            mes = today.month
            if today.day < 22:
                mes = meses[mes - 1]
            else:
                mes = meses[mes]

            datos_dict = {
                "COLABORADOR": unicodedata.normalize('NFKD', st.session_state.colab).encode(
                    'ASCII', 'ignore').decode('ASCII'),
                "AREA": unicodedata.normalize('NFKD', st.session_state['area']).encode('ASCII', 'ignore').decode('ASCII'),
                # Usar la lista de días de session_state
                "MES": unicodedata.normalize('NFKD', mes).encode(
                    'ASCII', 'ignore').decode('ASCII'),
                "DIA 1": unicodedata.normalize('NFKD', d).encode(
                    'ASCII', 'ignore').decode('ASCII'),
                "DIA 2": unicodedata.normalize('NFKD', e).encode(
                    'ASCII', 'ignore').decode('ASCII'),
                'ID': 0,
                "REGISTRO": fecha_hora_actual
            }

            permi = pd.DataFrame([datos_dict])  # Crear DataFrame
        if st.button("Guardar", key='Guardar-solicitud'):
            repo = acceso()

            # Crear un DataFrame temporal para la comparación
            permi_temp = permi[['COLABORADOR', 'MES']].copy()

            # Realizar un merge para encontrar coincidencias
            merged = permi_temp.merge(filtro1[['COLABORADOR', 'MES']], on=[
                                      'COLABORADOR', 'MES'], how='left', indicator=True)

            # Verificar si hay coincidencias
            if not merged[merged['_merge'] == 'both'].empty:  # Si el registro existe
                st.error(
                    'Ya existe el registro, por favor contacte con el administrador')
            else:
                if permi['DIA 1'].notna().any():
                    actualizar_csv(repo, permi)
                else:
                    st.error('Por favor seleccione una opción valida')

    with tab2:
        st.subheader("Base de datos")
        st.dataframe(filtro1, use_container_width=True, hide_index=True)

    try:
        with tab3:
            st.subheader("Solicitudes pendientes")
            edited_df = st.data_editor(filtro2, column_config={
                "AUTORIZACION": st.column_config.SelectboxColumn("AUTORIZACION", options=opcion, help="Selecciona si autoriza la incidencia", default='Pendiente')}, disabled=["widgets"], hide_index=True, use_container_width=True)
            # Botón para guardar los cambios
            if st.button('Guardar', key='Guardar-ConfirmarG'):
                if not (edited_df['AUTORIZACION'] == 'Pendiente').all():

                    # Obtener los índices de las filas seleccionadas (donde el checkbox está activado)
                    filas_seleccionadas = edited_df[edited_df['AUTORIZACION']
                                                    == 'Aprobar'].index
                    filas_seleccionadas_2 = edited_df[edited_df['AUTORIZACION']
                                                      == 'No aprobar'].index
                    filas_seleccionadas_3 = edited_df[edited_df['AUTORIZACION']
                                                      == 'Pendiente'].index

                    # Actualizar los valores de 'ID' en df_filtered para las filas seleccionadas

                    df_filtered.loc[filas_seleccionadas, 'ID'] = 2
                    df_filtered.loc[filas_seleccionadas_2, 'ID'] = 3
                    df_filtered.loc[filas_seleccionadas_3, 'ID'] = 0

                    repo = acceso()
                    # Imprime las columnas del DataFrame
                    print(df_filtered.columns)
                    actualizar_csv(repo, df_filtered)

                else:
                    st.warning(
                        "No se seleccionó ninguna incidencia para autorizar.")
    except:
        print("No existe el bloque")

    try:
        with tab4:
            # df_filtered = carga_datos(url)
            st.subheader("Solicitudes pendientes")
            edited_df = st.data_editor(filtro3,  column_config={
                "AUTORIZACION": st.column_config.SelectboxColumn("AUTORIZACION", options=opcion, help="Selecciona si autoriza la incidencia", default='Pendiente')}, disabled=["widgets"], hide_index=True, key='BaseDire', use_container_width=True)
            # Botón para guardar los cambios
            if st.button('Guardar', key='Guardar-ConfirmarDR'):
                # Verificar si algún checkbox está seleccionado
                if not (edited_df['AUTORIZACION'] == 'Pendiente').all():

                    filas_seleccionadas = edited_df[edited_df['AUTORIZACION']
                                                    == 'Aprobar'].index
                    filas_seleccionadas_2 = edited_df[edited_df['AUTORIZACION']
                                                      == 'No aprobar'].index
                    filas_seleccionadas_3 = edited_df[edited_df['AUTORIZACION']
                                                      == 'Pendiente'].index

                    # Actualizar los valores de 'ID' en df_filtered para las filas seleccionadas

                    df_filtered.loc[filas_seleccionadas, 'ID'] = 1
                    df_filtered.loc[filas_seleccionadas_2, 'ID'] = 3
                    df_filtered.loc[filas_seleccionadas_3, 'ID'] = 2

                    # Guardar el archivo localmente

                    df_filtered.to_csv(
                        "PERMISOS.csv", index=False, encoding='utf-8-sig')

                    # Subir el archivo a GitHub

                    repo = acceso()
                    # Imprime las columnas del DataFrame
                    print(df_filtered.columns)
                    actualizar_csv(repo, df_filtered)
                else:
                    st.warning(
                        "No se seleccionó ninguna incidencia para autorizar.")
    except:
        print("No existe el bloque")
