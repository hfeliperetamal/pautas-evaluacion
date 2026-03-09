import streamlit as st
import pandas as pd

# Rubric Data Structures
RUBRICS = {
    "Investigaci\u00f3n 2025": {
        "max_points": 17.75,
        "sections": [
            {
                "name": "Portada de Presentaci\u00f3n",
                "weight": 10,
                "items": [
                    "El t\u00edtulo describe el contenido, breve, claro e informativo.",
                    "Identifica el dise\u00f1o del estudio (descriptivo, revisi\u00f3n sistem\u00e1tica, etc.).",
                    "Autores presentados con nombre completo.",
                    "Distintivos institucionales, kinesiolog\u00eda, ciudad, fecha y a\u00f1o."
                ]
            },
            {
                "name": "Introducci\u00f3n",
                "weight": 15,
                "items": [
                    "Marco Te\u00f3rico: secuencia y desarrollo de conceptos preciso.",
                    "Referencias actualizadas que fundamentan la problem\u00e1tica.",
                    "Objetivos factibles y consistentes con la conceptualizaci\u00f3n te\u00f3rica."
                ]
            },
            {
                "name": "Material y M\u00e9todos",
                "weight": 15,
                "items": [
                    "Tipo de Estudio claramente especificado y correspondiente.",
                    "Selecci\u00f3n de sujetos, criterios de inclusi\u00f3n/exclusi\u00f3n, elegibilidad.",
                    "Instrumento: Detalla correctamente (sensibilidad, validez, confiabilidad, PRISMA, etc.).",
                    "Variables independientes y dependientes claramente especificadas."
                ]
            },
            {
                "name": "Resultados",
                "weight": 20,
                "items": [
                    "Expresa los resultados en gr\u00e1ficos/tablas de forma clara.",
                    "Informaci\u00f3n consistente con el tipo y los objetivos del estudio.",
                    "Uso correcto de pruebas estad\u00edsticas y significancia (si aplica)."
                ]
            },
            {
                "name": "Conclusi\u00f3n y Discusi\u00f3n",
                "weight": 20,
                "items": [
                    "Resume resultados principales y conclusiones en relaci\u00f3n a lo presentado.",
                    "Interpretaci\u00f3n global considerando objetivos, limitaciones y similares.",
                    "Discute limitaciones (sesgo, imprecisi\u00f3n).",
                    "Demuestra la relevancia del estudio."
                ]
            },
            {
                "name": "Formato Presentaci\u00f3n",
                "weight": 10,
                "items": [
                    "Expresi\u00f3n oral: clara, audible, terminolog\u00eda t\u00e9cnica formal.",
                    "Presentaci\u00f3n escrita: ortograf\u00eda, redacci\u00f3n, est\u00e9tica, secuencia l\u00f3gica.",
                    "Apoyo audiovisual atractivo, ordenado, claro y coherente.",
                    "Citas bibliogr\u00e1ficas de acuerdo a normativa (Vancouver/APA)."
                ]
            },
            {
                "name": "Preguntas y Respuestas",
                "weight": 10,
                "items": [
                    "Responde adecuadamente con fundamentos del m\u00e9todo cient\u00edfico.",
                    "Respuestas acertadas, coherentes, permiten clarificar.",
                    "Fundamenta el aporte significativo de la investigaci\u00f3n/gesti\u00f3n."
                ]
            }
        ]
    },
    "Gesti\u00f3n 2025": {
        "max_points": 19.75,
        "sections": [
            {
                "name": "Portada de Presentaci\u00f3n",
                "weight": 10,
                "items": [
                    "La portada posee los distintivos institucionales y del departamento de Kinesiolog\u00eda, ciudad, fecha y a\u00f1o.",
                    "El t\u00edtulo del proyecto da una idea concisa y precisa del problema que se quiere resolver o del objetivo.",
                    "El t\u00edtulo hace alusi\u00f3n y trata de la conveniencia para la organizaci\u00f3n o el inversionista.",
                    "Se presenta el nombre completo de los autores directos del proyecto, as\u00ed como del docente gu\u00eda."
                ]
            },
            {
                "name": "Introducci\u00f3n",
                "weight": 20,
                "items": [
                    "Se presenta un \u00edndice o tabla de contenidos preciso acerca de la presentaci\u00f3n a realizar.",
                    "Se realiza la descripci\u00f3n y justificaci\u00f3n del Proyecto (relevante, pertinente, oportuno).",
                    "Se deben describir los objetivos que se persiguen con la iniciativa de inversi\u00f3n."
                ]
            },
            {
                "name": "Viabilidad del Proyecto",
                "weight": 15,
                "items": [
                    "Se expone un an\u00e1lisis t\u00e9cnico del proyecto.",
                    "Se expone un an\u00e1lisis legal del Proyecto.",
                    "Se expone un an\u00e1lisis de la viabilidad de gesti\u00f3n del Proyecto.",
                    "Se expone un an\u00e1lisis de la viabilidad pol\u00edtica del Proyecto, ambiental, otro."
                ]
            },
            {
                "name": "An\u00e1lisis de Mercado",
                "weight": 15,
                "items": [
                    "An\u00e1lisis de mercado (Consumidor, Competidor, Proveedor, Distribuidor).",
                    "La informaci\u00f3n es presentada en tablas y/o gr\u00e1ficos, esquemas.",
                    "Se menciona la metodolog\u00eda utilizada para el levantamiento de la informaci\u00f3n.",
                    "Se expone un an\u00e1lisis de la Demanda para el Proyecto.",
                    "Se expone la estrategia comercial (tarifa, servicio, promoci\u00f3n, distribuci\u00f3n)."
                ]
            },
            {
                "name": "An\u00e1lisis T\u00e9cnico del Proyecto",
                "weight": 20,
                "items": [
                    "Se realiza una descripci\u00f3n de las inversiones, costos y gastos del proyecto.",
                    "Se exponen los beneficios esperados con la implementaci\u00f3n del Proyecto.",
                    "Se muestra un resumen del flujo de caja del Proyecto.",
                    "Se explicita alguna metodolog\u00eda de evaluaci\u00f3n del proyecto (viabilidad econ\u00f3mica)."
                ]
            },
            {
                "name": "Conclusiones y Recomendaciones finales",
                "weight": 10,
                "items": [
                    "Las Conclusiones est\u00e1n en consonancia con los objetivos y lo presentado.",
                    "Los autores hacen \u00e9nfasis en la conveniencia de invertir en el proyecto.",
                    "Se expone sobre posibilidades de continuidad del Proyecto.",
                    "Los autores insisten en la viabilidad del proyecto."
                ]
            },
            {
                "name": "Formato Presentaci\u00f3n",
                "weight": 10,
                "items": [
                    "Expresi\u00f3n oral: clara, audible, terminolog\u00eda t\u00e9cnica formal.",
                    "Presentaci\u00f3n escrita: ortograf\u00eda, redacci\u00f3n, est\u00e9tica, secuencia l\u00f3gica.",
                    "Apoyo audiovisual atractivo, ordenado, clara y coherente.",
                    "Las referencias y fuentes bibliogr\u00e1ficas est\u00e1n claramente explicitadas."
                ]
            }
        ]
    }
}

def calculate_grade(points, max_points, exigence=0.7):
    """
    Calculates grade from 1.0 to 7.0 based on points and exigence.
    """
    if points < exigence * max_points:
        grade = 1.0 + 3.0 * (points / (exigence * max_points))
    else:
        grade = 4.0 + 3.0 * ((points - exigence * max_points) / ((1 - exigence) * max_points))
    return round(grade, 1)

def get_scoring_details():
    return {
        5: "Sobresaliente",
        4: "Bueno",
        3: "Aceptable",
        2: "Necesita mejorar",
        1: "No se evidencia"
    }
