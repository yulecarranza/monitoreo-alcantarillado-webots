# Monitoreo Inteligente del Alcantarillado — Avance 4: Carretera, alcantarillado y árboles

Simulación en **Webots** de un canal de alcantarillado que corre por debajo de una avenida, con un
robot de monitoreo que recorre el canal, detecta acumulaciones de basura y alerta el nivel del agua.
En este avance se incorpora el entorno urbano (carretera, alcantarillado integrado en la vía y
árboles), con los objetos 3D modelados en **Blender**.

## Qué se implementó en este avance

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
- Árboles, farolas, rejilla del canal, tapa de alcantarilla, tragante y baliza de alerta son modelos
  3D creados con Blender y cargados en Webots como nodos `Mesh` desde `worlds/meshes/`.
- Cada modelo se exporta en formato `.obj` + `.mtl` (colores/materiales).

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
  meshes/                   # modelos .obj + .mtl exportados desde Blender
controllers/
  nivel_agua/               # nivel del agua, lluvia, compuerta y pantalla
  robot_monitor/            # robot de monitoreo, brazo y sensor
  ciudad/                   # baliza de alerta
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
- Semáforos con ciclo de luces
- Personas (peatones)
- Casas y edificios
- Carros
