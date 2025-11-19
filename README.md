# Laboratorio 6 
# 1 Punto Analizador de Sentimientos — Hilos + Streamlit + Docker

Este proyecto implementa un **sistema de análisis de sentimientos en paralelo** usando:

- Python `threading`
- Locks para evitar condiciones de carrera
- Análisis de sentimientos basado en diccionarios
- Streamlit para interfaz visual
- Docker para despliegue del aplicativo

Procesa **lotes grandes de comentarios en paralelo**, clasificándolos como:

-  Positivos  
-  Negativos  
-  Neutros  

---

# 1. Objetivo

Procesar textos en paralelo para analizar emociones usando hilos, integrando:

- Programación concurrente  
- Sincronización con `Lock`
- Interfaz web con Streamlit
- Despliegue mediante Docker

---

#  2. Descripción del Proyecto

El sistema recibe un **lote de comentarios**, por ejemplo opiniones de productos o reseñas de usuarios.

Luego:

1. Se divide el conjunto de comentarios entre varios hilos.
2. Cada hilo procesa su subconjunto y clasifica el sentimiento aplicando un diccionario de palabras positivas y negativas.
3. Los resultados se guardan en una lista compartida protegida con `Lock`.
4. Streamlit presenta:
   - Cantidad de comentarios procesados
   - Estadísticas
   - Listado completo de comentarios y clasificación final
5. Finalmente se empaqueta en Docker.

---

#  3. Condiciones de Carrera y Solución

Como varios hilos escriben sobre la **misma lista compartida**, existe riesgo de:

 Datos mezclados  
 Pérdida de información  
 Inconsistencia entre hilos  

###  Solución: Lock (Mutual Exclusion)

Se utiliza:

```python
lock = threading.Lock()
```
Cada vez que un hilo va a escribir en la lista:
```python
with lock:
    resultados.append({...})
```

Esto garantiza que solo un hilo escribe a la vez, evitando conflictos.

4. Implementación de Hilos

Los hilos se crean así:
```python
for i in range(num_hilos):
    hilo = threading.Thread(target=procesar_comentarios, args=(sublista,i))
    hilos.append(hilo)
    hilo.start()
```

Luego:
```python
for h in hilos:
    h.join()

```
Esto asegura:

Ejecución paralela

Sincronización al terminar

Seguridad al escribir

5. Método de Clasificación del Sentimiento

Se usa un diccionario simple:
```python
positivas = ["excelente", "bueno", "me encantó", "satisfecho"]
negativas = ["malo", "terrible", "defectuoso", "horrible"]
```

Clasificación:

Si predominan palabras positivas → positivo

Si predominan palabras negativas → negativo

Si están equilibradas o no aparecen → neutro

También se aplican normalización y limpieza del texto.

6. Interfaz Visual con Streamlit

Streamlit permite:

Cargar archivo de comentarios o escribir manualmente

Ejecutar análisis

Mostrar tabla con resultados por hilo

Mostrar gráficos y estadísticas

Ver cada comentario con color según su sentimiento

Ejemplo de ejecución:
```python

streamlit run app.py
```

7. Estructura del Proyecto

Analizadora Sentimientos/
│── app.py
│── requirements.txt
│── Dockerfile
│── comentarios.txt
│── imagenes/
      ├── docker_build.png
      ├── pagina_streamlit.png
      ├── comentarios_clasificados.png

8. requirements.txt
```python
streamlit
```
9. Dockerfile
```python
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
COPY app.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

10. Construcción del Contenedor

Desde la carpeta del proyecto:
```python

docker build -t analizador-sentimientos .
```

Ejemplo real de tu consola:
```python
docker build -t analizador-sentimientos .
[+] Building 58.4s (10/10) FINISHED
```
11. Ejecutar el contenedor
```python  
docker run -p 8501:8501 analizador-sentimientos

```
Salida esperada:
```python
You can now view your Streamlit app in your browser.
URL: http://0.0.0.0:8501
```

Luego abres:

 http://localhost:8501

 12. Galería de Imágenes (añade aquí tus capturas)
 Docker Build

<img width="1473" height="521" alt="image" src="https://github.com/user-attachments/assets/24107b48-bb12-49ff-81b0-48d2c56fb2bd" />

<img width="1452" height="558" alt="image" src="https://github.com/user-attachments/assets/3c3d1a20-db41-490a-a023-ca5716d51b72" />

 Aplicación Streamlit Corriendo
 
 <img width="1585" height="759" alt="image" src="https://github.com/user-attachments/assets/f3209b4b-bb99-407b-b613-68a3fa912601" />
 
<img width="1056" height="858" alt="image" src="https://github.com/user-attachments/assets/eefd878f-216c-42a7-a445-c900f2d3beff" />


 Comentarios Clasificados
 
 <img width="648" height="841" alt="image" src="https://github.com/user-attachments/assets/7bdcaa8b-5a34-4df7-9dc8-63829ff4e988" />
   

# Punto 2 

# Juego 2D Tipo Mario Bros con Hilos, Mutex, Semáforos y Docker

Este proyecto implementa un videojuego 2D estilo plataformas, utilizando conceptos avanzados de **programación concurrente**:

- Hilos (threads)
- Sección crítica
- Mutex (locks)
- Semáforos
- Sincronización de recursos compartidos
- Docker para aislar la ejecución

El objetivo es recrear una dinámica similar a la de Mario Bros, donde existen plataformas, enemigos, monedas, puntuación, vidas y pantalla de Game Over.

---

##  1. Objetivo del Proyecto

Implementar mecánicas clásicas de plataformas en 2D usando:

- **Hilos** para manejar elementos independientes
- **Mutex y semáforos** para sincronizar recursos compartidos
- **Docker** para ejecutar el juego en un entorno controlado

---

##  2. Arquitectura del Juego

El juego se compone de varios módulos clave:

###  Jugador
- Controlado por teclado.
- Afectado por gravedad.
- Saltos y movimiento lateral.
- Vidas y puntaje.
- Colisiones con plataformas.
- Tiene un **hilo adicional** que controla un período de invulnerabilidad temporal.

###  Enemigos
- Cada enemigo corre en **su propio hilo**.
- Se mueven de forma independiente.
- Colisionan con el jugador.
- Si lo tocan → pierde vida.
- Se usa un **semáforo** para limitar cuántos enemigos pueden existir al mismo tiempo.

###  Monedas
- Caen desde la parte superior.
- El jugador las recoge para sumar puntos.
- Un **hilo adicional** controla su respawn automático.

###  Plataformas
- El jugador puede pararse encima.
- Se manejan mediante colisiones rectangulares.

---

##  3. Detalle del Uso de Hilos

Estos son los hilos activos durante la ejecución:

###  Hilo principal del juego
- Dibuja la pantalla.
- Procesa teclas.
- Calcula física y colisiones.
- Actualiza HUD.

###  Hilos de enemigos
Cada enemigo tiene un hilo independiente:

```python
thread = threading.Thread(target=enemigo.mover)
thread.start()
```
Cada hilo actualiza constantemente:

- Su posición
- Colisiones con el jugador
- Movimiento horizontal

 ### hilo de respawn de monedas
 Genera monedas nuevas cada cierto tiempo:
```python
 threading.Thread(target=generar_monedas).start()
 ```

 ### Hilo de invulnerabilidad del jugador

Cuando el jugador recibe daño:
```python
threading.Thread(target=self.invulnerabilidad).start()
 ```
 Durante unos segundos el jugador no puede volver a perder vida.

 ### 4. Sección Crítica y Mutex

Como hay múltiples hilos accediendo a listas compartidas (enemigos, monedas, puntaje), se usa un mutex:
```python

mutex = threading.Lock()

with mutex:
    lista_enemigos.append(nuevo_enemigo)
 ```

Esto evita condiciones de carrera cuando varios hilos modifican datos al tiempo.

### 5. Semáforos

Para limitar la cantidad de enemigos simultáneos se utiliza:
```python
sem_enemigos = threading.Semaphore(5)
```

Cada enemigo hace:
```python
sem_enemigos.acquire()
```

Y al morir:
```python
sem_enemigos.release()
```

### 6. Dockerización del Proyecto

El proyecto puede ejecutarse dentro de un contenedor Docker para asegurar compatibilidad.
```python
Dockerfile
FROM python:3.11-slim

# Dependencias para pygame + entorno gráfico mínimo
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 python3-tk python3-dev xvfb xauth x11-apps \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "juego.py"]
```

 requirements.txt
```python
pygame==2.6.1
```
 Construcción
 ```python
docker build -t juego-hilos .
```
 Ejecución
 ```python
docker run --rm juego-hilos
```
Si tu sistema usa WSL o X11, puede requerir configuración adicional para mostrar la ventana gráfica

### 7. Capturas del Juego

### Pantalla principal del juego

<img width="1245" height="791" alt="image" src="https://github.com/user-attachments/assets/f8a7c61e-7670-49ec-bf91-4c38add73f34" />

### Caída de monedas
<img width="1242" height="787" alt="image" src="https://github.com/user-attachments/assets/4866e3fd-1874-469b-8a6b-38d5e0c604b3" />

### Enemigos moviéndose en hilos
<img width="1258" height="801" alt="image" src="https://github.com/user-attachments/assets/6ef8eb90-48e5-4e4a-b01e-17fe9cef39b5" />

### Game Over
<img width="1244" height="776" alt="image" src="https://github.com/user-attachments/assets/f930f240-32be-4fa3-ac47-b07b94ad4677" />

### Docker Build
<img width="1459" height="384" alt="image" src="https://github.com/user-attachments/assets/aa7b0196-ade6-422c-abdf-80eae89f0f33" />

### Docker completo
<img width="1467" height="583" alt="image" src="https://github.com/user-attachments/assets/12638e1e-199d-4175-9b4c-ed86d2874119" />

### 8. Ejecución Local (sin Docker)
```python
pip install pygame
python juego.py
```




# 3 Punto Detector de Gestos con DOS Manos — MediaPipe + Hilos + Mutex + Semáforos + Docker

Este proyecto desarrolla un sistema capaz de **detectar gestos de mano en tiempo real** usando:

- **MediaPipe Hands**
- **OpenCV**
- **Programación concurrente (hilos, mutex, semáforos)**
- **Streamlit**
- **Docker**

Se detectan gestos como:
-  OK  
-  Pulgar Arriba  
-  Pulgar Abajo  
-  Paz  
-  Puño Cerrado  
-  Mano Abierta  

Además, el sistema soporta **detección simultánea de 2 manos**.

---

#  1. Objetivo

Implementar un algoritmo sencillo pero completo que detecte diferentes gestos de mano utilizando:

- MediaPipe
- Hilos
- Semáforos
- Mutex y sección crítica
- Aplicación web con Streamlit
- Contenedor en Docker

---

#  2. Arquitectura General del Sistema

El sistema utiliza 3 hilos principales:

###  **Hilo 1 – Captura de Cámara**
- Obtiene frames de la cámara en tiempo real.
- Coloca cada frame en la variable compartida `compartido["frame"]`.
- Usa un `Semaphore` para indicar que hay un frame listo.

###  **Hilo 2 – Procesamiento de Gestos**
- Consume frames desde el semáforo.
- Ejecuta MediaPipe Hands.
- Clasifica el gesto detectado.
- Genera el frame anotado.
- Guarda resultados en variables compartidas.

###  **Hilo 3 – Interfaz Streamlit**
- Muestra el video procesado.
- Renderiza los gestos detectados.
- Controla botones de inicio/detención.

---

#  3. Recursos Compartidos, Mutex y Sección Crítica

El sistema usa:

##  **Mutex (`Lock`)**  
Protege el acceso a la estructura:

```python
compartido = {
    "frame": None,
    "frame_anotado": None,
    "texto_gesto": "",
    "activo": False
}
```

Solo un hilo puede modificar estos valores a la vez.

 Semáforo (Semaphore)
```python

frames_disponibles = Semaphore(0)

```
Controla cuándo el hilo de procesamiento puede obtener un nuevo frame.
Evita  sobrecarga o duplicación de frames.

4. Detección de Gestos con MediaPipe

Cada mano tiene 21 puntos (landmarks).
Se clasifica el gesto calculando:

- Dedos levantados
- Distancia entre pulgar y índice (OK)
- Posición del pulgar (arriba/abajo)
- Combinaciones para paz, puño, mano abierta

Ejemplo de lógica de dedo levantado:
```python
# Dedo levantado si la punta está más arriba que el nudillo
dedos = [1 if lm[t][1] < lm[p][1] else 0 for t, p in zip(puntas[1:], nudillos[1:])]
```
5. Flujo Completo
 Streamlit → botón "Iniciar cámara"

Activa el flag activo = True y lanza:

hilo de cámara

hilo de procesamiento

Hilo cámara captura video

Guarda los frames y libera el semáforo.

 Hilo procesamiento usa MediaPipe

Añade puntos + conexiones
Clasifica gesto
Devuelve texto + frame anotado

 Streamlit muestra todo en tiempo real

 6. Estructura del Proyecto
 gestos/
│── detector_de_gestos.py
│── requirements.txt
│── Dockerfile
│── imagenes/
      ├── captura1.png
      ├── captura2.png
      ├── pulgar_arriba.png
      ├── ok.png
      ├── streamlit.png
      ├── docker_build.png

 7. Instalación Local
```python
      pip install streamlit opencv-python mediapipe
streamlit run detector_de_gestos.py
```
Si OpenCV falla:
```python

Copiar código
pip install opencv-python-headless
```
8. Dockerización del Proyecto
requirements.txt
```python
streamlit
opencv-python
mediapipe
```
Dockerfile
```python
FROM python:3.10

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY detector_de_gestos.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "detector_de_gestos.py", "--server.address=0.0.0.0"]
```
9. Construcción y Ejecución del Contenedor
🔧 Construir imagen
```python
docker build -t detector-gestos .
```
▶️ Ejecutar
```python
docker run -p 8501:8501 detector-gestos

```
Abre en navegador:
```python

http://localhost:8501
```
10. Galería de Imágenes

Imaganes del punto 3

Detección de dos manos
 <img width="943" height="789" alt="image" src="https://github.com/user-attachments/assets/61b6b5c3-d520-4c9b-8272-14bb57d11534" />

 Pulgar arriba

<img width="936" height="834" alt="image" src="https://github.com/user-attachments/assets/f0246444-65bf-42d1-a01f-a3cc90b395b3" />
    
    
  Pulgar abajo
    <img width="926" height="827" alt="image" src="https://github.com/user-attachments/assets/0164f198-9bc0-4641-84c3-b69ba5098734" />

Gesto OK
 <img width="886" height="819" alt="image" src="https://github.com/user-attachments/assets/25eefe8e-c7cb-461d-b32e-0f3c3178852c" />

prueba puño
  <img width="894" height="829" alt="image" src="https://github.com/user-attachments/assets/9ca64eb9-dce5-4824-a5c7-657c2e6ee386" />

prueba manos abiertas
 <img width="891" height="830" alt="image" src="https://github.com/user-attachments/assets/3b4f8286-5b0a-4511-b7c7-bfc20c6caa62" />


Imagen del contenedor construido

<img width="1445" height="684" alt="image" src="https://github.com/user-attachments/assets/6460c94b-afa8-47a7-8b4c-21388e035da7" />
<img width="1461" height="644" alt="image" src="https://github.com/user-attachments/assets/cb37b75b-d226-49db-8ee3-ae46bb1890f2" />


### 9. Autores

Laboratorio 6 realizado por:

Miguel Montaña

Jeferson Hernández (Jefry)

Yossed Riaño

### 10. Conclusiones

Este laboratorio permitió aplicar conceptos fundamentales de concurrencia en un entorno real:

Manejo de múltiples hilos simultáneos.

Sección crítica controlada con mutex.

Semáforos para regular acceso a recursos.

Independencia y paralelismo en los enemigos.

Contenedorización con Docker para asegurar portabilidad.

Integración de todos estos elementos en un videojuego completamente funcional.

El proyecto demuestra cómo la programación concurrente mejora la fluidez, el rendimiento y la modularidad en aplicaciones interactivas como videojuegos.
