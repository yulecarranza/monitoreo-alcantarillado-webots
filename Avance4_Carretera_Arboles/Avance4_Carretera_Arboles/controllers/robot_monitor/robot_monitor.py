"""Robot de monitoreo del alcantarillado (Avance 2).

- Despliega el brazo (HingeJoint) que lleva el sensor de distancia hacia el agua.
- Recorre TODA la pasarela de un extremo a otro, de ida y vuelta, sin parar.
- ds_agua (punta del brazo): mide la distancia hasta el agua. Si la lectura baja
  de golpe, hay una acumulacion de basura en el canal (obstruccion).
- Emite alerta temprana (consola + LED + senal por radio al supervisor): verde / ambar / rojo.
"""
from controller import Robot

VELOCIDAD = 6.0              # rad/s (radio 0.08 m -> ~0.48 m/s)
X_LIMITE = 5.4               # m: el robot da la vuelta al llegar aqui
SALTO_OBSTRUCCION = 0.03     # m: caida brusca de la lectura = basura acumulada
DIST_AGUA_PRECAUCION = 0.45  # m: el agua se acerca al sensor
DIST_AGUA_CRITICO = 0.30     # m: riesgo de desborde
ALTURA_SENSOR = 0.78         # m: altura del sensor sobre el fondo del canal
DIST_FRENTE_SEGURIDAD = 0.30 # m: algo bloquea la pasarela adelante
KP = 20.0                    # correccion para mantenerse en el centro de la pasarela
KD = 20.0
W_MAX = 2.5                  # rad/s: maxima diferencia entre ruedas

robot = Robot()
dt = int(robot.getBasicTimeStep())

ruedas = [robot.getDevice(n) for n in (
    "rueda_del_izq", "rueda_tra_izq", "rueda_del_der", "rueda_tra_der")]
for r in ruedas:
    r.setPosition(float("inf"))
    r.setVelocity(0.0)

brazo = robot.getDevice("brazo_motor")
brazo_pos = robot.getDevice("brazo_sensor")
brazo_pos.enable(dt)

ds_frente = robot.getDevice("ds_frente")
ds_agua = robot.getDevice("ds_agua")
gps = robot.getDevice("gps")
for d in (ds_frente, ds_agua, gps):
    d.enable(dt)

emisor = robot.getDevice("emisor")


def enviar(texto):
    """Envia la senal del estado del canal al supervisor."""
    try:
        emisor.send(texto.encode())
    except Exception:
        emisor.send(texto)

led = robot.getDevice("led_alerta")
led.set(1)  # 1 = verde, 2 = ambar, 3 = rojo

brazo.setVelocity(1.0)
brazo.setPosition(1.5708)  # despliega el brazo (HingeJoint) hacia el agua
print("[ROBOT] Desplegando brazo del sensor de agua...")


def mover(v, w=0.0):
    """v: velocidad base. w>0 gira a la izquierda (ruedas izq. mas lentas)."""
    ruedas[0].setVelocity(v - w)
    ruedas[1].setVelocity(v - w)
    ruedas[2].setVelocity(v + w)
    ruedas[3].setVelocity(v + w)


desplegado = False
t_listo = 0.0
direccion = 1            # +1 hacia adelante, -1 hacia atras
base_agua = None         # distancia al agua sin contar la basura
en_pila = False
pilas = 0
estado_agua = "NORMAL"
bloqueo = 0
ultimo_reporte = 0.0
recorridos = 0
paso = 0
y_prev = None
vy_f = 0.0

while robot.step(dt) != -1:
    t = robot.getTime()

    if not desplegado:
        pos = brazo_pos.getValue()
        if abs(pos - 1.5708) < 0.05 or t > 6.0:
            desplegado = True
            t_listo = t
            print(f"[ROBOT] Brazo desplegado (posicion {pos:.2f} rad). Iniciando recorrido de la pasarela.")
        continue

    pos_gps = gps.getValues()
    x, y = pos_gps[0], pos_gps[1]
    if y_prev is not None:
        vy_f = 0.8 * vy_f + 0.2 * (y - y_prev) / (dt / 1000.0)
    y_prev = y
    d_agua = ds_agua.getValue()
    d_frente = ds_frente.getValue()

    # --- Recorrido de ida y vuelta por toda la pasarela ---
    if direccion == 1 and x > X_LIMITE:
        direccion = -1
        recorridos += 1
        print(f"[ROBOT t={t:.0f}s] Fin de la pasarela (x={x:.1f}). Regresando. Recorridos: {recorridos}")
    elif direccion == -1 and x < -X_LIMITE:
        direccion = 1
        recorridos += 1
        print(f"[ROBOT t={t:.0f}s] Inicio de la pasarela (x={x:.1f}). Avanzando. Recorridos: {recorridos}")

    # Seguridad: si algo bloquea la pasarela, da la vuelta (lectura sostenida)
    if direccion == 1 and t - t_listo > 2.0 and d_frente < DIST_FRENTE_SEGURIDAD:
        bloqueo += 1
        if bloqueo >= 5:
            direccion = -1
            bloqueo = 0
            print(f"[ALERTA t={t:.0f}s] Pasarela bloqueada a {d_frente:.2f} m (x={x:.1f}). Regresando.")
    else:
        bloqueo = 0

    # Mantiene el robot en el centro de la pasarela (y = 0)
    w = -direccion * (KP * y + KD * vy_f)
    w = max(-W_MAX, min(W_MAX, w))
    mover(VELOCIDAD * direccion, w)

    # --- Nivel del agua y acumulaciones de basura (sensor del brazo) ---
    if base_agua is None:
        base_agua = d_agua
    if d_agua < base_agua - SALTO_OBSTRUCCION:
        if not en_pila:
            en_pila = True
            pilas += 1
            print(f"[ALERTA t={t:.0f}s] OBSTRUCCION: acumulacion de basura en el canal (x={x:.1f} m).")
    else:
        en_pila = False
        base_agua = d_agua

    if base_agua < DIST_AGUA_CRITICO:
        nuevo = "CRITICO"
    elif base_agua < DIST_AGUA_PRECAUCION:
        nuevo = "PRECAUCION"
    else:
        nuevo = "NORMAL"

    if nuevo != estado_agua:
        estado_agua = nuevo
        nivel_cm = (ALTURA_SENSOR - base_agua) * 100
        if nuevo == "CRITICO":
            print(f"[ALERTA t={t:.0f}s] NIVEL CRITICO: agua a ~{nivel_cm:.0f} cm. RIESGO DE DESBORDE.")
        elif nuevo == "PRECAUCION":
            print(f"[AVISO t={t:.0f}s] Precaucion: el agua esta subiendo (~{nivel_cm:.0f} cm).")
        else:
            print(f"[OK t={t:.0f}s] Nivel de agua normal.")

    # --- LED de alerta ---
    severidad = 1
    if estado_agua == "PRECAUCION" or en_pila:
        severidad = 2
    if estado_agua == "CRITICO":
        severidad = 3
    led.set(severidad)

    # --- Senal de estado al supervisor (varias veces por segundo) ---
    paso += 1
    if paso % 8 == 0:
        nivel_cm = (ALTURA_SENSOR - base_agua) * 100
        enviar(f"{estado_agua};{nivel_cm:.0f};{pilas};{x:.1f};{1 if en_pila else 0}")

    # --- Reporte periodico ---
    if t - ultimo_reporte >= 5.0:
        ultimo_reporte = t
        nivel_cm = (ALTURA_SENSOR - base_agua) * 100
        sentido = "->" if direccion == 1 else "<-"
        print(f"[ESTADO t={t:.0f}s] x={x:+.1f} y={y:+.2f} {sentido} | ds_agua={d_agua:.2f} m | agua ~{nivel_cm:.0f} cm ({estado_agua}) | pilas: {pilas}")
