# Monitoreo Inteligente del Alcantarillado - AVANCE 3: casas, hoteles y carros (Webots + Blender)

1. Abre Webots y carga `worlds/alcantarillado.wbt` (File > Open World).
2. Dale Play y haz clic una vez en la vista 3D (para que reciba el teclado).
3. Flecha ARRIBA = sube el agua. Flecha ABAJO = baja el agua. L = lluvia automatica.

Contenido de este avance:
- Avenida con cruce, aceras y terraplen. El canal corre DEBAJO de la avenida (bajo el separador
  central) cubierto por una rejilla de drenaje: se ve el robot y el agua desde arriba.
- Alcantarillado integrado en la carretera: tapas de alcantarilla y tragantes a ras del pavimento.
- Arboles y farolas a los lados de la via.
- Baliza de alerta junto a la rejilla (verde = NORMAL, ambar = PRECAUCION, roja = CRITICO).
- BLENDER: arboles, farolas, rejilla, tapas, tragantes y baliza son modelos 3D hechos con Blender
  (carpeta `blender/`) y cargados en Webots como nodos Mesh desde `worlds/meshes/`.

- Semaforos en las 4 esquinas del cruce con ciclo de 28 s (verde / ambar / rojo).

- 12 casas y 4 hoteles alrededor del cruce (modelos de Blender).
- 16 carros que circulan por los 4 carriles y respetan los semaforos.

Proximo avance: personas.
