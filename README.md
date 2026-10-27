# Monitoreo Inteligente del Alcantarillado — Avance 3: Casas, hoteles y carros

Simulación en **Webots** de un canal de alcantarillado que corre por debajo de una avenida, con un
robot de monitoreo que recorre el canal, detecta acumulaciones de basura y alerta el nivel del agua.
Sobre el entorno urbano de los avances anteriores (carretera, alcantarillado integrado en la vía,
árboles y semáforos) se agregan en este avance **casas, hoteles y carros**, con los objetos 3D
modelados en **Blender**.

## Qué se implementó en este avance

### Casas (nuevo)
- **12 casas** en cuatro diseños (colores de pared y de teja distintos), repartidas en las cuatro
  manzanas alrededor del cruce.
- Cada casa tiene techo a dos aguas, chimenea, puerta con escalón y ventanas; todas están orientadas
  con la puerta hacia la calle.

### Hoteles (nuevo)
- **4 hoteles** de gran altura (21 a 30 m) en las esquinas del cruce, en tres diseños.
- Vestíbulo de vidrio con puerta principal y marquesina con columnas, ventanas en todos los pisos
  (algunas encendidas), cuarto de máquinas y antena en la azotea.
- Letrero **HOTEL** en la fachada, formado con bloques luminosos.

### Carros (nuevo)
- **16 carros** en seis colores, modelados en Blender, que circulan por los cuatro carriles de las
  dos avenidas.
- Los carros **respetan los semáforos**: frenan de forma gradual ante el rojo, esperan en la línea
  de pare, mantienen distancia con el carro de adelante y encienden las luces de freno.

## Base de los avances anteriores
- **Semáforos** en las cuatro esquinas del cruce con ciclo de 28 s coordinado entre las dos avenidas
  (verde / ámbar / rojo, con tiempo de despeje).

### 1. Carretera
- Avenida principal con un cruce, carriles, líneas centrales, líneas de pare y cebras peatonales.
- Aceras sobre un terraplén; la calzada queda a un nivel inferior al de las aceras.

### 2. Alcantarillado integrado en la carretera
- El canal corre **debajo de la avenida**, bajo el separador central, y queda cubierto por una
  **rejilla de drenaje** a ras del pavimento (desde arriba se ven el robot y el agua).
- **Tapas de alcantarilla** y **tragantes (sumideros)** colocados dentro de la calzada, a ras del
  asfalto, a lo largo de la avenida y en el cruce.

### 3. Árboles y alumbrado
- Árboles de tres variantes distribuidos a ambos lados de las vías.
- Farolas a lo largo de las calles.

### 4. Integración con Blender
- Carros, casas, hoteles, árboles, farolas, semáforos, rejilla del canal, tapa de alcantarilla, tragante y baliza de alerta son modelos
  3D creados con Blender y cargados en Webots como nodos `Mesh` desde `worlds/meshes/`.
- Cada modelo se exporta desde Blender y se divide por material (`modelo__material.obj`); el color
  de cada parte se asigna en el mundo con un `PBRAppearance`, para que se vea igual en cualquier
  versión de Webots.

### 5. Sistema de monitoreo (base del proyecto)
- **Robot de monitoreo** que recorre la pasarela del canal de ida y vuelta.
- **Brazo articulado** con sensor de distancia que mide la distancia hasta el agua; una caída
  brusca de la lectura indica una **obstrucción** (acumulación de basura).
- **Alerta temprana** en tres niveles — NORMAL (verde), PRECAUCIÓN (ámbar) y CRÍTICO (rojo) — con
  LED en el robot y señal por radio.
- **Baliza de alerta** junto a la rejilla que refleja el estado del canal.
- **Compuerta de alivio** que se abre automáticamente en estado CRÍTICO y se cierra al normalizarse.
- **Lluvia automática** y **pantalla de estado** (nivel real del agua, estado del canal,
  obstrucciones detectadas, posición del robot, estado de la compuerta).

## Cómo ejecutar
1. Extrae el proyecto completo en una carpeta (no abrirlo desde dentro del `.zip`).
2. Abre Webots y carga `worlds/alcantarillado.wbt` (*File > Open World*).
3. Pulsa **Play** y haz clic una vez en la vista 3D para que reciba el teclado.

### Controles
| Tecla | Acción |
|---|---|
| Flecha ARRIBA | Sube el nivel del agua |
| Flecha ABAJO | Baja el nivel del agua |
| L | Activa / desactiva la lluvia automática |

**Sugerencia para la demostración:** sube el agua con la flecha ARRIBA hasta llegar a CRÍTICO y
observa a la vez la baliza, la compuerta (a través de la rejilla) y la pantalla de estado.

## Estructura del proyecto
```
worlds/
  alcantarillado.wbt        # mundo de Webots
  meshes/                   # partes de los modelos de Blender (una por material)
controllers/
  nivel_agua/               # nivel del agua, lluvia, compuerta y pantalla
  robot_monitor/            # robot de monitoreo, brazo y sensor
  ciudad/                   # semáforos, carros y baliza de alerta
blender/
  crear_modelos_blender.py  # script que genera los modelos y el archivo .blend
  LEEME_BLENDER.md          # instrucciones de Blender
```

## Uso de Blender
1. Abre Blender (2.8 o superior).
2. En la pestaña **Scripting**, abre `blender/crear_modelos_blender.py` y pulsa **Run Script**.
3. Se generan los `.obj`/`.mtl` en `worlds/meshes/` y el archivo `blender/ciudad_alcantarillado.blend`.
4. Vuelve a abrir el mundo en Webots.

Ejes de exportación: *Forward = Y*, *Up = Z* (equivalente al sistema ENU de Webots).

## Próximos avances
- Personas (peatones)
