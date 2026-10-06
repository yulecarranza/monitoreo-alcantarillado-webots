"""Supervisor: controla el nivel del agua con el teclado y muestra la senal del robot.

- Flecha ARRIBA: sube el agua.  Flecha ABAJO: baja el agua.
  (haz clic primero en la vista 3D para que Webots reciba el teclado)
- Recibe del robot (Receiver) la senal con el estado del canal y la muestra en pantalla.
"""
from controller import Supervisor, Keyboard

NIVEL_INICIAL = 0.15   # m
NIVEL_MIN = 0.10       # m
NIVEL_MAX = 0.58       # m
VEL_NIVEL = 0.06       # m/s mientras se mantiene la flecha
ALTO_CAJA = 1.0        # m (alto de la caja de agua)

COLORES = {"NORMAL": 0x00E050, "PRECAUCION": 0xFFA500, "CRITICO": 0xFF3030}

sup = Supervisor()
dt = int(sup.getBasicTimeStep())
campo = sup.getFromDef("AGUA").getField("translation")
campo_det = sup.getFromDef("AGUA_DET").getField("translation")

teclado = sup.getKeyboard()
teclado.enable(dt)

rx = sup.getDevice("receptor")
rx.enable(dt)


def leer_paquete():
    try:
        return rx.getString()
    except Exception:
        try:
            return bytes(rx.getBytes()).decode()
        except Exception:
            return rx.getData()


nivel = NIVEL_INICIAL
senal = None

while sup.step(dt) != -1:
    # --- Teclado: flechas arriba / abajo ---
    while True:
        tecla = teclado.getKey()
        if tecla == -1:
            break
        if tecla == Keyboard.UP:
            nivel = min(NIVEL_MAX, nivel + VEL_NIVEL * dt / 1000.0)
        elif tecla == Keyboard.DOWN:
            nivel = max(NIVEL_MIN, nivel - VEL_NIVEL * dt / 1000.0)
    pos_agua = [0.0, 0.0, nivel - ALTO_CAJA / 2.0]
    campo.setSFVec3f(pos_agua)
    campo_det.setSFVec3f(pos_agua)

    # --- Senal del robot: estado;nivel_cm;pilas;x;obstruccion ---
    while rx.getQueueLength() > 0:
        try:
            estado, nivel_cm, pilas, x, obs = leer_paquete().split(";")
            senal = (estado, nivel_cm, pilas, x, obs == "1")
        except Exception:
            pass
        rx.nextPacket()

    sup.setLabel(0, f"Nivel real del agua: {nivel * 100:.0f} cm", 0.02, 0.02, 0.07, 0xFFFFFF, 0.0, "Arial")
    if senal is None:
        sup.setLabel(1, "Senal del robot: esperando...", 0.02, 0.09, 0.07, 0xAAAAAA, 0.0, "Arial")
    else:
        estado, nivel_cm, pilas, x, obs = senal
        sup.setLabel(1, f"Estado del canal: {estado}  (robot mide ~{nivel_cm} cm)", 0.02, 0.09, 0.07,
                     COLORES.get(estado, 0xFFFFFF), 0.0, "Arial")
        if obs:
            texto, color = f"OBSTRUCCION detectada en x = {x} m", 0xFFA500
        else:
            texto, color = f"Obstrucciones detectadas: {pilas}   |   robot en x = {x} m", 0xDDDDDD
        sup.setLabel(2, texto, 0.02, 0.16, 0.05, color, 0.0, "Arial")
    sup.setLabel(3, "Flecha ARRIBA: sube el agua  |  Flecha ABAJO: baja el agua", 0.02, 0.94, 0.045, 0xFFFFFF, 0.3, "Arial")
