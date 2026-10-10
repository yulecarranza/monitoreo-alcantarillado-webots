# Monitoreo Inteligente del Alcantarillado - Avance 3 (Webots)

1. Abre Webots y carga `worlds/alcantarillado.wbt` (File > Open World).
2. Dale Play y haz clic una vez en la vista 3D (para que reciba el teclado).
3. Flecha ARRIBA = sube el agua. Flecha ABAJO = baja el agua. L = lluvia automatica.

Que pasa en la simulacion:
- El robot despliega el brazo (HingeJoint) con el sensor de agua y recorre toda la pasarela de ida y vuelta.
- El sensor del brazo mide el agua y detecta las pilas de basura. El robot envia por radio el estado del canal.
- Avance 3: cuando el estado es CRITICO, la compuerta de alivio (otro HingeJoint, al fondo del canal)
  se abre sola y el agua baja. Cuando el canal vuelve a NORMAL, la compuerta se cierra.
- LED del robot: verde (normal), ambar (precaucion/obstruccion), rojo (nivel critico).
