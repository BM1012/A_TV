import streamlit as st
import datetime as dt
import unicodedata
import time
import pandas as pd
from io import StringIO
from github import Github
import sqlitecloud
import login as login
import calendar
import os  

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
    ruta2 = 'sqlitecloud://cunzcmk2nk.g5.sqlite.cloud:8860/home_office.db?apikey=DqTdjbNqB1ExoI2O2wUZjmfPaH2dWpYD69q2irRWB5g'
    conexion = sqlitecloud.connect(ruta2)

    def carga_datos():
        """Cargar datos desde la base de datos y devolver un DataFrame de Pandas."""
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM home_office")
        rows = cursor.fetchall()
        
        # Obtener nombres de columnas
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)

    def verificar_duplicados(colaborador, mes):
        """Verificar si ya existe un registro con el mismo COLABORADOR y FECHA."""
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM home_office WHERE COLABORADOR = ? AND MES = ?",
            (colaborador, mes)
        )
        return cursor.fetchone()[0] > 0 

    def actualizar_db(nuevos_datos):
        """Actualizar registros en la base de datos."""
        
        # Primero, obtenemos todos los registros existentes que podrían necesitar actualización
        cursor = conexion.cursor()
        colaboradores = tuple(nuevos_datos['COLABORADOR'].unique())
        fechas = tuple(nuevos_datos['MES'].unique())

        # Prevenir errores si solo hay un elemento en los tuples
        if len(colaboradores) == 1:
            colaboradores = f"('{colaboradores[0]}')"
        if len(fechas) == 1:
            fechas = f"('{fechas[0]}')"

        # Obtener los registros existentes en una sola consulta
        query = f"SELECT COLABORADOR, MES, ID FROM home_office WHERE COLABORADOR IN {colaboradores} AND MES IN {fechas}"
        cursor.execute(query)
        registros_existentes = {(row[0], row[1]): row[2]
                                for row in cursor.fetchall()}

        # Contar actualizaciones
        contador = 0

        # Actualizar solo los registros que cambiaron
        for _, fila in nuevos_datos.iterrows():
            clave = (fila['COLABORADOR'], fila['MES'])
            if clave in registros_existentes and registros_existentes[clave] != fila['ID']:
                cursor.execute(
                    "UPDATE home_office SET ID = ? WHERE COLABORADOR = ? AND MES = ?",
                    (fila['ID'], fila['COLABORADOR'], fila['MES'])
                )
                contador += 1

        conexion.commit()
        st.success("Datos guardados correctamente")
        time.sleep(3)
        st.rerun()

    def insertar_db(nuevos_datos):
        """Insertar o actualizar registros en la base de datos."""
        cursor = conexion.cursor()
        for _, fila in nuevos_datos.iterrows():
            if not verificar_duplicados(fila['COLABORADOR'], fila['MES']):
                cursor.execute(
                    "INSERT INTO home_office (COLABORADOR, AREA, MES, PERIODO, MES_FECHA, DIA_1, DIA_2,  ID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        fila['COLABORADOR'],
                        fila['AREA'],
                        fila['MES'],
                        fila['PERIODO'],
                        fila['MES_FECHA'],
                        fila['DIA_1'],
                        fila['DIA_2'],
                        fila['ID']
                    )
                )
        conexion.commit()
        st.success("Datos guardados correctamente")
        time.sleep(5)
        st.rerun()

    df_filtered = carga_datos()
    filtro1 = pd.DataFrame(df_filtered)
    filtro1['ID'] = pd.to_numeric(filtro1['ID'], errors='coerce')
    filtro1['AREA'] = filtro1['AREA'].apply(lambda x: unicodedata.normalize(
        'NFKD', str(x)).encode('ASCII', 'ignore').decode('ASCII'))
    filtro2 = pd.DataFrame(df_filtered)
    filtro2['ID'] = pd.to_numeric(filtro2['ID'], errors='coerce')
    filtro3 = pd.DataFrame(df_filtered)
    filtro3['ID'] = pd.to_numeric(filtro3['ID'], errors='coerce')
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
                       'DIA_1', 'DIA_2', 'MES', 'ID']]
    filtro1 = filtro1.drop_duplicates()

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
                           'DIA_1', 'DIA_2']]
    else:
        filtro2 = filtro2[['COLABORADOR', 'MES',
                           'DIA_1', 'DIA_2']]
    filtro2['AUTORIZACION'] = 'Pendiente'

    # SOLICITUDES DIRECCIÓN -----------------------------------------------------------

    filtro3 = filtro3[filtro3[
        'ID'] == 2]
    filtro3 = filtro3[['COLABORADOR', 'AREA',
                       'DIA_1', 'DIA_2']]
    filtro3['AUTORIZACION'] = 'Pendiente'

    # INTERFAZ -----------------------------------------------------------------------

    st.title("TRUST :grey[VALUE]")

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        tab1, tab2, tab4 = st.tabs(
            ["Home Office", "Estatus", 'Solicitudes Dirección'])
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
                "MES": meses[(today.month - 1)] if today.day < 17 else meses[today.month],
                "PERIODO": "2025",
                "MES_FECHA": today.month if today.day < 17 else (today.month + 1),
                "DIA_1": unicodedata.normalize('NFKD', d).encode(
                    'ASCII', 'ignore').decode('ASCII'),
                "DIA_2": unicodedata.normalize('NFKD', e).encode(
                    'ASCII', 'ignore').decode('ASCII'),
                'ID': 0 if st.session_state['usuario'] not in ['amendoza', 'omoctezuma', 'jreyes', 'molguin', 'clopez', 'aherrera', 'asanabria', 'ogallegos', 'dcamacho', 'bsanabria', 'jgalvez'] else 2
            }

            permi = pd.DataFrame([datos_dict])  # Crear DataFrame
        if st.button("Guardar", key='Guardar-solicitud'):

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
                if permi['DIA_1'].notna().any():
                    insertar_db(permi)
                else:
                    st.error('Por favor seleccione una opción valida')

    with tab2:
        st.subheader("Base de datos")
        st.dataframe(filtro1, use_container_width=True, hide_index=True)

    if st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        with tab3:
            st.subheader("Solicitudes pendientes")
            edited_df = st.data_editor(filtro2, column_config={
                "AUTORIZACION": st.column_config.SelectboxColumn("AUTORIZACION", options=opcion, help="Selecciona si autoriza la incidencia", default='Pendiente')}, disabled=["widgets"], hide_index=True, use_container_width=True)
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

                    # Subir el archivo 
                    actualizar_db(df_filtered)

                else:
                    st.warning(
                        "No se seleccionó ninguna incidencia para autorizar.")
    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
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

                    # Subir el archivo a GitHub
                    actualizar_db(df_filtered)
                else:
                    st.warning(
                        "No se seleccionó ninguna incidencia para autorizar.")
