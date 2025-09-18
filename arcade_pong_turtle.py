import turtle

# -------------------- CLASES --------------------

class Paddle(turtle.Turtle):
    def __init__(self, x, y, color):
        super().__init__()
        self.speed(0)
        self.shape("square")
        self.color(color)
        self.shapesize(stretch_wid=5, stretch_len=1)
        self.penup()
        self.goto(x, y)

    def mover_arriba(self):
        y = self.ycor()
        if y < 250:
            self.sety(y + 20)

    def mover_abajo(self):
        y = self.ycor()
        if y > -250:
            self.sety(y - 20)


class Ball(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.color("red")
        self.penup()
        self.speed(0)  # velocidad de dibujo de turtle
        self.velocidad = 0.1   # pasos iniciales (fluido)
        self.dx = self.velocidad
        self.dy = self.velocidad
        self.incremento_vel = 1.02  # 5% más rápida por rebote

    def mover(self):
        self.setx(self.xcor() + self.dx)
        self.sety(self.ycor() + self.dy)

    def rebotar_y(self):
         self.dy *= -1

    def rebotar_x(self):
        self.dx *= -1
        self.dx *= self.incremento_vel
        self.dy *= self.incremento_vel

    def reiniciar(self):
        self.goto(0, 0)
        # reinicia la velocidad a la inicial y cambia dirección
        self.dx = self.velocidad * (-1 if self.dx > 0 else 1)
        self.dy = self.velocidad


class Scoreboard(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.score_izq = 0
        self.score_der = 0
        self.color("white")
        self.penup()
        self.hideturtle()
        self.goto(0, 260)
        self.actualizar()

    def actualizar(self):
        self.clear()
        self.write(f"Jugador A: {self.score_izq}  Jugador B: {self.score_der}",
                   align="center", font=("Courier", 24, "normal"))

    def sumar_punto_izq(self):
        self.score_izq += 1
        self.actualizar()

    def sumar_punto_der(self):
        self.score_der += 1
        self.actualizar()

    def hay_ganador(self):
        if self.score_izq >= 5:
            return "Jugador A"
        elif self.score_der >= 5:
            return "Jugador B"
        return None


# -------------------- CLASE PRINCIPAL DEL JUEGO --------------------

class Game:
    def __init__(self):
        self.ventana = turtle.Screen()
        self.ventana.title("Pong en Python - POO")
        self.ventana.bgcolor("black")
        self.ventana.setup(width=800, height=600)
        self.ventana.tracer(0)

        # Objetos
        self.paleta_izq = Paddle(-350, 0, "green")
        self.paleta_der = Paddle(350, 0, "orange")
        self.pelota = Ball()
        self.marcador = Scoreboard()

        # Controles
        self.ventana.listen()
        self.ventana.onkeypress(self.paleta_izq.mover_arriba, "w")
        self.ventana.onkeypress(self.paleta_izq.mover_abajo, "s")
        self.ventana.onkeypress(self.paleta_der.mover_arriba, "Up")
        self.ventana.onkeypress(self.paleta_der.mover_abajo, "Down")

    def jugar(self):
        while True:
            self.ventana.update()
            self.pelota.mover()

            # Rebote arriba/abajo
            if self.pelota.ycor() > 290:
                self.pelota.sety(290)
                self.pelota.rebotar_y()

            if self.pelota.ycor() < -290:
                self.pelota.sety(-290)
                self.pelota.rebotar_y()

            # Punto para Jugador A
            if self.pelota.xcor() > 390:
                self.marcador.sumar_punto_izq()
                self.pelota.reiniciar()

            # Punto para Jugador B
            if self.pelota.xcor() < -390:
                self.marcador.sumar_punto_der()
                self.pelota.reiniciar()

            # Colisión con paleta derecha
            if (340 < self.pelota.xcor() < 350) and \
               (self.paleta_der.ycor() - 50 < self.pelota.ycor() < self.paleta_der.ycor() + 50):
                self.pelota.setx(340)
                self.pelota.rebotar_x()

            # Colisión con paleta izquierda
            if (-350 < self.pelota.xcor() < -340) and \
               (self.paleta_izq.ycor() - 50 < self.pelota.ycor() < self.paleta_izq.ycor() + 50):
                self.pelota.setx(-340)
                self.pelota.rebotar_x()

            # Revisar si hay ganador
            ganador = self.marcador.hay_ganador()
            if ganador:
                self.mostrar_ganador(ganador)
                break

    def mostrar_ganador(self, ganador):
        texto = turtle.Turtle()
        texto.color("yellow")
        texto.hideturtle()
        texto.write(f"🏆 {ganador} gana la partida 🏆",
                    align="center", font=("Courier", 28, "bold"))
        self.ventana.mainloop()


# -------------------- EJECUTAR JUEGO --------------------
if __name__ == "__main__":
    juego = Game()
    juego.jugar()