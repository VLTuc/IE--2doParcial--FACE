#!pip install pymupdf
#!pip install llama-index
#!pip install llama-index-llms-gemini
#!pip install llama-index-embeddings-gemini

import json
import streamlit as st
from llama_index.core.llms import ChatMessage
from llama_index.llms.gemini import Gemini

import fitz  # PyMuPDF para extraer texto y fórmulas
import re

# Configurar la clave API de manera segura
api_key = st.secrets["gemini_api_key"]
llm = Gemini(api_key=api_key)


# Función para extraer texto y fórmulas del PDF
def extraer_texto_y_formulas(pdf_path):
    texto = ""
    with fitz.open(pdf_path) as doc:
        for pagina in doc:
            # Extraer texto normal
            texto += pagina.get_text("text") + "\n"

            # Extraer texto de fórmulas en formato LaTeX si están embebidas (PyMuPDF no detecta imágenes)
            for bloque in pagina.get_text("blocks"):
                if re.search(r'[=+\-*/^]', bloque[4]):  # Si hay símbolos matemáticos
                    texto += f" [Fórmula]: {bloque[4]} \n"

    return texto.strip()



# Función para hacer la pregunta al LLM
def hacer_pregunta(pregunta):
    # Extraer contenido del PDF
    contexto = extraer_texto_y_formulas("TercerP.pdf")

    # Mensajes para el modelo
    mensajes = [
        ChatMessage(role="system", content=(
            "Te voy a compartir un PDF que contiene material con teoría y fórmulas matemáticas. "
            "Cuando te haga una pregunta, actúa como un experto en estadística y usa este contenido para responder. "
            "Cuando se te pida una definición o teorema, utiliza exclusivamente la teoria y notación del material en pdf, por favor respeta los subíndices y supraíndices. "
            "Si no encuentras la definición o teorema solicitada, avisa que ésta no se encuentra en el material de la cátedra."
            "Si la respuesta no está en el texto, indica que deben comunicarse con la Profesora Jorgelina por mail."
        )),
        ChatMessage(role="user", content=f"Material de la materia Estadística Inferencial:\n\n{contexto}"),
        ChatMessage(role="user", content=pregunta),
    ]
    # Consultar el modelo
    respuesta = llm.chat(mensajes)
    return respuesta





st.title("Asistente Inteligente")
#pregunta = st.text_input("Ingrese su pregunta aquí:")

with st.form(key="form_pregunta"):
    pregunta = st.text_input("Ingrese su pregunta aquí:")
    enviar = st.form_submit_button("Enviar")  # Botón para enviar

# Si se presiona Enter o el botón, se procesa la pregunta
if enviar and pregunta:
#if st.button("Enviar"):
    #with st.spinner('Procesando su pregunta...'):
    resp = hacer_pregunta(pregunta)
    respuesta = resp.message.content.strip()  
    st.write(respuesta)




                 