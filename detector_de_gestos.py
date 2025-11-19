import threading
import time
import cv2
import mediapipe as mp
import streamlit as st
from threading import Semaphore, Lock
import math

# ------------------------
# Mediapipe
# ------------------------
mp_manos = mp.solutions.hands
mp_dibujo = mp.solutions.drawing_utils

# ------------------------
# Variables compartidas
# ------------------------
compartido = {
    "frame": None,
    "frame_anotado": None,
    "texto_gesto": "",
    "activo": False
}

frames_disponibles = Semaphore(0)
candado = Lock()


# -------------------------------------------------------
# HILO DE CÁMARA
# -------------------------------------------------------
def hilo_camara(indice_cam=0):
    camara = cv2.VideoCapture(indice_cam, cv2.CAP_DSHOW)

    if not camara.isOpened():
        with candado:
            compartido["texto_gesto"] = "ERROR: No se pudo abrir la cámara."
            compartido["activo"] = False
        return

    while True:
        with candado:
            if not compartido["activo"]:
                break

        ok, frame = camara.read()
        if not ok:
            continue

        with candado:
            compartido["frame"] = frame.copy()

        frames_disponibles.release()
        time.sleep(0.01)

    camara.release()


# -------------------------------------------------------
# FUNCIÓN DE DETECCIÓN DE GESTOS
# -------------------------------------------------------
def clasificar_gesto(lm):
    """Clasifica gesto según dedos levantados y distancias"""

    puntas = [4, 8, 12, 16, 20]
    nudillos = [2, 6, 10, 14, 18]

    # Pulgar en eje X
    pulgar = 1 if lm[4][0] < lm[3][0] else 0

    # Otros dedos en eje Y
    dedos = [1 if lm[t][1] < lm[p][1] else 0 for t, p in zip(puntas[1:], nudillos[1:])]
    dedos_arriba = [pulgar] + dedos
    total = sum(dedos_arriba)

    # OK
    if math.dist(lm[4], lm[8]) < 35:
        return "👌 OK"

    # Pulgar arriba
    if dedos_arriba[0] == 1 and sum(dedos_arriba[1:]) == 0:
        return "👍 Pulgar Arriba"

    # Pulgar abajo
    if dedos_arriba[0] == 0 and sum(dedos_arriba[1:]) == 0 and lm[4][1] > lm[3][1]:
        return "👎 Pulgar Abajo"

    # Paz / Victoria
    if dedos_arriba[1] == 1 and dedos_arriba[2] == 1 and dedos_arriba[3] == 0 and dedos_arriba[4] == 0:
        return "✌️ Paz"

    # Puño cerrado
    if total == 0:
        return "✊ Puño"

    # Mano abierta
    if total == 5:
        return "🖐️ Mano Abierta"

    return f"Dedos levantados: {total}"


# -------------------------------------------------------
# HILO DE PROCESAMIENTO
# -------------------------------------------------------
def hilo_procesamiento():
    manos = mp_manos.Hands(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
        max_num_hands=2
    )

    while True:

        frames_disponibles.acquire()

        with candado:
            if not compartido["activo"]:
                frames_disponibles.release()
                break

            frame = compartido["frame"].copy() if compartido["frame"] is not None else None

        if frame is None:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = manos.process(rgb)

        frame_anotado = frame.copy()
        texto = ""

        if resultados.multi_hand_landmarks:
            for landmarks_mano, lado in zip(resultados.multi_hand_landmarks,
                                            resultados.multi_handedness):

                mp_dibujo.draw_landmarks(
                    frame_anotado, landmarks_mano, mp_manos.HAND_CONNECTIONS
                )

                h, w, _ = frame_anotado.shape
                lm = [(int(l.x * w), int(l.y * h)) for l in landmarks_mano.landmark]

                gesto = clasificar_gesto(lm)
                etiqueta = lado.classification[0].label  # "Left" or "Right"

                texto += f"*{etiqueta}:* {gesto}  \n"

        else:
            texto = "Sin manos detectadas"

        with candado:
            compartido["frame_anotado"] = frame_anotado
            compartido["texto_gesto"] = texto

    manos.close()


# -------------------------------------------------------
# INTERFAZ STREAMLIT
# -------------------------------------------------------
st.set_page_config(page_title="Detector de Gestos (2 manos)")
st.title("🤜🤛 Detector de Gestos con DOS MANOS — MediaPipe + Hilos")

boton_iniciar = st.button("Iniciar cámara")
boton_detener = st.button("Detener cámara")

zona_video = st.empty()
zona_texto = st.empty()

if boton_iniciar:
    with candado:
        if not compartido["activo"]:
            compartido["activo"] = True
            t1 = threading.Thread(target=hilo_camara, daemon=True)
            t2 = threading.Thread(target=hilo_procesamiento, daemon=True)
            t1.start()
            t2.start()

if boton_detener:
    with candado:
        compartido["activo"] = False

while True:
    with candado:
        activo = compartido["activo"]
        anotado = compartido["frame_anotado"]
        gesto_detectado = compartido["texto_gesto"]

    if anotado is not None:
        rgb = cv2.cvtColor(anotado, cv2.COLOR_BGR2RGB)
        zona_video.image(rgb, channels="RGB")

    zona_texto.markdown(f"### {gesto_detectado}")

    if not activo:
        break

    time.sleep(0.05)

st.write("Aplicación Finalizada")