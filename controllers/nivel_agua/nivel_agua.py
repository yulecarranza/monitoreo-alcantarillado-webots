"""Supervisor: nivel del agua, lluvia, compuerta de alivio y pantalla de estado.

- Flecha ARRIBA / ABAJO: sube / baja el agua (haz clic antes en la vista 3D).
- Tecla L: activa o desactiva la lluvia automatica.
- Recibe del robot (Receiver) la senal con el estado del canal y la muestra en pantalla.
- Compuerta de alivio (HingeJoint): se abre sola cuando el estado es CRITICO y se
  cierra cuando el canal vuelve a NORMAL. Mientras esta abierta, el agua baja.
"""
from controller import Supervisor, Keyboard

NIVEL_INICIAL = 0.15    # m
NIVEL_MIN = 0.10        # m
NIVEL_MAX = 0.58        # m
VEL_NIVEL = 0.06        # m/s con las flechas
VEL_LLUVIA = 0.012      # m/s con la lluvia automatica
VEL_DRENAJE = 0.025     # m/s con la compuerta totalmente abierta
APERTURA_ABIERTA = 1.2  # rad (~69 grados)
ALTO_CAJA = 1.0         # m (alto de la caja de agua)
TECLA_L = ord("L")

COLORES = {"NORMAL": 0x00E050, "PRECAUCION": 0xFFA500, "CRITICO": 0xFF3030}

sup = Supervisor()
dt = int(sup.getBasicTimeStep())
campo = sup.getFromDef("AGUA").getField("translation")
campo_det = sup.getFromDef("AGUA_DET").getField("translation")

teclado = sup.getKeyboard()
teclado.enable(dt)

rx = sup.getDevice("receptor")
rx.enable(dt)

puerta_motor = sup.getDevice("compuerta_motor")
puerta_sensor = sup.getDevice("compuerta_sensor")
puerta_sensor.enable(dt)
puerta_motor.setVelocity(0.8)
puerta_motor.setPosition(0.0)


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
lluvia = False
l_antes = False
puerta_abierta = False

while sup.step(dt) != -1:
    # --- Teclado ---
    teclas = set()
    while True:
        tecla = teclado.getKey()
        if tecla == -1:
            break
        teclas.add(tecla)
    if Keyboard.UP in teclas:
        nivel += VEL_NIVEL * dt / 1000.0
    if Keyboard.DOWN in teclas:
        nivel -= VEL_NIVEL * dt / 1000.0
    l_ahora = TECLA_L in teclas
    if l_ahora and not l_antes:
        lluvia = not lluvia
        print(f"[LLUVIA] Lluvia automatica {'ACTIVADA' if lluvia else 'DESACTIVADA'}.")
    l_antes = l_ahora

    # --- Lluvia y drenaje por la compuerta ---
    if lluvia:
        nivel += VEL_LLUVIA * dt / 1000.0
    apertura = puerta_sensor.getValue()
    if apertura > 0.3:
        factor = min(1.0, apertura / APERTURA_ABIERTA)
        nivel -= VEL_DRENAJE * factor * dt / 1000.0
    nivel = max(NIVEL_MIN, min(NIVEL_MAX, nivel))

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

    # --- Compuerta: se abre con CRITICO y se cierra con NORMAL ---
    if senal is not None:
        if senal[0] == "CRITICO" and not puerta_abierta:
            puerta_abierta = True
            puerta_motor.setPosition(APERTURA_ABIERTA)
            print("[COMPUERTA] Nivel critico: abriendo compuerta de alivio.")
        elif senal[0] == "NORMAL" and puerta_abierta:
            puerta_abierta = False
            puerta_motor.setPosition(0.0)
            print("[COMPUERTA] Nivel normal: cerrando compuerta.")

    # --- Pantalla ---
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

    if puerta_abierta:
        txt_puerta = "ABIERTA" if apertura > 1.0 else "ABRIENDO..."
    else:
        txt_puerta = "CERRADA" if apertura < 0.1 else "CERRANDO..."
    sup.setLabel(4, f"Compuerta de alivio: {txt_puerta}   |   Lluvia automatica (L): {'ON' if lluvia else 'OFF'}",
                 0.02, 0.22, 0.05, 0xFFFFFF, 0.0, "Arial")
    sup.setLabel(3, "Flecha ARRIBA: sube el agua  |  Flecha ABAJO: baja el agua  |  L: lluvia automatica",
                 0.02, 0.94, 0.045, 0xFFFFFF, 0.3, "Arial")
