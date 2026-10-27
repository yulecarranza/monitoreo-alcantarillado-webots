"""Controlador de la ciudad (Supervisor) - AVANCE 3: semaforos, carros y baliza de alerta.
No modifica el robot ni el canal; LEE la senal de radio que ya emite el robot (canal 1)
para mostrar el estado del alcantarillado en la baliza (verde / ambar / roja parpadeante)."""
from controller import Supervisor

robot = Supervisor()
TS = int(robot.getBasicTimeStep())
DT = TS / 1000.0

# ---------------- semaforos ----------------
CYCLE = 28.0   # s: ciclo completo de los dos ejes (A = avenida x, B = avenida y)

COLORS = {"R": ([1.0, 0.1, 0.1], [0.12, 0.0, 0.0]),
          "Y": ([1.0, 0.75, 0.0], [0.12, 0.09, 0.0]),
          "G": ([0.1, 1.0, 0.2], [0.0, 0.12, 0.03])}

mats = {(ax, k): robot.getFromDef(f"CIU_{ax}_{k}").getField("emissiveColor")
        for ax in "AB" for k in "RYG"}
last = {"A": None, "B": None}


def light_state(tm):
    """Devuelve (estado eje A, estado eje B) segun el instante del ciclo."""
    if tm < 10: return "G", "R"
    if tm < 12: return "Y", "R"
    if tm < 14: return "R", "R"
    if tm < 24: return "R", "G"
    if tm < 26: return "R", "Y"
    return "R", "R"


def paint(ax, state):
    if last[ax] == state:
        return
    last[ax] = state
    for k in "RYG":
        mats[(ax, k)].setSFColor(COLORS[k][0] if k == state else COLORS[k][1])


# ---------------- baliza del alcantarillado ----------------
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


# ---------------- carros ----------------
VMAX, ACC, DEC = 6.0, 3.0, 6.0
CAR_LEN, ROAD_L, STOP_U = 4.2, 90.0, -7.0
LANES = {"AE": ("A", lambda u: (u, -2.0)), "AW": ("A", lambda u: (-u, 2.0)),
         "BN": ("B", lambda u: (2.0, u)),  "BS": ("B", lambda u: (-2.0, -u))}

class Car:
    def __init__(self, idx, lane, u):
        self.node = robot.getFromDef(f"CIU_AUTO{idx}")
        self.pos = self.node.getField("translation")
        self.brake = robot.getFromDef(f"CIU_AUTO{idx}_FRENO").getField("emissiveColor")
        self.lane, self.u, self.v, self.braking = lane, u, VMAX, None

cars, idx = [], 0
for ln in ("AE", "AW", "BN", "BS"):
    for k in range(4):
        cars.append(Car(idx, ln, -ROAD_L / 2 + 22.5 * k + ("AE AW BN BS".split().index(ln)) * 5.0))
        idx += 1

def update_cars(states):
    for c in cars:
        axis, f = LANES[c.lane]
        st = states[axis]
        target = VMAX
        front = c.u + CAR_LEN / 2
        dist = STOP_U - front
        if dist > -0.3 and st != "G":
            can_stop = (c.v * c.v) / 8.0 <= (dist - 0.4)
            if st == "R" or can_stop:
                target = min(target, VMAX * max(0.0, min(1.0, (dist - 0.4) / 10.0)))
        gap = ROAD_L
        for o in cars:
            if o is not c and o.lane == c.lane:
                gap = min(gap, ((o.u - c.u) % ROAD_L) - CAR_LEN)
        target = min(target, VMAX * max(0.0, min(1.0, (gap - 1.5) / 6.0)))
        c.v += max(-DEC * DT, min(ACC * DT, target - c.v))
        c.u += c.v * DT
        if c.u > ROAD_L / 2: c.u -= ROAD_L
        x, y = f(c.u)
        c.pos.setSFVec3f([x, y, 0.04])
        br = target < c.v - 0.05 or c.v < 0.3
        if br != c.braking:
            c.braking = br
            c.brake.setSFColor([1.0, 0.05, 0.05] if br else [0.25, 0.0, 0.0])


estado_canal = "NORMAL"
while robot.step(TS) != -1:
    t = robot.getTime()
    sa, sb = light_state(t % CYCLE)
    paint("A", sa)
    paint("B", sb)
    update_cars({"A": sa, "B": sb})
    while rx.getQueueLength() > 0:
        try:
            estado_canal = leer_paquete().split(";")[0]
        except Exception:
            pass
        rx.nextPacket()
    pintar_baliza(estado_canal, t)
