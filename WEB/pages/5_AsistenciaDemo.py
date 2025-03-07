import streamlit as st
import unicodedata
import pandas as pd
import datetime as dt
import time
import login as login
from io import StringIO
from github import Github
from github.GithubException import BadCredentialsException

hoy = dt.datetime.now().strftime("%d/%m/%Y")
fecha_hora_actual = dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


login.generarLogin()


if 'usuario' in st.session_state and 'area' in st.session_state:
    # Configuración de Google Sheets
    opcion = ['Aprobar', 'No aprobar', 'Pendiente'
              ]

    url = 'https://raw.githubusercontent.com/BM1012/AsistenciasTV/main/PERMISOS.csv'

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

    # Función para actualizar el archivo CSV en GitHub

    def actualizar_csv(repo, nuevos_datos):
        while True:
            try:
                # Leer el archivo actual
                contenido = repo.get_contents("PERMISOS.csv")
                contenido_decodificado = contenido.decoded_content.decode(
                    'utf-8-sig')

                # Usar StringIO para simular un archivo
                df = pd.read_csv(
                    StringIO(contenido_decodificado), encoding='utf-8-sig')

                # Actualizar registros existentens
                for index, nueva_fila in nuevos_datos.iterrows():
                    condicion = (df['COLABORADOR'] == nueva_fila['COLABORADOR']) & \
                        (df['FECHA'] == nueva_fila['FECHA']) & \
                        (df['CONCEPTO'] == nueva_fila['CONCEPTO'])

                    if df[condicion].any().any():  # Si el registro existe
                        df.loc[condicion, 'ID'] = nueva_fila['ID']
                        # Debug
                        print(
                            f"Actualizando ID para: {nueva_fila['COLABORADOR']} - {nueva_fila['FECHA']}")
                    else:
                        df = pd.concat(
                            [df, nueva_fila.to_frame().T], ignore_index=True)

                # Subir la nueva versión
                repo.update_file(
                    path='PERMISOS.csv',
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
    filtro2 = pd.DataFrame(df_filtered)
    filtro3 = pd.DataFrame(df_filtered)
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
            'ID': 0
        }

        permi = pd.DataFrame([datos_dict])  # Corregido: envolver en una lista

        def show_warning():
            st.warning(
                body='Los datos guardados, se enviaron correctamente para su confirmación')

        # df_filtered = carga_datos(url)
        # df = pd.DataFrame([datos_dict])
        # df_completo = pd.concat([df_filtered, df], ignore_index=True)

        if st.button("Guardar", key='Guardar-solicitud'):
            repo = acceso()
            actualizar_csv(repo, permi)

            # try:
            #     repo = acceso()
            #     with open('PERMISOS.csv', 'r', encoding='latin-1') as file:
            #         content = file.read()
            #         estatus = content

            #     repo.update_file(
            #         path='PERMISOS.csv',
            #         message='Actualización automatica del archivo',
            #         content=content,
            #         # Obtener el SHA del archivo actual
            #         sha=repo.get_contents("PERMISOS.csv").sha

            #     )
            #     st.success("Datos guardados correctamente")

            # except Exception as e:
            #     st.error(f"Error al subir el archivo: {e}")

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
                # Verificar si algún checkbox está seleccionado
                # Verifica si algún valor en la columna 'ID' es True
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

                    # Verificar que las filas seleccionadas no estén vacías
                    if not filas_seleccionadas.empty:
                        df_filtered.loc[filas_seleccionadas, 'ID'] = 2
                    if not filas_seleccionadas_2.empty:
                        df_filtered.loc[filas_seleccionadas_2, 'ID'] = 3
                    if not filas_seleccionadas_3.empty:
                        df_filtered.loc[filas_seleccionadas_3, 'ID'] = 0

                    # Guardar el archivo localmente

                    df_filtered.to_csv(
                        "PERMISOS.csv", index=False, encoding='utf-8-sig')

                    # Subir el archivo a GitHub
                    repo = acceso()
                    actualizar_csv(repo, df_filtered)
                    # with open('PERMISOS.csv', 'r', encoding='latin-1') as file:
                    #     content = file.read()

                    # repo.update_file(
                    #     path='PERMISOS.csv',
                    #     message='Actualización automática del archivo',
                    #     content=content,
                    #     # Obtener el SHA del archivo actual
                    #     sha=repo.get_contents("PERMISOS.csv").sha)
                    # st.success("Datos guardados correctamente")
                    # except Exception as e:
                    #     st.error(f"Error al subir el archivo: {e}")
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

                    # try:
                    # Leer el archivo CSV desde GitHub
                    # carga_datos(url)

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

                    repo = acceso()
                    actualizar_csv(repo, df_filtered)
                    # with open('PERMISOS.csv', 'r', encoding='latin-1') as file:
                    #     content = file.read()

                    # repo.update_file(
                    #     path='PERMISOS.csv',
                    #     message='Actualización automática del archivo',
                    #     content=content,
                    #     # Obtener el SHA del archivo actual
                    #     sha=repo.get_contents("PERMISOS.csv").sha)
                    # st.success("Datos guardados correctamente")
                    # except Exception as e:
                    #     st.error(f"Error al subir el archivo: {e}")
                else:
                    st.warning(
                        "No se seleccionó ninguna incidencia para autorizar.")
    except:
        print("No existe el bloque")
