"""
juego.py  - Juego completo con hilos, mutex, plataformas, monedas y enemigos.
Rutas de imágenes deben estar en la misma carpeta:
  - HD-wallpaper-sonic-game-cool-retro.jpg
  - Doctor lab.png
  - Enemigo.png
  - MONEDA.jpg
Controles:
  - Izquierda/Derecha: flechas o A/D
  - Saltar: Barra espaciadora
  - Salir: cerrar ventana
"""

import pygame
import threading
import time
import random
from pathlib import Path

# ---------------- CONFIG ----------------
pygame.init()
ANCHO, ALTO = 1000, 600
FPS = 60
MAX_ENEMIGOS = 8

ROOT = Path(".")  # si quieres usar rutas absolutas, cámbialo
FONDO_IMG = "HD-wallpaper-sonic-game-cool-retro.jpg"
JUGADOR_IMG = "Doctor lab.png"
ENEMIGO_IMG = "Enemigo.png"
MONEDA_IMG = "MONEDA.jpg"

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego con Hilos - Versión Completa")
reloj = pygame.time.Clock()

# ---------------- CARGA RECURSOS ----------------
def cargar_imagen_safe(name, size=None):
    try:
        surf = pygame.image.load(name).convert_alpha()
        if size:
            surf = pygame.transform.smoothscale(surf, size)
        return surf
    except Exception as e:
        print(f"[WARN] No se pudo cargar {name}: {e}")
        # superficie de fallback
        s = pygame.Surface(size if size else (50, 50), pygame.SRCALPHA)
        s.fill((255, 0, 255, 200))
        return s

fondo_surf = cargar_imagen_safe(FONDO_IMG, (ANCHO, ALTO))
jugador_surf = cargar_imagen_safe(JUGADOR_IMG, (64, 88))
enemigo_surf = cargar_imagen_safe(ENEMIGO_IMG, (48, 48))
moneda_surf = cargar_imagen_safe(MONEDA_IMG, (28, 28))

# ---------------- ENTIDADES / MUNDO ----------------
# Plataformas (x, y, width, height)
plataformas = [
    pygame.Rect(40, ALTO - 40, ANCHO - 80, 40),   # suelo amplio (visible)
    pygame.Rect(60, 420, 160, 18),
    pygame.Rect(300, 360, 200, 18),
    pygame.Rect(640, 320, 220, 18),
    pygame.Rect(200, 240, 150, 18),
    pygame.Rect(480, 180, 160, 18)
]

# Jugador - representado por rect para colisiones
jug_w, jug_h = 48, 72
jug_start_x = 120
jug_start_y = plataformas[1].top - jug_h  # spawn seguro sobre plataforma 1
jugador_rect = pygame.Rect(jug_start_x, jug_start_y, jug_w, jug_h)
vel_x = 0
vel_y = 0
GRAVEDAD = 0.8
MAX_FALL_SPEED = 14
SPEED = 5
JUMP_SPEED = -14

# Estado del juego
vidas = 3
puntos = 0
invulnerable = True  # protección inicial
invulnerable_time = 2.0  # segundos
game_active = True

# Enemigos y monedas (listas compartidas)
enemigos = []      # cada item: dict {rect, vx}
monedas = []       # cada item: pygame.Rect

# Sincronización
lock = threading.Lock()
sem_enemigos = threading.Semaphore(MAX_ENEMIGOS)

# Hilos listos (solo para contar/limpiar)
threads = []

# ---------------- UTIL ----------------
def rects_overlap(rect1, rect2):
    return rect1.colliderect(rect2)

def spawn_moneda_on_platform(platform):
    x = random.randint(platform.left + 10, platform.right - 10 - 28)
    y = platform.top - 28 - 4
    return pygame.Rect(x, y, 28, 28)

def spawn_safe_enemy(avoid_rect, platforms):
    """
    Crea un enemigo en una plataforma pero evita aparecer encima del jugador.
    Retorna un pygame.Rect.
    """
    attempts = 0
    while attempts < 100:
        p = random.choice(platforms[1:])  # no spawnear en el suelo principal (index 0)
        ex = random.randint(p.left + 8, p.right - 48)
        ey = p.top - 48
        r = pygame.Rect(ex, ey, 48, 48)
        if not r.colliderect(avoid_rect.inflate(140, 120)):
            return r
        attempts += 1
    # fallback: spawn en esquina segura
    return pygame.Rect(20, platforms[1].top - 48, 48, 48)

# ---------------- CREAR MONEDAS INICIALES ----------------
with lock:
    for _ in range(6):
        plat = random.choice(plataformas[1:])
        monedas.append(spawn_moneda_on_platform(plat))

# ---------------- HILOS: ENEMIGOS ----------------
def enemy_thread_logic(enemy_index):
    """
    Mueve un enemigo continuamente. Usa lock para actualizar su recto en la lista compartida.
    Cuando game_active=False el hilo termina.
    """
    global enemigos, game_active
    try:
        # cada enemigo tiene su propia velocidad horizontal
        with lock:
            if enemy_index >= len(enemigos):
                return
            enemigos[enemy_index]['vx'] = random.choice([-2, -1, 1, 2])

        while game_active:
            with lock:
                if enemy_index >= len(enemigos):
                    return
                e = enemigos[enemy_index]
                rect = e['rect']
                vx = e.get('vx', 2)
                rect.x += vx
                # rebotar con límites de su plataforma (si hay)
                # buscaremos la plataforma debajo del enemigo
                plat_below = None
                for p in plataformas:
                    if rect.bottom <= p.top + 6 and rect.bottom >= p.top - 6 and rect.centerx >= p.left and rect.centerx <= p.right:
                        plat_below = p
                        break
                if plat_below:
                    if rect.left < plat_below.left + 8 or rect.right > plat_below.right - 8:
                        # invertir dirección
                        e['vx'] = -vx
                else:
                    # si está sin plataforma (teórico), desplazarlo hacia arriba hasta plataforma más cercana
                    rect.y = max(0, rect.y - 2)
            time.sleep(0.03)
    finally:
        # liberamos semáforo cuando el hilo muere
        try:
            sem_enemigos.release()
        except:
            pass

def spawn_enemy_background_loop():
    """
    Hilo que periódicamente intenta crear enemigos respetando el semáforo MAX_ENEMIGOS.
    """
    global enemigos, game_active
    while game_active:
        acquired = sem_enemigos.acquire(timeout=0.1)
        if not acquired:
            time.sleep(0.8)
            continue
        with lock:
            # spawn lejos del jugador
            r = spawn_safe_enemy(jugador_rect, plataformas)
            enemigos.append({'rect': r, 'vx': random.choice([-2, 2])})
            idx = len(enemigos) - 1
            t = threading.Thread(target=enemy_thread_logic, args=(idx,), daemon=True)
            threads.append(t)
            t.start()
        time.sleep(random.uniform(1.0, 2.5))

# iniciar unos enemigos iniciales (con semáforo)
def create_initial_enemies(count=4):
    global enemigos
    for _ in range(count):
        if not sem_enemigos.acquire(blocking=False):
            break
        with lock:
            r = spawn_safe_enemy(jugador_rect, plataformas)
            enemigos.append({'rect': r, 'vx': random.choice([-2, 2])})
            idx = len(enemigos) - 1
            t = threading.Thread(target=enemy_thread_logic, args=(idx,), daemon=True)
            threads.append(t)
            t.start()

# ---------------- HILO: MONEDAS QUE RESPAWNEAN ----------------
def coin_respawn_loop():
    global monedas, game_active
    while game_active:
        with lock:
            # mantener al menos 5 monedas
            if len(monedas) < 5:
                plat = random.choice(plataformas[1:])
                monedas.append(spawn_moneda_on_platform(plat))
        time.sleep(1.0)

# ---------------- INVULNERABILIDAD AL INICIO ----------------
def invulnerability_timer():
    global invulnerable
    time.sleep(invulnerable_time)
    invulnerable = False

# ---------------- INICIO HILOS ----------------
create_initial_enemies(5)  # crea 5 enemigos iniciales
t_spawn_enemies = threading.Thread(target=spawn_enemy_background_loop, daemon=True)
threads.append(t_spawn_enemies)
t_spawn_enemies.start()

t_coin = threading.Thread(target=coin_respawn_loop, daemon=True)
threads.append(t_coin)
t_coin.start()

t_inv = threading.Thread(target=invulnerability_timer, daemon=True)
threads.append(t_inv)
t_inv.start()

# ---------------- FUNCIONES DE JUEGO ----------------
def handle_player_movement(keys):
    global vel_x
    vel_x = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        vel_x = -SPEED
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        vel_x = SPEED

def apply_physics():
    global vel_y, jugador_rect, puntos, vidas, invulnerable, game_active

    # aplicar gravedad
    vel_y += GRAVEDAD
    if vel_y > MAX_FALL_SPEED:
        vel_y = MAX_FALL_SPEED
    jugador_rect.y += int(vel_y)

    # horizontal movement bounds
    if jugador_rect.left < 0:
        jugador_rect.left = 0
    if jugador_rect.right > ANCHO:
        jugador_rect.right = ANCHO

    # colisiones verticales - plataformas y suelo (detección desde arriba)
    on_ground = False
    for p in plataformas:
        if jugador_rect.colliderect(p):
            # comprobamos que veníamos desde arriba
            if vel_y >= 0 and jugador_rect.bottom - vel_y <= p.top + 4:
                jugador_rect.bottom = p.top
                vel_y = 0
                on_ground = True

    # Si baja hasta el fondo del mundo, resetear posición y quitar vida
    if jugador_rect.top > ALTO + 200:
        # caída mortal
        vidas -= 1
        if vidas <= 0:
            game_active = False
        else:
            # re-spawn seguro
            with lock:
                jugador_rect.x = jug_start_x
                jugador_rect.y = jug_start_y
                vel_y = 0
                # temporal invulnerability breve
                invulnerable = True
                threading.Thread(target=lambda: (time.sleep(1.2), set_inv(False)), daemon=True).start()

    return on_ground

def set_inv(val: bool):
    global invulnerable
    invulnerable = val

def player_jump():
    global vel_y
    # solo saltar si tocando plataforma desde arriba
    # comprobación simple: mover 1px hacia abajo y ver si hay colisión
    jugador_rect.y += 2
    touching = any(jugador_rect.colliderect(p) for p in plataformas)
    jugador_rect.y -= 2
    if touching:
        vel_y = JUMP_SPEED

# ---------------- BUCLE PRINCIPAL ----------------
font_hud = pygame.font.SysFont("Arial", 28, True)

while True:
    dt = reloj.tick(FPS) / 1000.0
    # eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            game_active = False
            pygame.quit()
            raise SystemExit
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                player_jump()

    keys = pygame.key.get_pressed()
    handle_player_movement(keys)

    # mover jugador horizontalmente
    with lock:
        jugador_rect.x += vel_x

    # aplicar física
    on_ground = apply_physics()

    # detectar colisiones con monedas
    with lock:
        for m in monedas[:]:
            if jugador_rect.colliderect(m):
                puntos += 1
                try:
                    monedas.remove(m)
                except ValueError:
                    pass

    # detección de colisión con enemigos (solo si no invulnerable)
    if not invulnerable:
        with lock:
            for e in list(enemigos):
                er = e['rect']
                if jugador_rect.colliderect(er):
                    # si el jugador cae sobre el enemigo (pequeño margen, vel_y>0)
                    if vel_y > 0 and jugador_rect.bottom - er.top < 20:
                        # matar enemigo
                        try:
                            enemigos.remove(e)
                        except ValueError:
                            pass
                        try:
                            sem_enemigos.release()
                        except:
                            pass
                        puntos += 10
                        vel_y = JUMP_SPEED / 1.6  # pequeño rebote
                    else:
                        # daño al jugador
                        vidas -= 1
                        invulnerable = True
                        threading.Thread(target=lambda: (time.sleep(1.2), set_inv(False)), daemon=True).start()
                        if vidas <= 0:
                            game_active = False

    # DIBUJO
    pantalla.blit(fondo_surf, (0, 0))

    # dibujar plataformas (con bing)
    for p in plataformas:
        pygame.draw.rect(pantalla, (100, 50, 10), p)

    # dibujar monedas
    with lock:
        for m in monedas:
            pantalla.blit(moneda_surf, (m.x, m.y))

    # dibujar enemigos
    with lock:
        for e in enemigos:
            pantalla.blit(enemigo_surf, (e['rect'].x, e['rect'].y))

    # dibujar jugador (si invulnerable parpadea)
    if invulnerable and (int(time.time() * 5) % 2 == 0):
        # parpadeo: dibujar semi-transparente
        img = jugador_surf.copy()
        img.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_MULT)
        pantalla.blit(img, (jugador_rect.x - (jug_w//2 - 1), jugador_rect.y - (jug_h - jug_h),))
    else:
        pantalla.blit(jugador_surf, (jugador_rect.x - (jug_w//2 - 1), jugador_rect.y))

    # HUD
    with lock:
        threads_count = sum(1 for t in threads if t.is_alive()) + 1  # sumar 1 por hilo main en counting-approx
        enemigos_count = len(enemigos)
    hud_text = f"Vidas: {vidas}    Puntos: {puntos}    Hilos activos: {threads_count}    Enemigos: {enemigos_count}"
    hud_surf = font_hud.render(hud_text, True, (255, 255, 255))
    pantalla.blit(hud_surf, (12, 8))

    # si el juego terminó, mostrar GAME OVER
    if not game_active:
        go_font = pygame.font.SysFont("Arial", 78, True)
        go_s = go_font.render("GAME OVER", True, (255, 30, 30))
        pantalla.blit(go_s, (ANCHO//2 - go_s.get_width()//2, ALTO//2 - go_s.get_height()//2))
        pygame.display.flip()
        # detener hilos y esperar 2s antes de salir
        time.sleep(2)
        pygame.quit()
        raise SystemExit

    pygame.display.flip()
