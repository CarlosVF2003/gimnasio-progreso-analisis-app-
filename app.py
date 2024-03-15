import pandas as pd
import re

import regex
import demoji

import numpy as np
from collections import Counter

import plotly.express as px
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
import seaborn as sns
import streamlit as st


# Crear pestañas
titulos_pestanas = ['GYM 💪', 'WSP ❤️']
pestaña1, pestaña2 = st.tabs(titulos_pestanas)

# Agregar contenido a la pestaña 'Tema A'
with pestaña1:
    # Inicializar Progreso_ind si no existe en la sesión
    if 'Progreso_ind' not in st.session_state:
        st.session_state['Progreso_ind'] = pd.DataFrame()

    def formulario_desarrollo_fuerza(sets):
        pesos = [st.number_input(f'Peso para el set {i+1}:', min_value=0, max_value=100, step=1) for i in range(sets)]
        repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
        descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
        return pesos, [repeticiones] * sets, [descanso] * sets  # Las repeticiones y el tiempo de descanso son constantes para el desarrollo de fuerza

    def formulario_mejora_resistencia(sets):
        pesos = [st.number_input(f'Peso para el set {i+1}:', min_value=0, max_value=100, step=1) for i in range(sets)]
        repeticiones = [st.number_input(f'Repeticiones para el set {i+1}:', min_value=1, max_value=30, step=1) for i in range(sets)]
        descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
        return pesos, repeticiones, [descanso] * sets

    def formulario_hipertrofia_muscular(sets):
        peso = st.number_input('Peso (kg):', min_value=0, max_value=100, step=1)
        repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
        descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
        return [peso] * sets, [repeticiones] * sets, [descanso] * sets  # Tanto el peso, las repeticiones y el tiempo de descanso son constantes para la hipertrofia muscular

    st.title('Nuestro progreso en el Gimnasio 💪')

    # Botón para abrir el formulario principal
    if st.button("Abrir Formulario Principal"):
        st.session_state['show_enfoque_form'] = True

    # Registro de datos.
    if st.session_state.get('show_enfoque_form', False):
        with st.form(key='mi_formulario'):
            # Widgets de entrada
            Dia = st.text_input('Ingresa el Día 📆:')
            Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
            Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Prensa de Piernas', 'Multipowers', 'Máquina de Extensión de Cuádriceps', 'Máquina de Femorales', 'Máquina de Aductores', 'Máquina de Abductores'))
            Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ('Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'))
            sets = st.number_input('Número de sets:', min_value=1, max_value=10, step=1, value=4)
            
            # Botón de envío del formulario
            guardar_button = st.form_submit_button(label='Guardar 💾')
            if guardar_button:
                if Enfoque == 'Desarrollo de Fuerza':
                    pesos, repeticiones, descansos = formulario_desarrollo_fuerza(sets)
                elif Enfoque == 'Mejora de la Resistencia':
                    pesos, repeticiones, descansos = formulario_mejora_resistencia(sets)
                else:  # Hipertrofia Muscular
                    pesos, repeticiones, descansos = formulario_hipertrofia_muscular(sets)
                    
                # Verificar que ambos formularios estén completos
                form_completo = all(pesos) and all(repeticiones) and all(descansos)
                
                if form_completo:
                    if Enfoque == 'Hipertrofia Muscular':
                        if len(set(pesos)) == 1 and len(set(repeticiones)) == 1:  # Verifica si todos los pesos y repeticiones son iguales
                            pesos = [pesos[0]]
                            repeticiones = [repeticiones[0]]
                            sets = sets
                        else:
                            sets = 0

                    for peso, repeticion, descanso in zip(pesos, repeticiones, descansos):
                        Progreso_new = {'Dia': Dia, 'Persona': Persona, 'Maquina': Maquina, 'Peso': peso, 'Descanso': descanso, 'Sets': sets, 'Repeticiones': repeticion}
                        st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], pd.DataFrame([Progreso_new])], ignore_index=True)
                        st.session_state['Sets'] =  st.session_state['Progreso_ind'].groupby(['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Repeticiones'])['Peso','Repeticiones','Maquina'].transform('count')
                    # Guardar el DataFrame actualizado en un archivo CSV
                    st.session_state['Progreso_ind'].to_csv('Libro1.csv', index=False, sep=';')
                    
                    # Mensaje de éxito
                    st.success('¡Datos registrados con éxito!')
                    
                    # Ocultar el formulario
                    st.session_state['show_enfoque_form'] = False
                else:
                    st.warning('Por favor completa todos los campos del formulario.')

    # Visualización de datos
    st.subheader("Visualización de datos registrados")
    # Eliminar filas duplicadas basadas en las columnas específicas y actualizar los sets
    unique_values = st.session_state['Progreso_ind'].drop_duplicates(subset=['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Repeticiones'])
    st.write(unique_values)
    # Gráfico de comparación entre personas
    st.subheader("Comparación de progreso entre personas")
    avg_peso = st.session_state['Progreso_ind'].groupby('Persona')['Peso'].mean().reset_index()
    fig, ax = plt.subplots()
    sns.barplot(data=avg_peso, x='Persona', y='Peso', ax=ax)
    ax.set_title('Promedio de peso levantado por persona')
    st.pyplot(fig)
    # Histograma de repeticiones por máquina y persona
    st.subheader("Histograma de repeticiones por máquina y persona")
    fig, ax = plt.subplots()
    sns.histplot(data=st.session_state['Progreso_ind'], x='Repeticiones', hue='Persona', multiple='stack', bins=10, ax=ax)
    ax.set_title('Distribución de repeticiones por máquina y persona')
    st.pyplot(fig)

    # Box plot de pesos por día y persona
    st.subheader("Box plot de pesos por día y persona")
    fig, ax = plt.subplots()
    sns.boxplot(data=st.session_state['Progreso_ind'], x='Dia', y='Peso', hue='Persona', ax=ax)
    ax.set_title('Distribución de pesos por día y persona')
    st.pyplot(fig)

    # Gráfico de línea de series por día
    st.subheader("Gráfico de línea de series por día")
    fig, ax = plt.subplots()
    sns.lineplot(data=st.session_state['Progreso_ind'], x='Dia', y='Series', hue='Persona', markers=True, ax=ax)
    ax.set_title('Número de series por día')
    st.pyplot(fig)

    # Diagrama de dispersión de peso vs repeticiones
    st.subheader("Diagrama de dispersión de peso vs repeticiones")
    fig, ax = plt.subplots()
    sns.scatterplot(data=st.session_state['Progreso_ind'], x='Peso', y='Repeticiones', hue='Persona', ax=ax)
    ax.set_title('Peso vs Repeticiones')
    st.pyplot(fig)


# Agregar contenido a la pestaña 'Tema B'
with pestaña2:
        # Título de la aplicación
    st.title('Análisis de nuestro chat de WhatsApp ❤️')
    ###################################
    ###################################

    ##########################################
    # ### Paso 1: Definir funciones necesarias
    ##########################################
    # Patron regex para identificar el comienzo de cada línea del txt con la fecha y la hora
    def IniciaConFechaYHora(s):
        # Ejemplo: '9/16/23, 5:59 PM - ...'
        patron = r'^([0-9]{1,2})/([0-9]{1,2})/([0-9]{4}), ([0-9]{1,2}):([0-9]{2})\s?(AM|PM) -'
        resultado = re.match(patron, s)  # Verificar si cada línea del txt hace match con el patrón de fecha y hora
        if resultado:
            return True
        return False

    # Patrón para encontrar a los miembros del grupo dentro del txt
    def EncontrarMiembro(s):
        patrones = ['Carlos:','Cinthia:']

        patron = '^' + '|'.join(patrones)
        resultado = re.match(patron, s)  # Verificar si cada línea del txt hace match con el patrón de miembro
        if resultado:
            return True
        return False

    # Separar las partes de cada línea del txt: Fecha, Hora, Miembro y Mensaje
    def ObtenerPartes(linea):
        # Ejemplo: '9/16/23, 5:59 PM - Sandreke: Todos debemos aprender a analizar datos'
        splitLinea = linea.split(' - ')
        FechaHora = splitLinea[0]                     # '9/16/23, 5:59 PM'
        splitFechaHora = FechaHora.split(', ')
        Fecha = splitFechaHora[0]                    # '9/16/23'
        Hora = ' '.join(splitFechaHora[1:])          # '5:59 PM'
        Mensaje = ' '.join(splitLinea[1:])             # 'Sandreke: Todos debemos aprender a analizar datos'
        if EncontrarMiembro(Mensaje):
            splitMensaje = Mensaje.split(': ')
            Miembro = splitMensaje[0]               # 'Sandreke'
            Mensaje = ' '.join(splitMensaje[1:])    # 'Todos debemos aprender a analizar datos'
        else:
            Miembro = None       
        return Fecha, Hora, Miembro, Mensaje


    ##################################################################################
    # ### Paso 2: Obtener el dataframe usando el archivo txt y las funciones definidas
    ##################################################################################

    # Leer el archivo txt descargado del chat de WhatsApp
    RutaChat = 'Chat con Cinthia.txt'

    # Lista para almacenar los datos (Fecha, Hora, Miembro, Mensaje) de cada línea del txt
    DatosLista = []
    with open(RutaChat, encoding="utf-8") as fp:
        fp.readline() # Eliminar primera fila relacionada al cifrado de extremo a extremo
        Fecha, Hora, Miembro = None, None, None
        while True:
            linea = fp.readline()
            if not linea:
                break
            linea = linea.strip()
            if IniciaConFechaYHora(linea): # Si cada línea del txt coincide con el patrón fecha y hora
                Fecha, Hora, Miembro, Mensaje = ObtenerPartes(linea) # Obtener datos de cada línea del txt
                DatosLista.append([Fecha, Hora, Miembro, Mensaje])

    # Convertir la lista con los datos a dataframe
    df = pd.DataFrame(DatosLista, columns=['Fecha', 'Hora', 'Miembro', 'Mensaje'])

    # Cambiar la columna Fecha a formato datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'], format="%d/%m/%Y")

    # Eliminar los posibles campos vacíos del dataframe
    # y lo que no son mensajes como cambiar el asunto del grupo o agregar a alguien
    df = df.dropna()

    # Resetear el índice
    df.reset_index(drop=True, inplace=True)

    # #### Filtrar el chat por fecha de acuerdo a lo requerido
    start_date = '2023-01-01'
    end_date = '2024-03-09'

    df = df[(df['Fecha'] >= start_date) & (df['Fecha'] <= end_date)]


    ##################################################################
    # ### Paso 3: Estadísticas de mensajes, multimedia, emojis y links
    ##################################################################

    # #### Total de mensajes, multimedia, emojis y links enviados
    def ObtenerEmojis(Mensaje):
        emoji_lista = []
        data = regex.findall(r'\X', Mensaje)  # Obtener lista de caracteres de cada mensaje
        for caracter in data:
            if demoji.replace(caracter) != caracter:
                emoji_lista.append(caracter)
        return emoji_lista

    # Obtener la cantidad total de mensajes
    total_mensajes = df.shape[0]

    # Obtener la cantidad de archivos multimedia enviados
    multimedia_mensajes = df[df['Mensaje'] == '<multimedia omitido>'].shape[0]

    # Obtener la cantidad de emojis enviados
    df['Emojis'] = df['Mensaje'].apply(ObtenerEmojis) # Se agrega columna 'Emojis'
    emojis = sum(df['Emojis'].str.len())

    # Obtener la cantidad de links enviados
    url_patron = r'(https?://\S+)'
    df['URLs'] = df.Mensaje.apply(lambda x: len(re.findall(url_patron, x))) # Se agrega columna 'URLs'
    links = sum(df['URLs'])

    # Obtener la cantidad de encuestas
    encuestas = df[df['Mensaje'] == 'POLL:'].shape[0]

    # Todos los datos pasarlo a diccionario
    estadistica_dict = {'Tipo': ['Mensajes', 'Multimedia', 'Emojis', 'Links', 'Encuestas'],
            'Cantidad': [total_mensajes, multimedia_mensajes, emojis, links, encuestas]
            }

    #Convertir diccionario a dataframe
    estadistica_df = pd.DataFrame(estadistica_dict, columns = ['Tipo', 'Cantidad'])

    # Establecer la columna Tipo como índice
    estadistica_df = estadistica_df.set_index('Tipo')

    ###################################
    ###################################
    st.header('💡 Estadísticas generales')
    col1, col2 = st.columns([1, 2])

    with col1:
        st.write(estadistica_df)
    ###################################
    ###################################

    # #### Emojis más usados

    # Obtener emojis más usados y las cantidades en el chat del grupo del dataframe
    emojis_lista = list([a for b in df.Emojis for a in b])
    emoji_diccionario = dict(Counter(emojis_lista))
    emoji_diccionario = sorted(emoji_diccionario.items(), key=lambda x: x[1], reverse=True)

    # Convertir el diccionario a dataframe
    emoji_df = pd.DataFrame(emoji_diccionario, columns=['Emoji', 'Cantidad'])

    # Establecer la columna Emoji como índice
    emoji_df = emoji_df.set_index('Emoji').head(10)


    # Plotear el pie de los emojis más usados
    fig = px.pie(emoji_df, values='Cantidad', names=emoji_df.index, hole=.3, template='plotly_dark', color_discrete_sequence=px.colors.qualitative.Pastel2)
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=20)

    # Ajustar el gráfico
    fig.update_layout(
        # title={'text': 'Emojis más usados',
        # #          'y':0.96,
        # #          'x':0.5,
        #          'xanchor': 'center'}, font=dict(size=17),
        showlegend=False)
    # fig.show()


    ###################################
    ###################################
    # st.header('Emojis más usados')
    # col1, col2 = st.columns([1, 2])

    # with col1:
    #     st.write(emoji_df)

    # with col2:
    #     st.plotly_chart(fig)
    ###################################
    ###################################

    # ### Paso 4: Estadísticas de los miembros del grupo

    # #### Miembros más activos

    # Determinar los miembros más activos del grupo
    df_MiembrosActivos = df.groupby('Miembro')['Mensaje'].count().sort_values(ascending=False).to_frame()
    df_MiembrosActivos.reset_index(inplace=True)
    df_MiembrosActivos.index = np.arange(1, len(df_MiembrosActivos)+1)
    df_MiembrosActivos['% Mensaje'] = (df_MiembrosActivos['Mensaje'] / df_MiembrosActivos['Mensaje'].sum()) * 100

    ###################################
    ###################################
    with col2:
        st.write(df_MiembrosActivos)
    ###################################
    ###################################

    # #### Estadísticas por miembro

    # Separar mensajes (sin multimedia) y multimedia (stickers, fotos, videos)
    multimedia_df = df[df['Mensaje'] == '<Media omitted>']
    mensajes_df = df.drop(multimedia_df.index)

    # Contar la cantidad de palabras y letras por mensaje
    mensajes_df['Letras'] = mensajes_df['Mensaje'].apply(lambda s : len(s))
    mensajes_df['Palabras'] = mensajes_df['Mensaje'].apply(lambda s : len(s.split(' ')))
    # mensajes_df.tail()


    # Obtener a todos los miembros
    miembros = mensajes_df.Miembro.unique()

    # Crear diccionario donde se almacenará todos los datos
    dictionario = {}

    for i in range(len(miembros)):
        lista = []
        # Filtrar mensajes de un miembro en específico
        miembro_df= mensajes_df[mensajes_df['Miembro'] == miembros[i]]

        # Agregar a la lista el número total de mensajes enviados
        lista.append(miembro_df.shape[0])
        
        # Agregar a la lista el número de palabras por total de mensajes (palabras por mensaje)
        palabras_por_msj = (np.sum(miembro_df['Palabras']))/miembro_df.shape[0]
        lista.append(palabras_por_msj)

        # Agregar a la lista el número de mensajes multimedia enviados
        multimedia = multimedia_df[multimedia_df['Miembro'] == miembros[i]].shape[0]
        lista.append(multimedia)

        # Agregar a la lista el número total de emojis enviados
        emojis = sum(miembro_df['Emojis'].str.len())
        lista.append(emojis)

        # Agregar a la lista el número total de links enviados
        links = sum(miembro_df['URLs'])
        lista.append(links)

        # Asignar la lista como valor a la llave del diccionario
        dictionario[miembros[i]] = lista
        
    # print(dictionario)


    # Convertir de diccionario a dataframe
    miembro_stats_df = pd.DataFrame.from_dict(dictionario)

    # Cambiar el índice por la columna agregada 'Estadísticas'
    estadísticas = ['Mensajes', 'Palabras por mensaje', 'Multimedia', 'Emojis', 'Links']
    miembro_stats_df['Estadísticas'] = estadísticas
    miembro_stats_df.set_index('Estadísticas', inplace=True)

    # Transponer el dataframe
    miembro_stats_df = miembro_stats_df.T

    #Convertir a integer las columnas Mensajes, Multimedia Emojis y Links
    miembro_stats_df['Mensajes'] = miembro_stats_df['Mensajes'].apply(int)
    miembro_stats_df['Multimedia'] = miembro_stats_df['Multimedia'].apply(int)
    miembro_stats_df['Emojis'] = miembro_stats_df['Emojis'].apply(int)
    miembro_stats_df['Links'] = miembro_stats_df['Links'].apply(int)
    miembro_stats_df = miembro_stats_df.sort_values(by=['Mensajes'], ascending=False)

    ###################################
    ###################################
    st.subheader('Cómo se distribuyen nuestros mensajes 👀')
    st.write(miembro_stats_df)
    ###################################
    ###################################



    ###################################
    ###################################
    st.header('🤗 Emojis más usados')
    col1, col2 = st.columns([1, 2])

    with col1:
        st.write(emoji_df)

    with col2:
        st.plotly_chart(fig)
    ###################################
    ###################################



    # ### Paso 5: Estadísticas del comportamiento del grupo

    df['rangoHora'] = pd.to_datetime(df['Hora'], format='%I:%M %p')

    # Define a function to create the "Range Hour" column
    def create_range_hour(hour):
        hour = pd.to_datetime(hour)
        start_hour = hour.hour
        end_hour = (hour + pd.Timedelta(hours=1)).hour
        return f'{start_hour:02d} - {end_hour:02d} h'

    # # Apply the function to create the "Range Hour" column
    df['rangoHora'] = df['rangoHora'].apply(create_range_hour)
    df['DiaSemana'] = df['Fecha'].dt.strftime('%A')
    mapeo_dias_espanol = {'Monday': '1 Lunes','Tuesday': '2 Martes','Wednesday': '3 Miércoles','Thursday': '4 Jueves',
                        'Friday': '5 Viernes','Saturday': '6 Sábado','Sunday': '7 Domingo'}
    df['DiaSemana'] = df['DiaSemana'].map(mapeo_dias_espanol)
    # df


    # #### Número de mensajes por rango de hora

    # Crear una columna de 1 para realizar el conteo de mensajes
    df['# Mensajes por hora'] = 1

    # Sumar (contar) los mensajes que tengan la misma fecha
    date_df = df.groupby('rangoHora').count().reset_index()

    # Plotear la cantidad de mensajes respecto del tiempo
    fig = px.line(date_df, x='rangoHora', y='# Mensajes por hora', color_discrete_sequence=['salmon'], template='plotly_dark')

    # Ajustar el gráfico
    # fig.update_layout(
    #     title={'text': 'Mensajes con ella ❤️ por hora',
    #              'y':0.96,
    #              'x':0.5,
    #              'xanchor': 'center'},
    #     font=dict(size=17))
    fig.update_traces(mode='markers+lines', marker=dict(size=10))
    fig.update_xaxes(title_text='Rango de hora', tickangle=30)
    fig.update_yaxes(title_text='# Mensajes')
    # fig.show()

    ###################################
    ###################################
    st.header('⏰ Mensajes por hora')
    st.plotly_chart(fig)
    ###################################
    ###################################


    # #### Número de mensajes por día

    # Crear una columna de 1 para realizar el conteo de mensajes
    df['# Mensajes por día'] = 1

    # Sumar (contar) los mensajes que tengan la misma fecha
    date_df = df.groupby('DiaSemana').count().reset_index()


    # Plotear la cantidad de mensajes respecto del tiempo
    fig = px.line(date_df, x='DiaSemana', y='# Mensajes por día', color_discrete_sequence=['salmon'], template='plotly_dark')

    # Ajustar el gráfico
    # fig.update_layout(
    #     title={'text': 'Mensajes con ella ❤️ por día', 'y':0.96, 'x':0.5, 'xanchor': 'center'},
    #     font=dict(size=17))

    fig.update_traces(mode='markers+lines', marker=dict(size=10))
    fig.update_xaxes(title_text='Día', tickangle=30)
    fig.update_yaxes(title_text='# Mensajes')
    # fig.show()

    ###################################
    ###################################
    st.header('📆 Mensajes por día')
    st.plotly_chart(fig)
    ###################################
    ###################################

    # #### Número de mensajes a través del tiempo

    # Crear una columna de 1 para realizar el conteo de mensajes
    df['# Mensajes por día'] = 1

    # Sumar (contar) los mensajes que tengan la misma fecha
    date_df = df.groupby('Fecha').sum().reset_index()

    # Plotear la cantidad de mensajes respecto del tiempo
    fig = px.line(date_df, x='Fecha', y='# Mensajes por día', color_discrete_sequence=['salmon'], template='plotly_dark')

    # Ajustar el gráfico
    # fig.update_layout(
    #     title={'text': 'Mensajes con ella ❤️',
    #              'y':0.96,
    #              'x':0.5,
    #              'xanchor': 'center'},
    #     font=dict(size=17))

    fig.update_xaxes(title_text='Fecha', tickangle=45, nticks=35)
    fig.update_yaxes(title_text='# Mensajes')
    # fig.show()

    ###################################
    ###################################
    st.header('📈 Mensajes a lo largo del tiempo')
    st.plotly_chart(fig)
    ###################################
    ###################################

    # #### Word Cloud de palabras más usadas

    # Crear un string que contendrá todas las palabras
    total_palabras = ' '
    stopwords = STOPWORDS.update(['que', 'qué', 'con', 'de', 'te', 'en', 'la', 'lo', 'le', 'el', 'las', 'los', 'les', 'por', 'es',
                                'son', 'se', 'para', 'un', 'una', 'chicos', 'su', 'si', 'chic','nos', 'ya', 'hay', 'esta',
                                'pero', 'del', 'mas', 'más', 'eso', 'este', 'como', 'así', 'todo', 'https','multimedia','omitido',
                                'y', 'mi', 'o', 'q', 'yo', 'al'])

    mask = np.array(Image.open('heart.jpg'))

    # Obtener y acumular todas las palabras de cada mensaje
    for mensaje in mensajes_df['Mensaje'].values:
        palabras = str(mensaje).lower().split() # Obtener las palabras de cada línea del txt
        for palabra in palabras:
            total_palabras = total_palabras + palabra + ' ' # Acumular todas las palabras

    wordcloud = WordCloud(width = 800, height = 800, background_color ='black', stopwords = stopwords,
                        max_words=100, min_font_size = 5,
                        mask = mask, colormap='PuRd').generate(total_palabras)

    # Plotear la nube de palabras más usadas
    # wordcloud.to_image()


    ###################################
    ###################################
    st.header('☁️ Nuestro word cloud')
    st.image(wordcloud.to_array(), caption='Las palabras que más usamos ❤️', use_column_width=True)
    ###################################
    ###################################