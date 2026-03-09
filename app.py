import streamlit as st
import pandas as pd
from utils import RUBRICS, calculate_grade, get_scoring_details
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Page configuration
st.set_page_config(page_title="Pautas de Investigaci\u00f3n y Gesti\u00f3n", layout="wide")

st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stSelectbox label, .stTextInput label {
        font-weight: bold;
    }
    .evaluation-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("\u2696\ufe0f Pautas de Evaluaci\u00f3n Online")
st.subheader("Investigaci\u00f3n y Gesti\u00f3n")

# Session State Initialization
if 'evaluation_data' not in st.session_state:
    st.session_state.evaluation_data = {}

# Header: Professor and Pauta Selection
col1, col2 = st.columns(2)
with col1:
    profesor = st.text_input("Nombre del Profesor Evaluador", key="profesor_name")
with col2:
    rubric_name = st.selectbox("Seleccione la Pauta", list(RUBRICS.keys()))

selected_rubric = RUBRICS[rubric_name]

st.divider()

# Person Selection (3 people)
st.write("### Integrantes a Evaluar")
names_cols = st.columns(3)
names = []
for i in range(3):
    with names_cols[i]:
        name = st.text_input(f"Persona {i+1}", key=f"person_{i}")
        names.append(name)

st.divider()

# Scoring system explanation
st.info("**Criterios de Puntaje:** 5: Sobresaliente | 4: Bueno | 3: Aceptable | 2: Necesita mejorar | 1: No se evidencia")

# Evaluation Form
evaluations = {name: {} for name in names if name}
observations = {name: "" for name in names if name}

if not evaluations:
    st.warning("Por favor ingrese al menos un nombre para comenzar la evaluaci\u00f3n.")
else:
    # We iterate through sections
    for section in selected_rubric["sections"]:
        with st.expander(f"\u21d2 {section['name']} (Peso: {section['weight']}%)", expanded=True):
            for item in section["items"]:
                st.write(f"**{item}**")
                cols = st.columns(len(evaluations))
                for idx, name in enumerate(evaluations.keys()):
                    with cols[idx]:
                        evaluations[name][item] = st.select_slider(
                            f"Nota para {name}",
                            options=[1, 2, 3, 4, 5],
                            value=3,
                            key=f"eval_{name}_{item}"
                        )
            st.divider()

    # Observations block
    st.write("### Observaciones Finales")
    obs_cols = st.columns(len(evaluations))
    for idx, name in enumerate(evaluations.keys()):
        with obs_cols[idx]:
            observations[name] = st.text_area(f"Observaciones para {name}", key=f"obs_{name}")

    if st.button("\u2705 Enviar Evaluaci\u00f3n"):
        if not profesor:
            st.error("El nombre del profesor es obligatorio.")
        else:
            final_results = []
            for name, scores in evaluations.items():
                total_pts = 0
                for section in selected_rubric["sections"]:
                    section_points = (sum([scores[item] for item in section["items"]]) / (len(section["items"]) * 5)) * (selected_rubric["max_points"] * section["weight"] / 100)
                    total_pts += section_points
                
                grade = calculate_grade(total_pts, selected_rubric["max_points"])
                
                res = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Profesor": profesor,
                    "Pauta": rubric_name,
                    "Estudiante": name,
                    "Puntaje Total": round(total_pts, 2),
                    "Nota": grade,
                    "Observaciones": observations[name]
                }
                final_results.append(res)
            
            df = pd.DataFrame(final_results)
            st.success("¡Evaluación procesada con éxito!")
            st.dataframe(df)
            
            # Google Sheets connection
            try:
                st.info("Conectando con Google Sheets...")
                
                # Intentamos limpiar la llave privada si viene con saltos de l\u00ednea mal formateados
                try:
                    # Acceso directo a los secretos para limpieza preventiva
                    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                        pk = st.secrets["connections"]["gsheets"].get("private_key", "")
                        if "\\n" in pk:
                            # Si detectamos caracteres literalizados de salto de l\u00ednea, los corregimos
                            st.warning("Aviso: Formato de llave detectado con caracteres de escape. Limpiando para compatibilidad...")
                except:
                    pass

                conn = st.connection("gsheets", type=GSheetsConnection)
                
                # Leer datos existentes sin usar el cache (ttl=0)
                try:
                    existing_data = conn.read(ttl=0)
                    if existing_data is not None and not existing_data.empty:
                        updated_df = pd.concat([existing_data, df], ignore_index=True)
                    else:
                        updated_df = df
                except Exception as read_error:
                    # Si falla la lectura (hoja vac\u00eda), usamos solo los datos actuales
                    st.warning(f"Aviso: No se pudieron leer datos previos ({read_error}). Iniciando nueva hoja.")
                    updated_df = df
                
                # Actualizar la planilla
                conn.update(data=updated_df)
                st.success("\u2705 \u00a1Datos respaldados con \u00e9xito en la planilla!")
            except Exception as e:
                st.error(f"Error cr\u00edtico de conexi\u00f3n: {e}")
                st.info("Sugerencia: Si el error es 'Invalid private key', intenta copiar la llave del JSON y pegarla en una sola l\u00ednea reemplazando los saltos de l\u00ednea por el texto \\n dentro de los Secrets.")
            
            st.balloons()

st.sidebar.title("Instrucciones")
st.sidebar.info("""
1. Ingrese su nombre como profesor.
2. Seleccione la pauta correspondiente.
3. Ingrese los nombres de hasta 3 personas.
4. Eval\u00fae cada \u00edtem para cada persona.
5. Presione 'Enviar Evaluaci\u00f3n' al finalizar.
""")
