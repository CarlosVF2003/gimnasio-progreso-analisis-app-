import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Cargar el archivo Progreso.csv si existe
if 'Progreso_ind' not in st.session_state:
    if Path("Progreso.csv").is_file():
        st.session_state['Progreso_ind'] = pd.read_csv("Progreso.csv", sep=';')
    else:
        st.session_state['Progreso_ind'] = pd.DataFrame()

# Definimos las funciones
def formulario_desarrollo_fuerza(sets):
    pesos = [st.number_input(f'💪 Peso para el set {i+1}:', min_value=0, max_value=100, step=1) for i in range(sets)]
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, [repeticiones] * sets, [descanso] * sets  # Las repeticiones y el tiempo de descanso son constantes para el desarrollo de fuerza

def formulario_mejora_resistencia(sets):
    pesos = [st.number_input(f'💪 Peso para el set {i+1}:', min_value=0, max_value=100, step=1) for i in range(sets)]
    repeticiones = [st.number_input(f'🏃 Repeticiones para el set {i+1}:', min_value=1, max_value=30, step=1) for i in range(sets)]
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, repeticiones, [descanso] * sets

def formulario_hipertrofia_muscular(sets):
    peso = st.number_input('💪 Peso (kg):', min_value=0, max_value=100, step=1)
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return [peso] * sets, [repeticiones] * sets, [descanso] * sets  # Tanto el peso, las repeticiones y el tiempo de descanso son constantes para la hipertrofia muscular

# Título de la aplicación
st.title('🏋️‍♂️ Nuestro progreso en el Gimnasio 🏋️‍♀️')

# Botón para abrir el formulario principal
if st.button("📝 Abrir Formulario Principal"):
    st.session_state['show_enfoque_form'] = True

# Registro de datos.
if st.session_state.get('show_enfoque_form', False):
    with st.form(key='mi_formulario'):
        # Widgets de entrada
        Dia = st.text_input('Ingresa el Día 📆 (Número):')
        Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
        Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Prensa de Piernas', 'Multipowers', 'Máquina de Extensión de Cuádriceps', 'Máquina de Femorales', 'Máquina de Aductores', 'Máquina de Abductores','Press de pecho','Extension de hombro',
                                                                    'Extension tricep en polea','Extension lateral','Extension frontal'))
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
                for peso, repeticion, descanso in zip(pesos, repeticiones, descansos):
                    Progreso_new = {'Dia': int(Dia), 'Persona': Persona, 'Maquina': Maquina, 'Peso': peso, 'Descanso': descanso, 'Sets': sets, 'Repeticiones': repeticion}
                    st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], pd.DataFrame([Progreso_new])], ignore_index=True)
                # Guardar el DataFrame actualizado en un archivo CSV
                # Utiliza transform para agregar la columna de conteo directamente al DataFrame existente
                st.session_state['Progreso_ind']['Sets'] = st.session_state['Progreso_ind'].groupby(['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Repeticiones'])['Peso'].transform('size')
                st.session_state['show_enfoque_form'] = False
                st.success('¡Datos registrados con éxito!')
                st.session_state['Progreso_ind'].to_csv('Progreso.csv', index= False, sep= ';')
                # Ocultar el formulario
            else:
                st.warning('Por favor completa todos los campos del formulario.')

# Sección del dashboard
st.title('Dashboard de Progreso en el Gimnasio')

# Filtros
st.sidebar.header('Filtros')

# Filtro por Persona
filtro_persona = st.sidebar.selectbox('Selecciona persona:', ['Todos'] + list(st.session_state['Progreso_ind']['Persona'].unique()))

# Filtro por Máquina o Ejercicio
filtro_maquina = st.sidebar.selectbox('Selecciona máquina o ejercicio:', ['Todos'] + list(st.session_state['Progreso_ind']['Maquina'].unique()))

# Filtro por Rango de Fechas
if not st.session_state['Progreso_ind'].empty:
    min_fecha = min(st.session_state['Progreso_ind']['Dia'])
    max_fecha = max(st.session_state['Progreso_ind']['Dia'])
    min_fecha = st.sidebar.number_input('Día mínimo:', min_value=min_fecha, max_value=max_fecha, value=min_fecha)
    max_fecha = st.sidebar.number_input('Día máximo:', min_value=min_fecha, max_value=max_fecha, value=max_fecha)
else:
    min_fecha = st.sidebar.number_input('Día mínimo:', None)
    max_fecha = st.sidebar.number_input('Día máximo:', None)

# Aplicar filtros
datos_filtrados = st.session_state['Progreso_ind']
if filtro_persona != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Persona'] == filtro_persona]
if filtro_maquina != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Maquina'] == filtro_maquina]
if not datos_filtrados.empty:
    datos_filtrados = datos_filtrados[(datos_filtrados['Dia'] >= min_fecha) & (datos_filtrados['Dia'] <= max_fecha)]

# Mostrar gráficos y tablas si hay datos filtrados
if not datos_filtrados.empty:
    # Gráficos y tablas aquí...
    st.subheader("Gráficos de Líneas")
    
    # Gráfico de progreso individual por persona
    fig_progress_persona = px.line(datos_filtrados, x='Dia', y='Peso', color='Persona', title='Progreso Individual por Persona', color_discrete_map={'Carlos': 'black', 'Cinthia': 'lightblue'})
    st.plotly_chart(fig_progress_persona, use_container_width=True)
    
    # Gráfico de progreso por máquina o ejercicio
    fig_progress_maquina = px.line(datos_filtrados, x='Dia', y='Peso', color='Maquina', title='Progreso por Máquina o Ejercicio')
    st.plotly_chart(fig_progress_maquina, use_container_width=True)
    
    st.subheader("Gráficos de Barras")
    
    # Gráfico de rendimiento por día
    fig_rendimiento_dia = px.bar(datos_filtrados, x='Dia', y='Peso', color='Persona', title='Rendimiento por Día', color_discrete_map={'Carlos': 'black', 'Cinthia': 'lightblue'})
    st.plotly_chart(fig_rendimiento_dia, use_container_width=True)
    
    # Gráfico de número de sets
    fig_sets = px.bar(datos_filtrados, x='Persona', y='Sets', title='Número de Sets por Persona')
    st.plotly_chart(fig_sets, use_container_width=True)
    
    # Gráfico de peso levantado
    fig_peso = px.bar(datos_filtrados, x='Dia', y='Peso', title='Peso Levantado por Día')
    st.plotly_chart(fig_peso, use_container_width=True)
    
    st.subheader("Histogramas")
    
    # Histograma de repeticiones por ejercicio
    fig_repeticiones = px.histogram(datos_filtrados, x='Repeticiones', title='Distribución de Repeticiones por Ejercicio')
    st.plotly_chart(fig_repeticiones, use_container_width=True)
    
    # Histograma de descanso
    fig_descanso = px.histogram(datos_filtrados, x='Descanso', title='Distribución de Tiempo de Descanso')
    st.plotly_chart(fig_descanso, use_container_width=True)
    
    st.subheader("Gráficos de Dispersión")
    
    # Gráfico de peso vs. descanso
    fig_peso_vs_descanso = px.scatter(datos_filtrados, x='Peso', y='Descanso', title='Peso vs. Descanso')
    st.plotly_chart(fig_peso_vs_descanso, use_container_width=True)
    
    # Gráfico de peso vs. repeticiones
    fig_peso_vs_repeticiones = px.scatter(datos_filtrados, x='Peso', y='Repeticiones', title='Peso vs. Repeticiones')
    st.plotly_chart(fig_peso_vs_repeticiones, use_container_width=True)
    
    st.subheader("Tablas de Progreso")
    
    # Tabla de progreso por persona
    st.write("Tabla de Progreso por Persona")
    st.write(datos_filtrados.groupby('Persona').agg({'Peso': 'mean', 'Repeticiones': 'mean', 'Sets': 'sum'}).reset_index())
    
    # Tabla de progreso por máquina o ejercicio
    st.write("Tabla de Progreso por Máquina o Ejercicio")
    st.write(datos_filtrados.groupby('Maquina').agg({'Peso': 'mean', 'Repeticiones': 'mean', 'Sets': 'sum'}).reset_index())
    
else:
    st.write('No hay datos disponibles para los filtros seleccionados.')
