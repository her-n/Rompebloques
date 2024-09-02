import tkinter.messagebox
import pygame
import sys
import random
import time
import os
import tkinter


# Inicializar Pygame
pygame.init()
pygame.mixer.init()
pygame.font.init()

# Crear una pantalla
screen_info = pygame.display.Info()
ALTO = screen_info.current_h
ANCHO = screen_info.current_w
screen = pygame.display.set_mode((ANCHO, ALTO))

# Establecer el título de la ventana
pygame.display.set_caption("Rompebloques")

# Definir colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
VERDE = (181, 255, 10, 0.91)

# LAs rutas de la musica
base_dir = os.path.dirname(os.path.abspath(__file__))

RUTA_SONIDO_GAME_OVER = os.path.join(base_dir, "game_over.mp3")
RUTA_SONIDO_POTENCIADOR = os.path.join(base_dir, "potenciador.mp3")
RUTA_SONIDO_REBOTE = os.path.join(base_dir, "rebote.mp3")
RUTA_MUSICA = os.path.join(base_dir, "musica.mp3")
RUTA_ESTADO_JUEGO = os.path.join(base_dir, "estado_juego.json")


# Colores del arcoíris
COLORES_ARCOIRIS = [
    (148, 0, 211),   # Violeta
    (75, 0, 130),    # Índigo
    (0, 0, 255),     # Azul
    (0, 255, 0),     # Verde
    (255, 255, 0),   # Amarillo
    (255, 127, 0),   # Naranja
    (255, 0, 0)      # Rojo
]


# Definir sonidos y música
sonido_game_over = pygame.mixer.Sound(RUTA_SONIDO_GAME_OVER)
sonido_potenciador = pygame.mixer.Sound(RUTA_SONIDO_POTENCIADOR)
sonido_rebote = pygame.mixer.Sound(RUTA_SONIDO_REBOTE)
pygame.mixer.music.load(RUTA_MUSICA)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

def gameover():
    root = tkinter.Tk()
    root.withdraw()
    sonido_game_over.play()
    pygame.mixer.music.set_volume(0)
    tkinter.messagebox.showinfo("GAME OVER", "Has perdido. ¡Mas suerte las próxima vez!")
    root.destroy()
    sys.exit()
    pygame.quit()


# Clase de la pelota
class Pelota:
    def __init__(self, x, y):
        self.posicion = [x, y]
        self.radio = 10  # Tamaño de la pelota
        self.rect = pygame.Rect(x, y, self.radio, self.radio)
        self.color = VERDE
        self.velocidad_x = random.choice([7, -7])
        self.velocidad_y = random.choice([7, -7])
        self.vidas = 3

    def mover(self):
        self.posicion[0] += self.velocidad_x
        self.posicion[1] += self.velocidad_y

        # Actualizar el rectángulo de la pelota
        self.rect.topleft = (self.posicion[0], self.posicion[1])

        # Detectar colisiones con los bordes de la pantalla
        if self.posicion[0] <= 0 or self.posicion[0] + self.radio >= ANCHO:
            self.velocidad_x = -self.velocidad_x  # Invertir la dirección en x
        if self.posicion[1] <= 0 or self.posicion[1] + self.radio >= ALTO:
            self.velocidad_y = -self.velocidad_y  # Invertir la dirección en y

        # Detectar colisiones con el borde inferior de la pantalla
        if self.posicion[1] + self.radio >= ALTO:
            if self.vidas != 0:
                self.vidas -= 1
                if self.vidas!=0:
                    return
            self.vidas = 0
            sonido_game_over.play()
            gameover()

    def dibujar(self, pantalla):
        # Dibujar la pelota en la pantalla
        pygame.draw.rect(pantalla, self.color, self.rect)


# Clase de la paleta
class Paleta:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 170, 10)
        self.color = BLANCO
        self.velocidad_normal = 7
        self.velocidad_burst = 14
        self.velocidad = self.velocidad_normal
        self.burst_activado = False
        self.burst_preparado = True
        self.tiempo_burst = 0
        self.TIEMPO_ESPERA = 10
        self.TIEMPO_CORRIENDO = 5

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)

    def mover(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
        if keys[pygame.K_SPACE]:
            self.activar_burst()

        # Limitar la paleta dentro de los bordes de la pantalla
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > ANCHO - self.rect.width:
            self.rect.x = ANCHO - self.rect.width

    def activar_burst(self):
        if not self.burst_activado and self.burst_preparado:
            self.burst_activado = True
            self.burst_preparado = False
            self.tiempo_burst = time.time()
            self.velocidad = self.velocidad_burst
            sonido_potenciador.play()


    def verificar_burst(self):
        if self.burst_activado:
            if time.time() - self.tiempo_burst >= self.TIEMPO_CORRIENDO: # Si ya ha pasado el tiempo de burst activo
                self.velocidad = self.velocidad_normal
                self.burst_activado = False
                self.tiempo_burst = time.time()  # Reiniciar el tiempo para el cooldown

        if not self.burst_preparado:
            if time.time() - self.tiempo_burst >= self.TIEMPO_ESPERA:
                self.burst_preparado = True


# Clase Bloque
class Bloque:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)

# Crear bloques
def crear_bloques(filas, columnas, ancho_bloque, alto_bloque):
    bloques = []
    for fila in range(filas):
        for col in range(columnas):
            x = col * (ancho_bloque + 4)
            y = fila * (alto_bloque + 4)
            color = COLORES_ARCOIRIS[fila % len(COLORES_ARCOIRIS)]
            bloque = Bloque(x, y, ancho_bloque, alto_bloque, color)
            bloques.append(bloque)
    return bloques

# Función para detectar colisiones con bloques
def detectar_colisiones_bloques(pelota, bloques):
    for bloque in bloques:
        if pelota.rect.colliderect(bloque.rect):
            bloques.remove(bloque)
            pelota.velocidad_y = -pelota.velocidad_y  # Invertir la dirección de la pelota
            sonido_rebote.play()
            break  # Salir del bucle para evitar colisiones múltiples

# Reloj para controlar FPS
clock = pygame.time.Clock()

# Instancias de todos los objetos
pelota = Pelota(ANCHO // 2, ALTO // 2)
paleta = Paleta((ANCHO // 2) - (170 // 2), ALTO - 30)

# Crear una cuadrícula de bloques
filas = 7
columnas = 10
ancho_bloque = ANCHO // columnas
alto_bloque = 30
bloques = crear_bloques(filas, columnas, ancho_bloque, alto_bloque)

# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Lógica del juego
    keys = pygame.key.get_pressed()

    # Dibujar en la pantalla
    screen.fill(NEGRO)

    # Funciones de la pelota
    pelota.dibujar(screen)
    pelota.mover()

    # Detectar colisiones con la paleta
    if pelota.rect.colliderect(paleta.rect):
        pelota.velocidad_y = -pelota.velocidad_y  # Invertir la dirección en y

    # Detectar colisiones con bloques
    detectar_colisiones_bloques(pelota, bloques)

    # Dibujar bloques
    for bloque in bloques:
        bloque.dibujar(screen)

    # Funciones de la paleta
    paleta.dibujar(screen)
    paleta.mover(keys)
    paleta.verificar_burst()


    # Vidas en pantalla
    font = pygame.font.SysFont('Arial', 30)
    vidas_texto = font.render(f'Vidas: {pelota.vidas}', True, BLANCO)
    instrucciones = font.render('Presione la teclas "ESPACE" para activar un burst de velocidad', True, BLANCO)
    screen.blit(instrucciones,(10, ALTO - 70))
    screen.blit(vidas_texto, (10, ALTO - 40))

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar FPS
    clock.tick(60)
