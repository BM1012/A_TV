import streamlit as st
import unicodedata
import pandas as pd
import datetime as dt
import time
import login as login
from io import StringIO
import sqlitecloud

hoy = dt.datetime.now().strftime("%d/%m/%Y")
fecha_hora_actual = dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


login.generarLogin()


if 'usuario' in st.session_state and 'area' in st.session_state:
    # Configuración de Google Sheets
    opcion = ['Aprobar', 'No aprobar', 'Pendiente'
              ]
    ruta = 'sqlitecloud://cunzcmk2nk.g5.sqlite.cloud:8860/permisos.db?apikey=DqTdjbNqB1ExoI2O2wUZjmfPaH2dWpYD69q2irRWB5g'
    conexion = sqlitecloud.connect(ruta)

    def carga_datos():
        """Cargar datos desde la base de datos y devolver un DataFrame de Pandas."""
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM permisos")
        rows = cursor.fetchall()
        # Obtener nombres de columnas
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)

    # Función para actualizar el archivo CSV en GitHub

    def verificar_duplicados(colaborador, mes):
        """Verificar si ya existe un registro con el mismo COLABORADOR y FECHA."""
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM permisos WHERE COLABORADOR = ? AND FECHA = ?",
            (colaborador, mes)
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
        query = f"SELECT COLABORADOR, FECHA, ID FROM permisos WHERE COLABORADOR IN {colaboradores} AND FECHA IN {fechas}"
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
                    "UPDATE permisos SET ID = ? WHERE COLABORADOR = ? AND FECHA = ?",
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
                    "INSERT INTO permisos (COLABORADOR, AREA, FECHA, CONCEPTO, DETALLE, REGISTRO, ID) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        fila['COLABORADOR'],
                        fila['AREA'],
                        fila['FECHA'],
                        fila['CONCEPTO'],
                        fila['DETALLE'],
                        fila['REGISTRO'],
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
    filtro2 = pd.DataFrame(df_filtered)
    filtro2['ID'] = pd.to_numeric(filtro2['ID'], errors='coerce')    
    filtro3 = pd.DataFrame(df_filtered)
    filtro3['ID'] = pd.to_numeric(filtro3['ID'], errors='coerce')
    filtro2['AREA'] = filtro2['AREA'].replace(
        "AtenciÃ³n a clientes", 'Atencion a clientes')

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
        # Aquí podrías agregar lógica para estos usuarios si es necesario
        pass  # No necesita modificación
    else:
        filtro1 = filtro1[filtro1['COLABORADOR'] == st.session_state['colab']]

    filtro1['ID'] = filtro1['ID'].replace(
        0, 'EN ESPERA DE CONFIRMACIÓN DE GERENTE')
    filtro1['ID'] = filtro1['ID'].replace(
        1, 'APROBADO')
    filtro1['ID'] = filtro1['ID'].replace(
        2, 'EN ESPERA DE CONFIRMACIÓN DE DIRECCIÓN')
    filtro1['ID'] = filtro1['ID'].replace(3, 'NO AUTORIZADO')
    filtro1 = filtro1[['COLABORADOR',
                       'FECHA', 'CONCEPTO', 'DETALLE', 'ID']]
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
                           'FECHA', 'CONCEPTO', 'DETALLE']]
    else:
        filtro2 = filtro2[['COLABORADOR',
                           'FECHA', 'CONCEPTO', 'DETALLE']]
    filtro2['AUTORIZACION'] = 'Pendiente'

    # SOLICITUDES DIRECCIÓN -----------------------------------------------------------

    filtro3 = filtro3[filtro3[
        'ID'] == 2]
    filtro3 = filtro3[['COLABORADOR', 'AREA',
                       'FECHA', 'CONCEPTO', 'DETALLE']]
    filtro3['AUTORIZACION'] = 'Pendiente'

    # INTERFAZ -----------------------------------------------------------------------

    st.title("TRUST :grey[VALUE]")

    print(st.session_state['usuario'])
    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Incidencias", "Estatus", 'Solicitudes Gerentes', 'Solicitudes a Dirección'])
    elif st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        tab1, tab2, tab3 = st.tabs(
            ["Incidencias", "Estatus", 'Solicitudes'])
    else:
        tab1, tab2 = st.tabs(
            ["Incidencias", "Estatus"])

    # SOLICITUD USUARIOS -------------------------------------------------------------

    with tab1:

        st.subheader("Envío de incidencias")

        today = dt.datetime.now()
        next_year = today.year
        jan_1 = dt.date(today.year, today.month, today.day)
        dec_31 = dt.date(next_year, 12, 31)
        fecha_hora_actual = dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        d = st.date_input(
            "Elige el día de la incidencia", min_value=today,
            format="DD.MM.YYYY"
        )

        e = st.selectbox("Selecciona la opción deseada:", options=[
                         'ENFERMEDAD', 'FALLECIMIENTO DIRECTO', 'FALLECIMIENTO INDIRECTO', 'MATERNIDAD', 'PATERNIDAD', 'MOTIVOS PERSONALES', 'CASOS FORTUITOS'])

        c = st.text_input("Justifica tu solicitud: ")

        c = unicodedata.normalize('NFKD', c).encode(
            'ASCII', 'ignore').decode('ASCII')

        datos_dict = {
            # Guardar el nombre directamente
            "COLABORADOR": st.session_state['colab'],
            # Guardar la opción directamente
            # Aplicar normalización
            "AREA": unicodedata.normalize('NFKD', st.session_state['area']).encode('ASCII', 'ignore').decode('ASCII'),
            # Guardar las fechas seleccionadas
            "FECHA": d.strftime(format="%d/%m/%Y"),
            "CONCEPTO": e,     # Guardar el concepto
            'DETALLE': c,
            "REGISTRO": fecha_hora_actual,  # Columna de fecha y hora
            'ID': 0 if st.session_state['usuario'] not in ['amendoza', 'omoctezuma', 'jreyes', 'molguin', 'clopez', 'aherrera', 'asanabria', 'ogallegos', 'dcamacho', 'bsanabria', 'jgalvez'] else 2
        }

        nuevos_datos = pd.DataFrame([datos_dict])
        # Separar fechas en filas individuales
        nuevos_datos = nuevos_datos.explode('FECHA')

        if st.button("Guardar", key='Guardar-solicitud'):
            if nuevos_datos['FECHA'].notna().any():
                insertar_db(nuevos_datos)
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
            # Botón para guardar los cambios
            if st.button('Guardar', key='Guardar-ConfirmarG'):
                # Verificar si algún checkbox está seleccionado
                # Verifica si algún valor en la columna 'ID' es True
                if not (edited_df['AUTORIZACION'] == 'Pendiente').all():

                    filas_seleccionadas = edited_df[edited_df['AUTORIZACION']
                                                    == 'Aprobar'].index
                    filas_seleccionadas_2 = edited_df[edited_df['AUTORIZACION']
                                                      == 'No aprobar'].index
                    filas_seleccionadas_3 = edited_df[edited_df['AUTORIZACION']
                                                      == 'Pendiente'].index
                    # Verificar que las filas seleccionadas no estén vacías
                    if not filas_seleccionadas.empty:
                        df_filtered.loc[filas_seleccionadas, 'ID'] = 2
                    if not filas_seleccionadas_2.empty:
                        df_filtered.loc[filas_seleccionadas_2, 'ID'] = 3
                    if not filas_seleccionadas_3.empty:
                        df_filtered.loc[filas_seleccionadas_3, 'ID'] = 0

                    # Imprime las columnas del DataFrame
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
                    # Obtener los índices de las filas seleccionadas (donde el checkbox está activado)
                    filas_seleccionadas = edited_df[edited_df['AUTORIZACION']
                                                    == 'Aprobar'].index
                    filas_seleccionadas_2 = edited_df[edited_df['AUTORIZACION']
                                                      == 'No aprobar'].index
                    filas_seleccionadas_3 = edited_df[edited_df['AUTORIZACION']
                                                      == 'Pendiente'].index

                    # Actualizar los valores de 'ID' en df_filtered para las filas seleccionadas

                    if not filas_seleccionadas.empty:
                        df_filtered.loc[filas_seleccionadas, 'ID'] = 1
                    if not filas_seleccionadas_2.empty:
                        df_filtered.loc[filas_seleccionadas_2, 'ID'] = 3
                    if not filas_seleccionadas_3.empty:
                        df_filtered.loc[filas_seleccionadas_3, 'ID'] = 2

                    # Guardar el archivo localmente

                    df_filtered.to_csv(
                        "PERMISOS.csv", index=False, encoding='utf-8-sig')

                    # Subir el archivo a GitHub

                    actualizar_db(df_filtered)
                else:
                    st.warning(
                        "No se seleccionó ninguna incidencia para autorizar.")
