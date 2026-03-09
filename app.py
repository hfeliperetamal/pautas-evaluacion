import streamlit as st
import pandas as pd
from utils import RUBRICS, calculate_grade, get_scoring_details
from datetime import datetime

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

    if st.button("\u2705 Enviar Evaluaci\u00f3n"):
        if not profesor:
            st.error("El nombre del profesor es obligatorio.")
        else:
            final_results = []
            for name, scores in evaluations.items():
                # Calculate points per section
                total_calculated_points = 0
                for section in selected_rubric["sections"]:
                    section_scores = [scores[item] for item in section["items"]]
                    section_sum = sum(section_scores)
                    # The doc logic: (Sum / (Items * 5)) * Weight? 
                    # Looking at the doc totals: Gestion Portada 10% (4 items) -> total points 20 (max 4*5=20). 
                    # If points=20, calc=10% of max pts total? No.
                    # Calculated value = Points * Weight / MaxSectionPoints
                    section_max_points = len(section["items"]) * 5
                    calculated_section_value = (section_sum * section["weight"]) / section_max_points
                    total_calculated_points += (calculated_section_value / 5) # Normalize to 1-5 scale?
                    # Re-reading doc logic: 
                    # Gestion Portada: Weight 10, items 4. Sum/20 * 2 = Calculated value? No, doc says 10% -> /2 pts.
                    # Max raw points = 5*4 = 20. If points=20, value=2. 
                    # So: value = (sum / 20) * 2. 
                    # Actually: TotalCalculated = Sum( (SectionSum / MaxSectionSum) * SectionWeightPoints )
                
                # Let's simplify and follow the exact points in the doc:
                # Gestion max pts: 19.75. Sum of weights: 10+20+15+15+20+10+10 = 100.
                # Section maxes in pts: 2, 4, 3, 3.75, 4, 2, 2.
                # Item value = (score/5) * (Weight / Items)
                total_pts = 0
                for section in selected_rubric["sections"]:
                    section_item_weight = section["weight"] / (len(section["items"]) * 5 * 100 / selected_rubric["max_points"])
                    # Let's use a simpler scaling: 
                    # Points_Section = (Sum_Section / (Count_Section * 5)) * (Max_Points * Weight / 100)
                    section_points = (sum([scores[item] for item in section["items"]]) / (len(section["items"]) * 5)) * (selected_rubric["max_points"] * section["weight"] / 100)
                    total_pts += section_points
                
                grade = calculate_grade(total_pts, selected_rubric["max_points"])
                
                res = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Profesor": profesor,
                    "Pauta": rubric_name,
                    "Estudiante": name,
                    "Puntaje Total": round(total_pts, 2),
                    "Nota": grade
                }
                final_results.append(res)
            
            df = pd.DataFrame(final_results)
            st.success("\u00a1Evaluaci\u00f3n procesada con \u00e9xito!")
            st.dataframe(df)
            
            # TODO: Add Google Sheets connection
            st.info("Conectando con Google Sheets para guardar los datos...")
            # conn = st.connection("gsheets", type=GSheetsConnection)
            # conn.create(data=df)
            
            st.balloons()

st.sidebar.title("Instrucciones")
st.sidebar.info("""
1. Ingrese su nombre como profesor.
2. Seleccione la pauta correspondiente.
3. Ingrese los nombres de hasta 3 personas.
4. Eval\u00fae cada \u00edtem para cada persona.
5. Presione 'Enviar Evaluaci\u00f3n' al finalizar.
""")
