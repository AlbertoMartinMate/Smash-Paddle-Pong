import pygame
import sys
import json
import os

# -------------------- CONSTANTES --------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
MAX_SCORE_DOBLE = 3
MAX_SCORE_EXPERTO = 5
RECORDS_FILE = "records.json"

# Sonidos (asegúrate de tener estos archivos o comenta estas líneas si no los usas)
SONIDO_REBOTE = "rebote.wav"
SONIDO_PUNTO = "punto.wav"
MUSICA_FONDO = "musica_fondo.mp3"

# -------------------- CLASES --------------------

class Paddle:
    """Paleta vertical u horizontal"""
    def __init__(self, x, y, width, height, color, speed=7):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = speed

    def mover_arriba(self):
        if self.rect.top > 0:
            self.rect.y -= self.speed

    def mover_abajo(self, screen_height):
        if self.rect.bottom < screen_height:
            self.rect.y += self.speed

    def mover_izquierda(self):
        if self.rect.left > 0:
            self.rect.x -= self.speed

    def mover_derecha(self, screen_width):
        if self.rect.right < screen_width:
            self.rect.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class Ball:
    """Pelota del juego"""
    def __init__(self, screen_width, screen_height):
        self.rect = pygame.Rect(screen_width//2-10, screen_height//2-10, 20, 20)
        self.color = (255,0,0)
        self.velocidad = 3
        self.dx = self.velocidad
        self.dy = self.velocidad
        self.incremento_vel = 1.03
        self.flash_frames = 0  # frames para efecto de flash

    def mover(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.flash_frames > 0:
            self.flash_frames -= 1

    def rebotar_y(self):
        self.dy *= -1
        self.flash_frames = 3  # activa efecto de flash

    def rebotar_x(self):
        self.dx *= -1
        self.dx *= self.incremento_vel
        self.dy *= self.incremento_vel
        self.flash_frames = 3

    def reiniciar(self, screen_width, screen_height):
        self.rect.center = (screen_width//2, screen_height//2)
        self.dx = self.velocidad * (-1 if self.dx>0 else 1)
        self.dy = self.velocidad

    def draw(self, screen):
        color = (255,255,0) if self.flash_frames > 0 else self.color
        pygame.draw.ellipse(screen, color, self.rect)


class Scoreboard:
    """Marcador clásico"""
    def __init__(self, font, max_score):
        self.score_izq = 0
        self.score_der = 0
        self.font = font
        self.max_score = max_score

    def sumar_punto_izq(self):
        self.score_izq += 1

    def sumar_punto_der(self):
        self.score_der += 1

    def hay_ganador(self):
        if self.score_izq >= self.max_score:
            return "Jugador A"
        elif self.score_der >= self.max_score:
            return "Jugador B"
        return None

    def draw(self, screen, screen_width):
        text = self.font.render(f"Jugador A: {self.score_izq}  Jugador B: {self.score_der}", True, (255,255,255))
        screen.blit(text, (screen_width//2 - text.get_width()//2, 20))


class IndividualScoreboard:
    """Marcador de golpeos para INDIVIDUAL"""
    def __init__(self, font):
        self.golpeos_izq = 0
        self.golpeos_der = 0
        self.font = font

    def sumar_golpeo_izq(self):
        self.golpeos_izq += 1

    def sumar_golpeo_der(self):
        self.golpeos_der += 1

    def draw(self, screen, screen_width):
        text = self.font.render(f"Golpeos Izq: {self.golpeos_izq}  Golpeos Der: {self.golpeos_der}", True, (255,255,255))
        screen.blit(text, (screen_width//2 - text.get_width()//2, 20))

    def guardar_record(self, game):
        record = max(self.golpeos_izq, self.golpeos_der)
        nombre = game.pedir_nombre()
        if os.path.exists(RECORDS_FILE):
            with open(RECORDS_FILE, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []  # archivo vacío o corrupto
        else:
            data = []
        data.append({"nombre": nombre, "golpeos": record})
        data = sorted(data, key=lambda x:x["golpeos"], reverse=True)[:5]
        with open(RECORDS_FILE, "w") as f:
            json.dump(data, f)
        print("Récord guardado!")


# -------------------- CLASE PRINCIPAL --------------------

class Game:
    """Clase principal con modos y efectos de sonido"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Smash Paddle Pong")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier", 24)
        self.modo = None
        self.salir = False  # bandera global para terminar el programa desde el menú

        # Objetos por modo
        self.paleta_izq = None
        self.paleta_der = None
        self.paleta_izq_hor = None
        self.paleta_der_hor = None
        self.pelota = None
        self.marcador = None
        self.individual_score = None

        # Cargar sonidos
        pygame.mixer.init()
        try:
            self.sonido_rebote = pygame.mixer.Sound(SONIDO_REBOTE)
            self.sonido_punto = pygame.mixer.Sound(SONIDO_PUNTO)
        except:
            self.sonido_rebote = None
            self.sonido_punto = None
        if os.path.exists(MUSICA_FONDO):
            pygame.mixer.music.load(MUSICA_FONDO)
            pygame.mixer.music.play(-1)

    def mostrar_menu(self):
        """Menú principal con selección de modo y acceso a récords"""
        font_big = pygame.font.SysFont("Courier", 30, bold=True)
        while True:
            self.screen.fill((0, 0, 0))
            textos = [
                "Introduce la modalidad de juego:",
                "1 - INDIVIDUAL",
                "2 - DOBLE",
                "3 - DOBLE EXPERTO",
                "4 - VER RECORDS",
                "5 - SALIR",
                "Presiona 1,2,3,4 o 5 para seleccionar"
            ]
            for i, t in enumerate(textos):
                text = font_big.render(t, True, (255, 255, 255))
                self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 80 + i * 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.salir = True
                    return  # volvemos a run()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.modo = "INDIVIDUAL"; return
                    if event.key == pygame.K_2:
                        self.modo = "DOBLE"; return
                    if event.key == pygame.K_3:
                        self.modo = "DOBLE EXPERTO"; return
                    if event.key == pygame.K_4:
                        self.mostrar_records()  # vuelve aquí al cerrar records
                    if event.key == pygame.K_5:
                        self.salir = True
                        return

    def pedir_nombre(self):
        """Pantalla para que el jugador escriba su nombre en Pygame (pulsa Enter para confirmar)"""
        nombre = ""
        escribiendo = True
        font = pygame.font.SysFont("Courier", 30)

        while escribiendo:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:      # Enter confirma
                        escribiendo = False
                    elif event.key == pygame.K_BACKSPACE: # Borrar último carácter
                        nombre = nombre[:-1]
                    else:
                        if len(nombre) < 12:             # límite opcional de caracteres
                            nombre += event.unicode

            # Dibujo en pantalla dentro del bucle para que el jugador vea lo que escribe
            self.screen.fill((0, 0, 0))
            prompt = font.render("Nuevo récord! Escribe tu nombre:", True, (255, 255, 255))
            display = font.render(nombre, True, (255, 255, 0))
            self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 40))
            self.screen.blit(display, (WIDTH//2 - display.get_width()//2, HEIGHT//2 + 10))
            pygame.display.flip()
            self.clock.tick(FPS)

        # si se pulsa Enter con nombre vacío, meter un valor por defecto
        if nombre.strip() == "":
            nombre = "Jugador"
        return nombre

    def mostrar_records(self):
        """Muestra los récords guardados en pantalla"""
        font_big = pygame.font.SysFont("Courier", 32, bold=True)
        font_small = pygame.font.SysFont("Courier", 24)

        # Cargar records del archivo
        if os.path.exists(RECORDS_FILE):
            with open(RECORDS_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        viendo = True
        while viendo:
            self.screen.fill((0, 0, 0))

            titulo = font_big.render("🏆 TOP 5 RECORDS INDIVIDUAL 🏆", True, (255, 255, 0))
            self.screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 100))

            if data:
                for i, record in enumerate(data):
                    linea = font_small.render(
                        f"{i+1}. {record['nombre']} - {record['golpeos']} golpes", True, (255, 255, 255)
                    )
                    self.screen.blit(linea, (WIDTH // 2 - linea.get_width() // 2, 180 + i * 40))
            else:
                vacio = font_small.render("No hay récords guardados todavía.", True, (200, 200, 200))
                self.screen.blit(vacio, (WIDTH // 2 - vacio.get_width() // 2, 200))

            salir = font_small.render("Pulsa cualquier tecla para volver al menú", True, (150, 150, 150))
            self.screen.blit(salir, (WIDTH // 2 - salir.get_width() // 2, HEIGHT - 100))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    viendo = False  # volver al menú

    def inicializar_modo(self):
        """Inicializa el modo seleccionado"""

        # Limpieza previa para evitar arrastres de objetos entre modos
        self.paleta_izq = None
        self.paleta_der = None
        self.paleta_izq_hor = None
        self.paleta_der_hor = None
        self.pelota = None
        self.marcador = None
        self.individual_score = None

        # Pelota común
        self.pelota = Ball(WIDTH, HEIGHT)

        if self.modo == "DOBLE":
            self.paleta_izq = Paddle(50, HEIGHT//2-50, 20, 100, (0,255,0))
            self.paleta_der = Paddle(WIDTH-70, HEIGHT//2-50, 20, 100, (255,165,0))
            self.marcador = Scoreboard(self.font, MAX_SCORE_DOBLE)

        elif self.modo == "DOBLE EXPERTO":
            # Verticales
            self.paleta_izq = Paddle(50, HEIGHT//2-50, 20, 100, (0,255,0))
            self.paleta_der = Paddle(WIDTH-70, HEIGHT//2-50, 20, 100, (255,165,0))
            # Horizontales
            self.paleta_izq_hor = Paddle(WIDTH//2-50, HEIGHT-40, 100, 20, (0,255,0))
            self.paleta_der_hor = Paddle(WIDTH//2-50, 20, 100, 20, (255,165,0))
            self.marcador = Scoreboard(self.font, MAX_SCORE_EXPERTO)

        elif self.modo == "INDIVIDUAL":
            self.paleta_izq = Paddle(50, HEIGHT//2-50, 20, 100, (0,255,0))
            self.paleta_der = Paddle(WIDTH-70, HEIGHT//2-50, 20, 100, (255,165,0))
            self.individual_score = IndividualScoreboard(self.font)


    def jugar(self):
        """Bucle principal del juego"""
        corriendo = True
        while corriendo:
            keys = pygame.key.get_pressed()

            # --- EVENTOS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    corriendo = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        # Subbucle de pausa
                        pausado = True
                        font = pygame.font.SysFont("Courier", 40, bold=True)
                        while pausado:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                elif e.type == pygame.KEYDOWN:
                                    if e.key == pygame.K_p:  # Reanudar
                                        pausado = False
                                    elif e.key == pygame.K_ESCAPE:  # Volver al menú
                                        return  # Sale de jugar() y vuelve al menú
                            # Mostrar mensaje de pausa
                            self.screen.fill((0,0,0))
                            text = font.render("PAUSA - P para continuar, ESC para menú", True, (255,255,0))
                            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
                            pygame.display.flip()
                            self.clock.tick(FPS)


            # Controles según modo
            if self.modo in ["DOBLE", "INDIVIDUAL"]:
                if keys[pygame.K_w]:
                    self.paleta_izq.mover_arriba()
                if keys[pygame.K_s]:
                    self.paleta_izq.mover_abajo(HEIGHT)
                if keys[pygame.K_UP]:
                    self.paleta_der.mover_arriba()
                if keys[pygame.K_DOWN]:
                    self.paleta_der.mover_abajo(HEIGHT)

            elif self.modo == "DOBLE EXPERTO":
                # Jugador A
                if keys[pygame.K_w]:
                    self.paleta_izq.mover_arriba()
                if keys[pygame.K_s]:
                    self.paleta_izq.mover_abajo(HEIGHT)
                if keys[pygame.K_a]:
                    self.paleta_izq_hor.mover_izquierda()
                if keys[pygame.K_d]:
                    self.paleta_izq_hor.mover_derecha(WIDTH)

                # Jugador B
                if keys[pygame.K_UP]:
                    self.paleta_der.mover_arriba()
                if keys[pygame.K_DOWN]:
                    self.paleta_der.mover_abajo(HEIGHT)
                if keys[pygame.K_LEFT]:
                    self.paleta_der_hor.mover_izquierda()
                if keys[pygame.K_RIGHT]:
                    self.paleta_der_hor.mover_derecha(WIDTH)

            # Movimiento de la pelota
            self.pelota.mover()

            if self.modo in ["DOBLE", "INDIVIDUAL"]:
                if self.pelota.rect.top <= 0 or self.pelota.rect.bottom >= HEIGHT:
                    self.pelota.rebotar_y()
                    if self.sonido_rebote: self.sonido_rebote.play()

            elif self.modo == "DOBLE EXPERTO":
                if self.pelota.rect.top <= 0:
                # Punto para Jugador A si la bola sale por arriba
                    self.marcador.sumar_punto_izq()
                    if self.sonido_punto: self.sonido_punto.play()
                    self.pelota.reiniciar(WIDTH, HEIGHT)

                if self.pelota.rect.bottom >= HEIGHT:
                    # Punto para Jugador B si la bola sale por abajo
                    self.marcador.sumar_punto_der()
                    if self.sonido_punto: self.sonido_punto.play()
                    self.pelota.reiniciar(WIDTH, HEIGHT)

            # Modos
            if self.modo == "DOBLE" or self.modo == "DOBLE EXPERTO":
                if self.pelota.rect.left >= WIDTH:
                    self.marcador.sumar_punto_izq()
                    if self.sonido_punto: self.sonido_punto.play()
                    self.pelota.reiniciar(WIDTH, HEIGHT)

                if self.pelota.rect.right <= 0:
                    self.marcador.sumar_punto_der()
                    if self.sonido_punto: self.sonido_punto.play()
                    self.pelota.reiniciar(WIDTH, HEIGHT)

            elif self.modo == "INDIVIDUAL":
                if self.pelota.rect.left <= 0 or self.pelota.rect.right >= WIDTH:
                    if self.individual_score:
                        self.individual_score.guardar_record(self)
                    pygame.time.wait(1000)  # espera opcional 1s para que se vea el mensaje
                    corriendo = False

            # Colisiones con paletas
            if self.pelota.rect.colliderect(self.paleta_der.rect):
                self.pelota.rebotar_x()
                self.pelota.rect.right = self.paleta_der.rect.left
                if self.sonido_rebote: self.sonido_rebote.play()
                if self.modo == "INDIVIDUAL": self.individual_score.sumar_golpeo_der()

            if self.pelota.rect.colliderect(self.paleta_izq.rect):
                self.pelota.rebotar_x()
                self.pelota.rect.left = self.paleta_izq.rect.right
                if self.sonido_rebote: self.sonido_rebote.play()
                if self.modo == "INDIVIDUAL": self.individual_score.sumar_golpeo_izq()

            if self.modo == "DOBLE EXPERTO":
                if self.pelota.rect.colliderect(self.paleta_izq_hor.rect):
                    self.pelota.rebotar_y()
                    self.pelota.rect.bottom = self.paleta_izq_hor.rect.top
                    if self.sonido_rebote: self.sonido_rebote.play()

                if self.pelota.rect.colliderect(self.paleta_der_hor.rect):
                    self.pelota.rebotar_y()
                    self.pelota.rect.top = self.paleta_der_hor.rect.bottom
                    if self.sonido_rebote: self.sonido_rebote.play()

            # Ganador
            if self.modo in ["DOBLE", "DOBLE EXPERTO"]:
                ganador = self.marcador.hay_ganador()
                if ganador:
                    self.mostrar_ganador(ganador)
                    pygame.time.wait(3000)
                    corriendo = False

            # Dibujar
            self.screen.fill((0,0,0))
            self.paleta_izq.draw(self.screen)
            self.paleta_der.draw(self.screen)
            if self.paleta_izq_hor: self.paleta_izq_hor.draw(self.screen)
            if self.paleta_der_hor: self.paleta_der_hor.draw(self.screen)
            self.pelota.draw(self.screen)

            if self.modo in ["DOBLE","DOBLE EXPERTO"] and self.marcador:
                self.marcador.draw(self.screen, WIDTH)
            elif self.modo == "INDIVIDUAL" and self.individual_score:
                self.individual_score.draw(self.screen, WIDTH)

            pygame.display.flip()
            self.clock.tick(FPS)

        
    def run(self):
        """Al terminar la partida, volver al menú"""
        while not self.salir:
            self.mostrar_menu()
            if self.salir:
                break
            self.inicializar_modo()
            self.jugar()
        pygame.quit()
        sys.exit()

    def mostrar_ganador(self, ganador):
        """Pantalla de ganador"""
        font_big = pygame.font.SysFont("Courier", 40, bold=True)
        text = font_big.render(f"🏆 {ganador} gana la partida 🏆", True, (255, 255, 0))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()


# -------------------- EJECUTAR --------------------
if __name__ == "__main__":
    juego = Game()
    juego.run()
