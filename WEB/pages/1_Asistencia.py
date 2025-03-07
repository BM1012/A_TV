import streamlit as st
import utils
import pandas as pd
import datetime
from datetime import timedelta
import plotly.express as px
import matplotlib.pyplot as plt
import login as login

st.set_page_config(
    page_title="MiAppTV",  # Titulo de la pagina
    layout="wide",  # Forma de layout ancho o compacto
    initial_sidebar_state="expanded")  # Definimos si el sidebar aparece expandido o colapsado

# Colores del fondo
backgroundColor = st.get_option('theme.secondaryBackgroundColor')
textColor = st.get_option('theme.textColor')

# Aplicando colores CSS
utils.local_css('/mount/src/asistenciastv/WEB/estilos.css', backgroundColor)

login.generarLogin()

if 'usuario' in st.session_state and 'area' in st.session_state:
    gsheet = '1DISw0wlrkcy76HPD7lGDrZ49yhK69jVJiIgF29tRFYo'
    sheetid = '0'
    url = f'https://docs.google.com/spreadsheets/d/{gsheet}/export?format=csv&gid={sheetid}&format'

    sheetid = '583896735'
    urlho = f'https://docs.google.com/spreadsheets/d/{gsheet}/export?format=csv&gid={sheetid}&format'

    sheetid = '1662268283'
    urlvc = f'https://docs.google.com/spreadsheets/d/{gsheet}/export?format=csv&gid={sheetid}&format'

    sheetid = '1613484335'
    urlhr = f'https://docs.google.com/spreadsheets/d/{gsheet}/export?format=csv&gid={sheetid}&format'

    mes_actual = datetime.datetime.now().month

    ghdf = 'https://raw.githubusercontent.com/BM1012/AsistenciasTV/main/Vacaciones.csv'

    def carga_datos(link):
        return pd.read_csv(link, encoding='utf-8-sig')

    GitVacs = carga_datos(ghdf)

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        pass
    elif st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        GitVacs = GitVacs[GitVacs['AREA'] == st.session_state['area']]        
    else:
        GitVacs = GitVacs[GitVacs['COLABORADOR'] == st.session_state['Nombre']]

    GitVacs = GitVacs[GitVacs['ID'] == 1]

    GitVacs = GitVacs.groupby(by='COLABORADOR', as_index=False)[
        'ID'].count()

    # DataFrame
    df = pd.read_csv(url)
    df2 = pd.read_csv(urlho)
    df3 = pd.read_csv(urlvc)
    df4 = pd.read_csv(urlhr)

    days = {
        'Monday': 'LUNES',
        'Tuesday': 'MARTES',
        'Wednesday': 'MIÉRCOLES',
        'Thursday': 'JUEVES',
        'Friday': 'VIERNES',
        'Saturday': 'SABADO',
        'Sunday': 'DOMINGO'
    }

    vcc = {
        (1, 1.99): 12,
        (2, 2.99): 14,
        (3, 3.99): 16,
        (4, 4.99): 18,
        (5, 5.99): 20,
        (6, 10.99): 22,
        (11, 15.99): 24,
        (16, 20.99): 26,
        (21, 25.99): 28,
        (26, 30.99): 30,
        (31, 50): 32
    }

    df3['FECHA'] = pd.to_datetime(df3['FECHA'])
    df['FECHA'] = pd.to_datetime(df['FECHA'])
    df['HORA REGISTRO EN…'] = df['HORA REGISTRO EN…'].replace('-', None)
    df['HORA REGISTRO SAL…'] = df['HORA REGISTRO SAL…'].replace('-', None)
    df['HORA REGISTRO EN…'] = pd.to_datetime(
        df['HORA REGISTRO EN…'], errors='coerce').dt.time
    df['REGISTRO'] = pd.to_datetime(
        df['REGISTRO'], errors='coerce').dt.time
    df['QUINCENAS'] = pd.to_numeric(df['QUINCENAS'], errors='coerce')
    df['R. EXCEDIDO'] = pd.to_numeric(df['R. EXCEDIDO'], errors='coerce')

    hoy = pd.to_datetime(datetime.datetime.now())
    dia_semana = days[hoy.strftime('%A')]

    # Filtro por área

    if st.session_state['usuario'] not in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        df_filtered = df[df['NOMBRE'] == st.session_state['Nombre']]
    elif st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        df_filtered = df
    else:
        df_filtered = df[df['ÁREA'] == st.session_state['area']]

    if st.session_state['usuario'] not in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        dfho = df2[(df2['MES FECHA'] == mes_actual)]
        dfho = dfho[(dfho['DÍA 1'] == dia_semana) |
                    (dfho['DÍA 2'] == dia_semana)]
    if st.session_state['usuario']in ['lfortunato', 'clopez', 'bsanabria']:    
        dfho = df2
    else:
        dfho = df2[(df2['ÁREA'] == st.session_state['area'])]

    if st.session_state['usuario'] not in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        dfvc = df3  # [(df3['EJECUTIVO'] == st.session_state['Nombre'])]
        dfvc = dfvc[dfvc['FECHA'] > (hoy - timedelta(days=1))]
    elif st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria']:
        dfvc = df3    
    else:
        dfvc = df3[(df3['AREA'] == st.session_state['area'])]

    dfvc = dfvc[['EJECUTIVO', 'MES', 'FECHA']]
    dfvc['FECHA'] = dfvc['FECHA'].dt.date

    dfvc = dfvc.sort_values(by='FECHA', ascending=True)

    dfho = dfho[['EJECUTIVO', 'MES', 'DÍA 1', 'DÍA 2']]

    if st.session_state['usuario'] in ['omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        dfhr = df4[(df4['ÁREA'] == st.session_state['area'])] 
    else:
        dfhr = df4

    # Suma de vacaciones tomadas

    with st.sidebar:
        if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
            ejecutivo = st.selectbox(
                label='Colaboradores', options=['Selecciona un colaborador'] + df_filtered['NOMBRE'].unique().tolist(), index=0)
        mes = st.selectbox(
            label='Mes', options=['Selecciona un mes'] + df_filtered['MES'].unique().tolist(), index=0)

    # FILTROS
    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        if ejecutivo != 'Selecciona un colaborador':
            df_filtered = df_filtered[df_filtered['NOMBRE'] == ejecutivo]
            dfho = dfho[dfho['EJECUTIVO'] == ejecutivo]
            dfvc = dfvc[dfvc['EJECUTIVO'] == ejecutivo]
            dfhr = dfhr[dfhr['EJECUTIVO'] == ejecutivo]

    if mes != 'Selecciona un mes':
        df_filtered = df_filtered[df_filtered['MES'] == mes]
        if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
            dfho = dfho[dfho['MES'] == mes]
            dfvc = dfvc[dfvc['MES'] == mes]

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        if ejecutivo == 'Selecciona un colaborador':
            ingreso = dfhr[(dfhr['ÁREA'] == st.session_state['area'])]
        else:
            ingreso = dfhr[(dfhr['EJECUTIVO'] == ejecutivo)]
    else:
        ingreso = dfhr[(dfhr['EJECUTIVO'] == st.session_state['Nombre'])]
    # Asegúrate de que ingreso sea de tipo fecha
    ingreso = pd.to_datetime(ingreso['INGRESO'], format='%d/%m/%Y')

    quincenas = df_filtered[df_filtered['QUINCENAS'] == 1]
    quincenas_agrupadas = quincenas.groupby(
        'NOMBRE', as_index=False)['FECHA'].agg(list)
    quincenas['FECHA'] = quincenas['FECHA'].dt.date
    quincenas['QUINCENAS'] = ("Sin registros de entrada")
    quincenas = quincenas[['NOMBRE', 'FECHA', 'QUINCENAS']]
    # quincenas = quincenas.sort_values(by='FECHA', ascending=False)

    detailAsis = df_filtered[['NOMBRE', 'FECHA', 'HORA REGISTRO EN…',
                              'R. EXCEDIDO', 'TOLERANCIA', 'RETARDOS', 'REGISTRO']]

    # Base de datos // TAB 2
    dfnew = df_filtered[['NOMBRE', 'FECHA', 'MES', 'HO', 'TOLERANCIA',
                         'HORA REGISTRO EN…', 'HORA REGISTRO SAL…',  'RETARDOS']]
    dfnew['FECHA'] = dfnew['FECHA'].dt.date

    vt = round(pd.to_numeric(
        df_filtered['VACACIONES TOMADAS'], errors='coerce').sum(), 2)

    df_filtered = df_filtered.dropna(subset=['HORA REGISTRO EN…'])
    hightR = df_filtered[['FECHA',
                          'NOMBRE', 'HORA REGISTRO EN…', 'R. EXCEDIDO']]

    # CALCULO DE TIEMPO EXCEDENTE
    excedente = df_filtered[['NOMBRE', 'R. EXCEDIDO']]
    # excedente = excedente[excedente['R. EXCEDIDO'] > 0]
    excedente = round(excedente.groupby('NOMBRE', as_index=False)[
        'R. EXCEDIDO'].mean(), 0)
    excedente = excedente.sort_values(by='R. EXCEDIDO', ascending=False)
    excedente['R. EXCEDIDO'] = excedente['R. EXCEDIDO'].astype(str) + \
        ' Minutos excedidos promediados'

    if ingreso.dt.month.iloc[0] == hoy.month and ingreso.dt.day.iloc[0] == hoy.day:
        vt = 0  # Establecer vt a 0 si es el aniversario

    # Leer el archivo CSV PASS-ST
    # Asegúrate de proporcionar la ruta correcta
    df_pass_st = pd.read_csv('/mount/src/asistenciastv/WEB/PASS-ST.csv')

    # Filtrar por el área en st.session_state

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:

        if ejecutivo == 'Selecciona un colaborador':
            vtgh = GitVacs['ID'].sum()
            total_tomados = df_pass_st[df_pass_st['Area'] ==
                                       st.session_state['area']]['Tomados'].sum()
            vt = vt + total_tomados + vtgh
        else:
            total_tomados = df_pass_st[df_pass_st['Ejecutivo'] ==
                                       ejecutivo]['Tomados'].sum()
            vtgh = GitVacs[GitVacs['COLABORADOR'] == ejecutivo]['ID'].sum()
            vt = vt + total_tomados + vtgh

    else:
        vt = vt + st.session_state['Tomados']

    dfhr = dfhr[['EJECUTIVO', 'ENTRADA', 'SALIDA']]

    dfhr = dfhr.sort_values(by='EJECUTIVO', ascending=True)
    # Suma de vacaciones pendientes|

    if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        if ejecutivo == 'Selecciona un colaborador':
            # for a in ingreso:
            diferencia_dias = [round(((hoy - a).days) / 365) for a in ingreso]
        else:
            diferencia_dias = ((hoy - ingreso).dt.days) / 365
    else:
        diferencia_dias = ((hoy - ingreso).dt.days) / 365

    vp = []  # Inicializa vp como una lista
    for dia in diferencia_dias:
        for a, b in vcc.items():
            if a[0] <= dia <= a[1]:
                vp.append(b)  # Agrega el valor b a la lista
                break

    if vp is None:  # Si no se encontró ningún valor, asigna 0
        vp = 0

    vp = sum(vp)  # Suma todos los valores en la lista
    vp = vp - vt

    if st.session_state['usuario'] not in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
        st.session_state['vacaciones'] = vp

    # Total de asistencias
    atotal = df_filtered['NOMBRE'].count()

    # Suma de retardos
    rtotal = detailAsis['RETARDOS'].sum()

    # Suma de puntualidad
    ptotal = (atotal) - (rtotal)

    # Suma de horas efectivas
    he = round(pd.to_numeric(
        df_filtered['HORAS EFECTIVAS'], errors='coerce').mean(), 2)

    # Suma de inasistencias

    exc_fech = df_filtered.groupby('FECHA', as_index=False)[
        'R. EXCEDIDO'].max()

    # detailAsis = pd.merge(
    #     detailAsis, exc_fech[['NOMBRE', 'FECHA']], on='R. EXCEDIDO', how='left')
    detailAsis = pd.merge(
        detailAsis, exc_fech[['R. EXCEDIDO', 'FECHA']], on='FECHA', how='left')

    ndf_filtered = df_filtered.sort_values(
        by='RETARDOS', ascending=True)  # Ordenar de mayor a menor
    dfhor = df_filtered[['FECHA', 'HORA REGISTRO EN…', 'TOLERANCIA']]

    # DAY_MAX == PICOS RETARDOS
    hightR['FECHA'] = hightR['FECHA'].dt.date
    day_max = hightR.groupby('FECHA', as_index=False)[
        'R. EXCEDIDO'].max()
    day_max = day_max[day_max['R. EXCEDIDO'] > 0]
    day_max = pd.merge(day_max, hightR[['NOMBRE',  'R. EXCEDIDO', 'HORA REGISTRO EN…']],
                       on='R. EXCEDIDO', how='left')  # Agregar columna R. EXCEDIDO
    # Elimina duplicados en 'R. EXCEDIDO'
    day_max = day_max.drop_duplicates(subset=['FECHA', 'NOMBRE'])
    day_max['MINUTOS OUT'] = day_max['R. EXCEDIDO'].astype(str) + \
        ' Minutos'

    fig = px.pie(values=[rtotal, ptotal],
                 names=['Retardos', 'Puntualidad'],
                 title='Retardos / Puntualidad')
    fig.update_traces(textposition='outside',
                      textinfo='percent+label')

    fig2 = px.scatter(day_max,
                      x='FECHA',
                      y='R. EXCEDIDO',
                      title='Picos Retardos',
                      width=800,  # Ajusta el ancho de la gráfica
                      height=407)  # Ajusta la altura de la gráfica
    fig2.update_traces(textposition='top center',
                       textfont=dict(size=16))
    # Agregar sombreado
    fig2.add_traces(px.area(day_max, x='FECHA', y='R. EXCEDIDO').data)

    detailAsis['HORA REGISTRO EN…'] = pd.to_datetime(
        detailAsis['HORA REGISTRO EN…'], format='%H:%M:%S', errors='coerce'
    ).dt.time
    detailAsis['TOLERANCIA'] = detailAsis['TOLERANCIA'].round(2)
    detailAsis['TOLERANCIA'] = pd.to_datetime(
        detailAsis['TOLERANCIA'], format='%H:%M').dt.time

    # Convertir las horas a segundos para que Plotly pueda manejarlas
    detailAsis['MINUTOS'] = detailAsis['REGISTRO'].apply(
        lambda x: x.hour * 60 + x.minute + x.second / 60)  # Convertir a minutos
    detailAsis['LIMITE'] = detailAsis['TOLERANCIA'].apply(
        lambda x: x.hour * 60 + x.minute + x.second / 60)  # Convertir a minutos

    # Crear gráfico de dispersión
    fig3 = px.scatter(detailAsis,
                      x='FECHA',
                      y='MINUTOS',
                      title='Reporte detallado de retardos',
                      width=800,
                      height=450,
                      hover_data={'MINUTOS': False})  # Desactivar la visualización de MINUTOS

    # Establecer el rango del eje Y (de 08:00:00 a 10:00:00 en segundos)
    fig3.update_yaxes(
        # 08:00:00 = 28800 segundos, 10:00:00 = 36000 segundos
        range=[8 * 60, 10 * 60 + 30],
        # Marcas cada 30 minutos (1800 segundos)
        tickvals=[8 * 60 + i * 30 for i in range(6)],
        ticktext=['08:00:00', '08:30:00', '09:00:00', '09:30:00',
                  '10:00:00', '10:30:00']  # Etiquetas en formato HH:MM:SS
    )

    # Shape
    # Recorre los valores únicos de 'LIMITE'
    for limite in detailAsis['LIMITE'].unique():
        fig3.add_shape(
            type='line',
            x0=detailAsis['FECHA'].iloc[0],  # Primera fecha
            x1=detailAsis['FECHA'].iloc[-1],  # Última fecha
            y0=limite,  # Valor de 'LIMITE'
            y1=limite,  # Mismo valor para que sea horizontal
            line=dict(color='black', width=2, dash='dash'),
            name=f'Límite {limite}'  # Nombre de la línea (opcional)
        )

    # Ajustar la posición del texto en las marcas
    fig3.update_traces(textposition='top center', textfont=dict(size=16))

    # Agregar sombreado (área)
    fig3.add_traces(px.area(detailAsis, x='FECHA', y='MINUTOS').data)

    # Encabezado
    st.title("TRUST :grey[VALUE]")
    # Dataframe
    tab1, tab2 = st.tabs(["Tablero", "Data"])
    with tab1:
        st.subheader("Tablero asistencia")
        col1, col2, col3, col4 = st.columns(4)
        with st.container(key='container-asistencia'):
            with col1:
                st.metric(label=f'Retardos', value=f'{rtotal}')
            with col2:
                st.metric(label=f'Vacaciones Tomadas', value=f'{vt}')
            with col3:
                st.metric(label=f'Vacaciones Pendientes', value=f'{vp}')
            with col4:
                if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
                    st.metric(label=f'Horas Efectivas', value=f'{he}')
                else:
                    st.metric(label='Área', value=st.session_state['area'])
        col1, col2 = st.columns(2)
        with col1:
            tab5, tab6 = st.tabs(['Promedio Retardos', "Inasistencias"])
            with tab5:
                st.subheader('Excedente retardos')
                st.dataframe(excedente, hide_index=True,
                             use_container_width=True, height=300)
            with tab6:
                if len(quincenas) > 0:
                    st.subheader("Sin Asistencia / Pre / Post Quincena")
                    st.dataframe(quincenas, use_container_width=True,
                                 hide_index=True, key='tabla-asistencia')
                else:
                    st.subheader("Sin Asistencia / Pre / Post Quincena")
                    st.write('No hay inasistencias en este periodo.')
        with col2:
            st.plotly_chart(
                utils.aplicarformatoChart(
                    fig,
                    backgroundColor=backgroundColor,
                    textcolor=textColor
                ),
                key='chart-pie'
            )
        col7, col8 = st.columns([65, 35])
        if st.session_state['usuario'] in ['lfortunato', 'clopez', 'bsanabria', 'omoctezuma', 'molguin', 'jreyes', 'amendoza', 'aherrera']:
            if ejecutivo == 'Selecciona un colaborador':
                with col7:
                    st.plotly_chart(utils.aplicarformatoChart(fig2,
                                                              backgroundColor=backgroundColor, textcolor=textColor), use_container_width=True, key='chart-picos')
                with col8:
                    st.subheader("Detalle / Picos Retardos")
                    st.dataframe(
                        day_max[['FECHA', 'NOMBRE', 'MINUTOS OUT']], use_container_width=True, hide_index=True, height=290)

            else:
                with col7:
                    st.plotly_chart(utils.aplicarformatoChart(fig3, backgroundColor=backgroundColor,
                                                              textcolor=textColor), use_container_width=True, key='chart-picos-ejecutivos')
                with col8:
                    detailAsis['FECHA'] = detailAsis['FECHA'].dt.date
                    st.subheader("Detalle / Picos Retardos")
                    st.dataframe(
                        detailAsis[['FECHA', 'NOMBRE', 'REGISTRO']], use_container_width=True, hide_index=True, height=290)
        else:
            with col7:
                st.plotly_chart(utils.aplicarformatoChart(fig3, backgroundColor=backgroundColor,
                                                          textcolor=textColor), use_container_width=True, key='chart-picos-ejecutivos')
            with col8:
                detailAsis['FECHA'] = detailAsis['FECHA'].dt.date
                st.subheader("Detalle / Picos Retardos")
                st.dataframe(
                    detailAsis[['FECHA', 'NOMBRE', 'REGISTRO']], use_container_width=True, hide_index=True, height=360)
        col5, col6 = st.columns(2)
        with col5:
            st.subheader("Home Office")
            st.dataframe(dfho, hide_index=True, use_container_width=True)

        with col6:
            # Cambiamos las tabs en función de si 'dfvc' está vacío o no
            tab3, tab4 = st.tabs(['Vacaciones', 'Horario'])

            # Dependiendo de la variable 'tab_seleccionada', mostramos la pestaña correspondiente
            if len(dfvc) != 0:
                with tab3:
                    st.subheader('Vacaciones')
                    st.dataframe(dfvc, hide_index=True,
                                 use_container_width=True, height=340)
            else:
                with tab3:
                    st.subheader('Vacaciones')
                    st.write('No hay datos disponibles para mostrar.')

            with tab4:
                st.subheader('Horario')
                st.dataframe(dfhr, hide_index=True,
                             use_container_width=True, height=340)  # Ajusta la altura de la gráfica
    with tab2:
        st.subheader("Base de datos")
        st.dataframe(dfnew, use_container_width=True, hide_index=True)
