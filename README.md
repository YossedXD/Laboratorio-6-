# Laboratorio 6 

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
