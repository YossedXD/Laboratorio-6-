import streamlit as st
from concurrent.futures import ThreadPoolExecutor
import threading

# Bloqueo para evitar condiciones de carrera en procesos paralelos
lock = threading.Lock()

# Diccionarios simples de palabras positivas y negativas
positive_words = ["good", "excelente",  "Buen", "increible", "lindo "," bien", "perfecto", "love", "genial", "bueno"]
negative_words = ["bad", "terrible", "muy malo", "dificl", "complicado", "horrible", "malo", "hate", "asqueroso", "pésimo"]

# --- Función que analiza el sentimiento de un solo comentario ---
def analyze_sentiment(text):
    """
    Analiza el comentario buscando palabras positivas o negativas.
    Devuelve 'Positivo', 'Negativo' o 'Neutro'.
    """
    score = 0
    texto = text.lower()

    # Sumar puntos por palabras positivas
    for p in positive_words:
        if p in texto:
            score += 1

    # Restar puntos por palabras negativas
    for n in negative_words:
        if n in texto:
            score -= 1

    # Clasificación
    if score > 0:
        return "Positivo"
    elif score < 0:
        return "Negativo"
    else:
        return "Neutro"

# --- Función que procesa varios comentarios en paralelo ---
def process_batch(comments):
    """
    Procesa una lista de comentarios en paralelo usando ThreadPoolExecutor.
    Cada comentario se analiza y se guarda su resultado.
    """
    results = []

    # Función interna para procesar cada comentario con bloqueo
    def worker(comment):
        with lock:  # Evitar condiciones de carrera al modificar 'results'
            sentimiento = analyze_sentiment(comment)
            results.append((comment, sentimiento))

    # Ejecutar análisis en paralelo
    with ThreadPoolExecutor() as executor:
        executor.map(worker, comments)

    return results

# --- Interfaz de usuario con Streamlit ---
st.title("Procesamiento de Comentarios en Paralelo 🧵⚡")
st.write("Ingresa varios comentarios y los analizaré al mismo tiempo.")

# Entrada de texto tipo multilinea
input_text = st.text_area("Ingresa los comentarios (uno por línea):", height=200)

# Botón para procesar
if st.button("Procesar"):
    # Convertir el texto en una lista separada por líneas
    comments = [c.strip() for c in input_text.split("\n") if c.strip() != ""]

    if not comments:
        st.warning("⚠️ No ingresaste ningún comentario.")
    else:
        # Procesar comentarios
        resultados = process_batch(comments)

        st.subheader("Resultados del Análisis")
        for comentario, sentimiento in resultados:
            st.write(f"**{comentario}** → 🟢 {sentimiento}" if sentimiento == "Positivo" else
                     f"**{comentario}** → 🔴 {sentimiento}" if sentimiento == "Negativo" else
                     f"**{comentario}** → 😐 {sentimiento}")
