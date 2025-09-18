import pygame
import sys

# -------------------- CLASES --------------------

class Paddle:
    """Clase para las paletas de los jugadores"""
    def __init__(self, x, y, color):
        # Rectángulo que representa la paleta (x, y, ancho, alto)
        self.rect = pygame.Rect(x, y, 20, 100)
        self.color = color
        self.speed = 7  # velocidad de movimiento

    def mover_arriba(self):
        """Mueve la paleta hacia arriba, sin salir de la pantalla"""
        if self.rect.top > 0:
            self.rect.y -= self.speed

    def mover_abajo(self, screen_height):
        """Mueve la paleta hacia abajo, sin salir de la pantalla"""
        if self.rect.bottom < screen_height:
            self.rect.y += self.speed

    def draw(self, screen):
        """Dibuja la paleta en la pantalla"""
        pygame.draw.rect(screen, self.color, self.rect)


class Ball:
    """Clase para la pelota del juego"""
    def __init__(self, screen_width, screen_height):
        # Posición inicial centrada y tamaño 20x20
        self.rect = pygame.Rect(screen_width // 2 - 10, screen_height // 2 - 10, 20, 20)
        self.color = (255, 0, 0)  # color rojo
        self.velocidad = 3         # velocidad inicial
        self.dx = self.velocidad   # movimiento horizontal
        self.dy = self.velocidad   # movimiento vertical
        self.incremento_vel = 1.02 # aumenta 2% al rebotar con paleta

    def mover(self):
        """Actualiza la posición de la pelota"""
        self.rect.x += self.dx
        self.rect.y += self.dy

    def rebotar_y(self):
        """Invierte dirección vertical al rebotar arriba/abajo"""
        self.dy *= -1

    def rebotar_x(self):
        """Invierte dirección horizontal y aumenta velocidad al rebotar con paleta"""
        self.dx *= -1
        self.dx *= self.incremento_vel
        self.dy *= self.incremento_vel

    def reiniciar(self, screen_width, screen_height):
        """Coloca la pelota en el centro después de un punto"""
        self.rect.center = (screen_width // 2, screen_height // 2)
        self.dx = self.velocidad * (-1 if self.dx > 0 else 1)
        self.dy = self.velocidad

    def draw(self, screen):
        """Dibuja la pelota como un círculo"""
        pygame.draw.ellipse(screen, self.color, self.rect)


class Scoreboard:
    """Clase para el marcador de puntos"""
    def __init__(self, font):
        self.score_izq = 0
        self.score_der = 0
        self.font = font

    def sumar_punto_izq(self):
        self.score_izq += 1

    def sumar_punto_der(self):
        self.score_der += 1

    def hay_ganador(self):
        """Revisa si hay ganador (3 puntos por defecto)"""
        if self.score_izq >= 3:
            return "Jugador A"
        elif self.score_der >= 3:
            return "Jugador B"
        return None

    def draw(self, screen, screen_width):
        """Dibuja el marcador en la parte superior, centrado"""
        text = self.font.render(f"Jugador A: {self.score_izq}  Jugador B: {self.score_der}", True, (255, 255, 255))
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, 20))


# -------------------- CLASE PRINCIPAL DEL JUEGO --------------------

class Game:
    """Clase principal que controla el juego"""
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Arcade Pong by AlbertoMtMt")
        self.clock = pygame.time.Clock()  # para controlar FPS

        # Crear paletas, pelota y marcador
        self.paleta_izq = Paddle(50, self.HEIGHT // 2 - 50, (0, 255, 0))     
        self.paleta_der = Paddle(self.WIDTH - 70, self.HEIGHT // 2 - 50, (255, 165, 0))
        self.pelota = Ball(self.WIDTH, self.HEIGHT)
        self.font = pygame.font.SysFont("Courier", 24)
        self.marcador = Scoreboard(self.font)

    def jugar(self):
        corriendo = True
        while corriendo:
            # -------------------- Eventos --------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    corriendo = False

            # -------------------- Controles --------------------
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.paleta_izq.mover_arriba()
            if keys[pygame.K_s]:
                self.paleta_izq.mover_abajo(self.HEIGHT)
            if keys[pygame.K_UP]:
                self.paleta_der.mover_arriba()
            if keys[pygame.K_DOWN]:
                self.paleta_der.mover_abajo(self.HEIGHT)

            # -------------------- Lógica de la pelota --------------------
            self.pelota.mover()

            # Rebote con paredes superior e inferior
            if self.pelota.rect.top <= 0 or self.pelota.rect.bottom >= self.HEIGHT:
                self.pelota.rebotar_y()

            # Punto para jugador A (si la pelota sale por la derecha)
            if self.pelota.rect.left >= self.WIDTH:
                self.marcador.sumar_punto_izq()
                self.pelota.reiniciar(self.WIDTH, self.HEIGHT)

            # Punto para jugador B (si la pelota sale por la izquierda)
            if self.pelota.rect.right <= 0:
                self.marcador.sumar_punto_der()
                self.pelota.reiniciar(self.WIDTH, self.HEIGHT)

            # Colisión con paletas
            if self.pelota.rect.colliderect(self.paleta_der.rect):
                self.pelota.rebotar_x()
                self.pelota.rect.right = self.paleta_der.rect.left  # evita que se quede dentro

            if self.pelota.rect.colliderect(self.paleta_izq.rect):
                self.pelota.rebotar_x()
                self.pelota.rect.left = self.paleta_izq.rect.right  # evita que se quede dentro

            # Revisar ganador
            ganador = self.marcador.hay_ganador()
            if ganador:
                self.mostrar_ganador(ganador)
                pygame.time.wait(3000)  # espera 3 segundos
                corriendo = False

            # -------------------- Dibujar todo --------------------
            self.screen.fill((0, 0, 0))                # limpiar pantalla
            self.paleta_izq.draw(self.screen)
            self.paleta_der.draw(self.screen)
            self.pelota.draw(self.screen)
            self.marcador.draw(self.screen, self.WIDTH)
            pygame.display.flip()                      # actualizar pantalla

            self.clock.tick(60)                        # limitar a 60 FPS

        pygame.quit()
        sys.exit()

    def mostrar_ganador(self, ganador):
        """Muestra el mensaje de victoria centrado"""
        font_big = pygame.font.SysFont("Courier", 40, bold=True)
        text = font_big.render(f"🏆 {ganador} gana la partida 🏆", True, (255, 255, 0))
        self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2))
        pygame.display.flip()


# -------------------- EJECUTAR JUEGO --------------------
if __name__ == "__main__":
    juego = Game()
    juego.jugar()