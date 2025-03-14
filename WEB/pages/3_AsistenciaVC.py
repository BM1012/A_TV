import streamlit as st
import datetime as dt
import unicodedata
import time
import pandas as pd
import login as login
import os
from io import StringIO
import sqlitecloud
from github import Github, GithubException
from github.GithubException import BadCredentialsException

login.generarLogin()

if 'usuario' in st.session_state and 'area' in st.session_state:
    # Inicializar la lista de días en session_state si no existe
    if 'days' not in st.session_state:
        st.session_state['days'] = []

    opcion = ['Aprobar', 'No aprobar', 'Pendiente']
    ruta3 = 'sqlitecloud://cunzcmk2nk.g5.sqlite.cloud:8860/vacaciones.db?apikey=DqTdjbNqB1ExoI2O2wUZjmfPaH2dWpYD69q2irRWB5g'
    conexion = sqlitecloud.connect(ruta3)

    def carga_datos():
        """Cargar datos desde la base de datos y devolver un DataFrame de Pandas."""
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM vacaciones")
        rows = cursor.fetchall()
        # Obtener nombres de columnas
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)

    def verificar_duplicados(colaborador, fecha):
        """Verificar si ya existe un registro con el mismo COLABORADOR y FECHA."""
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM vacaciones WHERE COLABORADOR = ? AND FECHA = ?",
            (colaborador, fecha)
        )
        return cursor.fetchone()[0] > 0  # True si existe, False si no

    def actualizar_db(nuevos_datos):
        """Actualizar registros en la base de datos."""
        # Primero, obtenemos todos los registros existentes que podrían necesitar actualización
        cursor = conexion.cursor()
        colaboradores = tuple(nuevos_datos['COLABORADOR'].unique())
        fechas = tuple(nuevos_datos['FECHA'].unique())

        # Prevenir errores si solo hay un elemento en los tuples
        if len(colaboradores) == 1:
            colaboradores = f"('{colaboradores[0]}')"
        if len(fechas) == 1:
            fechas = f"('{fechas[0]}')"

        # Obtener los registros existentes en una sola consulta
        query = f"SELECT COLABORADOR, FECHA, ID FROM vacaciones WHERE COLABORADOR IN {colaboradores} AND FECHA IN {fechas}"
        cursor.execute(query)
        registros_existentes = {(row[0], row[1]): row[2]
                                for row in cursor.fetchall()}

        # Contar actualizaciones
        contador = 0

        # Actualizar solo los registros que cambiaron
        for _, fila in nuevos_datos.iterrows():
            clave = (fila['COLABORADOR'], fila['FECHA'])
            if clave in registros_existentes and registros_existentes[clave] != fila['ID']:
                cursor.execute(
                    "UPDATE vacaciones SET ID = ? WHERE COLABORADOR = ? AND FECHA = ?",
                    (fila['ID'], fila['COLABORADOR'], fila['FECHA'])
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
            if not verificar_duplicados(fila['COLABORADOR'], fila['FECHA']):
                cursor.execute(
                    "INSERT INTO vacaciones (COLABORADOR, AREA, FECHA, MES, ID, REGISTRO) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        fila['COLABORADOR'],
                        fila['AREA'],
                        fila['FECHA'],
                        fila['MES'],
                        fila['ID'],
                        fila['REGISTRO']
                    )
                )
        conexion.commit()
        st.success("Datos guardados correctamente")
        time.sleep(3)
        st.rerun()
    df_filtered = carga_datos()
    filtro1 = pd.DataFrame(df_filtered)
    filtro1['AREA'] = filtro1['AREA'].apply(lambda x: unicodedata.normalize(
        'NFKD', str(x)).encode('ASCII', 'ignore').decode('ASCII'))
    filtro2 = pd.DataFrame(df_filtered)
    filtro3 = pd.DataFrame(df_filtered)
    filtro2['AREA'] = filtro2['AREA'].replace(
        "AtenciÃ³n a clientes", 'Atencion a clientes')
    fecha_hora_actual = dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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
        "0", 'EN ESPERA DE CONFIRMACIÓN DE GERENTE')
    filtro1['ID'] = filtro1['ID'].replace("1", 'APROBADO')
    filtro1['ID'] = filtro1['ID'].replace(
        "2", 'EN ESPERA DE AUTORIZACION DE DIRECCIÓN')
    filtro1['ID'] = filtro1['ID'].replace("3", 'NO APROBADO')
    filtro1 = filtro1[['COLABORADOR', 'FECHA', 'MES', 'ID']]
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

    filtro2 = filtro2[filtro2['ID'] == "0"]

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        filtro2 = filtro2[['COLABORADOR', 'AREA',
                           'FECHA']]
    else:
        filtro2 = filtro2[['COLABORADOR',
                           'FECHA']]
    filtro2['AUTORIZACION'] = 'Pendiente'

    # SOLICITUDES DIRECCIÓN -----------------------------------------------------------

    filtro3 = filtro3[filtro3[
        'ID'] == "2"]
    filtro3 = filtro3[['COLABORADOR', 'AREA',
                       'FECHA']]
    filtro3['AUTORIZACION'] = 'Pendiente'

    # INTERFAZ -----------------------------------------------------------------------

    st.title("TRUST :grey[VALUE]")

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Vacaciones", "Estatus", 'Solicitudes Gerentes', 'Solicitudes a Dirección'])
    elif st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        tab1, tab2, tab3 = st.tabs(["Vacaciones", "Estatus", 'Solicitudes'])
    else:
        tab1, tab2 = st.tabs(["Vacaciones", "Estatus"])

    # SOLICITUD USUARIOS -------------------------------------------------------------

    with tab1:
        st.subheader("Solicitud de vacaciones")

        # Expander para la selección de fechas
        with st.expander("Seleccionar días de vacaciones", expanded=True):
            today = dt.datetime.now()
            next_year = today.year
            jan_1 = dt.date(today.year, today.month, today.day)
            dec_31 = dt.date(next_year, 12, 31)

            # Selección de fechas
            d = st.date_input(
                "Elige tus días que requieres de vacaciones",
                (jan_1, dt.date(next_year, today.month, today.day)),
                jan_1,
                dec_31,
                format="DD.MM.YYYY",
            )

            # Función para agregar días a la lista
            def agg_vac(days_list):
                if len(d) == 2:  # El usuario selecciona un rango de fechas
                    start_date, end_date = d
                    date_range = pd.date_range(start=start_date, end=end_date)
                    days_list.extend(date_range.strftime("%d/%m/%Y").tolist())
                    dias_semana = date_range.strftime('%A').tolist()
                    indices_a_eliminar = []

                    for i, dia in enumerate(dias_semana):
                        if dia.lower() in ['saturday', 'sunday']:
                            indices_a_eliminar.append(i)

                    for i in reversed(indices_a_eliminar):
                        if i < len(days_list):
                            days_list.pop(i)
                            dias_semana.pop(i)

                elif len(d) == 1:  # Si el usuario selecciona un solo día
                    days_list.append(d[0].strftime("%d/%m/%Y"))

                if 'vacaciones' not in st.session_state:
                    st.error(
                        "Es necesario iniciar correctamente la aplicación. Redirigiendo a la página de inicio...")
                    time.sleep(5)
                    # Redirigir a la página de inicio
                    st.switch_page("Inicio.py")
                elif len(days_list) > st.session_state['vacaciones']:
                    d_vac = st.session_state['vacaciones']
                    days_list.clear()
                    st.error(
                        f'Solo cuentas con: {d_vac} días disponibles, por favor selecciona un rango válido')
                else:
                    st.write(f"Los días que seleccionaste son: {days_list}")

            # Botón para agregar días
            if st.button("Agregar días"):
                agg_vac(st.session_state['days'])

        # Expander para mostrar las fechas seleccionadas
        with st.expander("Ver días seleccionados", expanded=True):
            # Mostrar los días seleccionados
            def d_seleccion():
                if st.session_state['days']:
                    st.write("Días seleccionados hasta ahora:",
                             st.session_state['days'])
                else:
                    # Mostrar mensaje si no hay días seleccionados
                    st.write("No se han seleccionado días aún.")
            d_seleccion()

            # Botón para limpiar la selección
            if st.button("Limpiar selección"):
                st.session_state['days'] = []  # Limpiar la lista de días
                st.rerun()  # Usar st.rerun() en lugar de experimental_rerun

        # Crear el diccionario con las fechas seleccionadas
        datos_dict = {
            "COLABORADOR": st.session_state['colab'],
            "AREA": unicodedata.normalize('NFKD', st.session_state['area']).encode('ASCII', 'ignore').decode('ASCII'),
            # Usar la lista de días de session_state
            "FECHA": st.session_state['days'],
            "MES": 'FEBRERO',
            # "MES": unicodedata.normalize('NFKD', mes).encode(
            #         'ASCII', 'ignore').decode('ASCII'),
            'ID': 0,
            "REGISTRO": fecha_hora_actual
        }

        nuevos_datos = pd.DataFrame([datos_dict])
        # Separar fechas en filas individuales
        nuevos_datos = nuevos_datos.explode('FECHA')

        if st.button("Guardar", key='Guardar-solicitud'):

            # Crear un DataFrame temporal para la comparación
            permi_temp = nuevos_datos[['COLABORADOR', 'FECHA']].copy()

            # Realizar un merge para encontrar coincidencias
            merged = permi_temp.merge(filtro1[['COLABORADOR', 'FECHA']], on=[
                                      'COLABORADOR', 'FECHA'], how='left', indicator=True)

            # Verificar si hay coincidencias
            if not merged[merged['_merge'] == 'both'].empty:  # Si el registro existe
                st.error(
                    'Ya existe el registro, por favor contacte con el administrador')
            else:
                if nuevos_datos['FECHA'].notna().any():
                    actualizar_db(nuevos_datos)
                else:
                    st.error('Por favor seleccione una opción valida')
    with tab2:
        st.subheader("Base de datos")
        st.dataframe(filtro1, use_container_width=True, hide_index=True)
    if st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera', 'clopez', 'bsanabria', 'lfortunato']:
        with tab3:
            st.subheader("Solicitudes pendientes")
            edited_df = st.data_editor(filtro2, column_config={
                "AUTORIZACION": st.column_config.SelectboxColumn("AUTORIZACION", options=opcion, help="Selecciona si autoriza la incidencia", default='Pendiente')}, disabled=["widgets"], hide_index=True, use_container_width=True)
            # Botón para guardar los cambios
            if st.button('Guardar', key='Guardar-ConfirmarG'):
                if not (edited_df['AUTORIZACION'] == 'Pendiente').all():

                    # try:
                    # Leer el archivo CSV desde GitHub
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

                    actualizar_db(df_filtered)
                else:
                    st.warning(
                        "No se seleccionó ninguna incidencia para autorizar.")
