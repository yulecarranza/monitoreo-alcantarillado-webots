"""Controlador de la ciudad (Supervisor) - AVANCE 1: solo la baliza de alerta.
No modifica el robot ni el canal; LEE la senal de radio que ya emite el robot (canal 1)
para mostrar el estado del alcantarillado en la baliza (verde / ambar / roja parpadeante)."""
from controller import Supervisor

robot = Supervisor()
TS = int(robot.getBasicTimeStep())

COLORS = {"R": ([1.0, 0.1, 0.1], [0.12, 0.0, 0.0]),
          "Y": ([1.0, 0.75, 0.0], [0.12, 0.09, 0.0]),
          "G": ([0.1, 1.0, 0.2], [0.0, 0.12, 0.03])}

rx = robot.getDevice("receptor_ciudad")
rx.enable(TS)
bal = {c: robot.getFromDef(f"CIU_BAL_{c}").getField("emissiveColor") for c in "RYG"}
bal_estado = None


def leer_paquete():
    try:
        return rx.getString()
    except Exception:
        try:
            return bytes(rx.getBytes()).decode()
        except Exception:
            return rx.getData()


def pintar_baliza(estado, t):
    global bal_estado
    if estado == "CRITICO":
        parpadeo = int(t * 3) % 2 == 0
        clave = ("CRITICO", parpadeo)
        encendido = "R" if parpadeo else None
    else:
        clave = (estado, None)
        encendido = {"NORMAL": "G", "PRECAUCION": "Y"}.get(estado)
    if clave == bal_estado:
        return
    bal_estado = clave
    for c in "RYG":
        bal[c].setSFColor(COLORS[c][0] if c == encendido else COLORS[c][1])


estado_canal = "NORMAL"
while robot.step(TS) != -1:
    t = robot.getTime()
    while rx.getQueueLength() > 0:
        try:
            estado_canal = leer_paquete().split(";")[0]
        except Exception:
            pass
        rx.nextPacket()
    pintar_baliza(estado_canal, t)
