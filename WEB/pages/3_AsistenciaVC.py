import streamlit as st
import datetime as dt
import unicodedata
import time
import pandas as pd
from io import StringIO
from github import Github
from github.GithubException import BadCredentialsException
import login as login

login.generarLogin()

if 'usuario' in st.session_state and 'area' in st.session_state:
    # Inicializar la lista de días en session_state si no existe
    if 'days' not in st.session_state:
        st.session_state['days'] = []

    opcion = ['Aprobar', 'No aprobar', 'Pendiente']
    url = 'https://raw.githubusercontent.com/BM1012/AsistenciasTV/main/Vacaciones.csv'

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
                contenido = repo.get_contents("Vacaciones.csv")
                contenido_decodificado = contenido.decoded_content.decode(
                    'utf-8-sig')

                # Usar StringIO para simular un archivo
                df = pd.read_csv(
                    StringIO(contenido_decodificado), encoding='utf-8-sig')

                # Actualizar registros existentes
                for index, nueva_fila in nuevos_datos.iterrows():
                    condicion = (df['COLABORADOR'] == nueva_fila['COLABORADOR']) & \
                                (df['FECHA'] == nueva_fila['FECHA'])
                    if not df.loc[condicion].empty:  # Si el registro existe
                        df.loc[condicion, 'ID'] = nueva_fila['ID']
                    else:
                        df = pd.concat(
                            [df, nueva_fila.to_frame().T], ignore_index=True)

                # Subir la nueva versión
                repo.update_file(
                    path='Vacaciones.csv',
                    message='Actualización automática del archivo',
                    content=df.to_csv(index=False, encoding='utf-8-sig'),
                    sha=contenido.sha
                )
                st.success("Datos guardados correctamente")
                break
            except Exception as e:
                st.warning(f"Error: {e}. Reintentando en 5 segundos...")
                time.sleep(5)

    df_filtered = carga_datos(url)
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
        0, 'EN ESPERA DE CONFIRMACIÓN DE GERENTE')
    filtro1['ID'] = filtro1['ID'].replace(1, 'APROBADO')
    filtro1['ID'] = filtro1['ID'].replace(
        2, 'EN ESPERA DE AUTORIZACION DE DIRECCIÓN')
    filtro1['ID'] = filtro1['ID'].replace(3, 'NO APROBADO')
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

    filtro2 = filtro2[filtro2['ID'] == 0]

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        filtro2 = filtro2[['COLABORADOR', 'AREA',
                           'FECHA']]
    else:
        filtro2 = filtro2[['COLABORADOR',
                           'FECHA']]
    filtro2['AUTORIZACION'] = 'Pendiente'

    # SOLICITUDES DIRECCIÓN -----------------------------------------------------------

    filtro3 = filtro3[filtro3[
        'ID'] == 2]
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

                if len(days_list) > st.session_state['vacaciones']:
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
            'ID': 0,
            "REGISTRO": fecha_hora_actual
        }

        permi = pd.DataFrame([datos_dict])  # Crear DataFrame
        permi = permi.explode('FECHA')

        if st.button("Guardar", key='Guardar-solicitud'):
            repo = acceso()
            if permi['FECHA'].notna().any():
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
                        "PERMISOS.csv", index=False, encoding='latin-1')

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
