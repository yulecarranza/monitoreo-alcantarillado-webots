# Sistema Inteligente de Monitoreo de Alcantarillado

**Ciénaga, Magdalena — Proyecto de Robótica en Webots**

## 📌 Descripción

Este proyecto consiste en el desarrollo de un sistema robótico para el monitoreo de alcantarillados, utilizando simulación en Webots.

Un robot recorre una pasarela a lo largo del canal del alcantarillado y, con sensores de distancia, detecta situaciones de riesgo como **niveles elevados de agua** y **obstrucciones por acumulación de basura**. Cuando el nivel es crítico, el sistema emite una alerta temprana y abre automáticamente una compuerta de alivio para bajar el agua antes de que ocurra el desborde.

## 🌧️ Problemática

El alcantarillado de Ciénaga se desborda con las lluvias fuertes y también se rebosa por la acumulación de basura, incluso en días sin lluvia, provocando inundaciones frecuentes en la comunidad.

Este proyecto busca una solución de monitoreo que permita detectar estas situaciones de manera temprana.

## 🤖 Solución con robótica

- Un robot recorre el canal del alcantarillado de ida y vuelta.
- Sensores de distancia detectan el nivel del agua y las posibles obstrucciones.
- El sistema emite una alerta temprana antes de que ocurra el desborde.

### ¿Cómo funciona el sensor de distancia?

Es un dispositivo que mide qué tan cerca o lejos está un objeto del robot. Emite una señal (ultrasonido, infrarrojo o láser) que viaja hasta chocar con un objeto y regresa al sensor; con el tiempo que tarda en volver, calcula la distancia.

**Aplicación en nuestro proyecto:**

- **Nivel de agua:** detecta si el agua sube demasiado (riesgo de desborde).
- **Obstrucciones:** detecta basura acumulada que bloquea el paso del agua.

## 🎯 Objetivos

- Diseñar un entorno de alcantarillado en Webots.
- Diseñar un robot para realizar el monitoreo.
- Incorporar sensores de distancia.
- Detectar posibles niveles elevados de agua.
- Detectar posibles obstrucciones.
- Generar alertas cuando se detecten condiciones críticas.
- Realizar pruebas mediante simulación.

## ⚙️ Funcionamiento del sistema (Avance 3)

### Robot (`robot_monitor`)

- Cuatro ruedas motrices; recorre toda la pasarela de ida y vuelta y se mantiene centrado con un control proporcional-derivativo.
- Despliega un **brazo articulado (HingeJoint)** que lleva el sensor de distancia `ds_agua` hacia el agua.
- Sensor `ds_frente`: si algo bloquea la pasarela, el robot da la vuelta.
- GPS para conocer su posición en el canal.
- **Nivel de agua:** se calcula a partir de la distancia medida por `ds_agua`.
- **Obstrucciones:** una caída brusca en la lectura indica una pila de basura acumulada.
- **LED de alerta:** 🟢 verde (normal), 🟠 ámbar (precaución u obstrucción), 🔴 rojo (nivel crítico).
- Envía por radio (Emitter) el estado del canal al supervisor.

| Estado | Distancia del sensor al agua |
|---|---|
| NORMAL | mayor a 0.45 m |
| PRECAUCIÓN | entre 0.30 m y 0.45 m |
| CRÍTICO | menor a 0.30 m |

### Supervisor (`nivel_agua`)

- Simula el nivel del agua: se controla con el teclado o con lluvia automática.
- Recibe la señal del robot (Receiver) y muestra el estado en pantalla.
- **Compuerta de alivio (HingeJoint):** se abre sola cuando el estado es CRÍTICO y se cierra cuando el canal vuelve a NORMAL. Mientras está abierta, el agua baja.

### Controles de la simulación

| Tecla | Acción |
|---|---|
| ⬆️ Flecha arriba | Sube el agua |
| ⬇️ Flecha abajo | Baja el agua |
| `L` | Activa o desactiva la lluvia automática |

> Haz clic una vez en la vista 3D para que reciba el teclado.

## ▶️ Cómo ejecutarlo

1. Abre Webots y carga `worlds/alcantarillado.wbt` (*File > Open World*).
2. Dale **Play** y haz clic una vez en la vista 3D.
3. Sube el agua con la flecha arriba (o activa la lluvia con `L`) y observa cómo el robot cambia de estado y la compuerta se abre.

## 🛠️ Herramientas

- Webots
- Python (controladores del robot y del supervisor)
- GitHub
- Blender

## 📂 Estructura del proyecto

```text
monitoreo-alcantarillado-webots/
├── controllers/
│   ├── robot_monitor/
│   │   └── robot_monitor.py
│   └── nivel_agua/
│       └── nivel_agua.py
├── worlds/
│   ├── alcantarillado.wbt
│   
├── GUIA.md
└── README.md
```

## 📋 Estado del proyecto

### 🔎 Investigación

- [x] Investigación sobre sensores.
- [x] Investigación sobre monitoreo del nivel del agua.
- [x] Investigación sobre detección de obstrucciones.

### 🎨 Diseño del entorno

- [x] Modelado del alcantarillado (canal, paredes, pasarela y vigas).
- [x] Modelado del robot (chasis, cuatro ruedas y brazo articulado).
- [x] Modelado de obstáculos (pilas de basura en el canal y el fondo).
- [ ] Modelos en Blender (pendiente / opcional).

### 🤖 Webots

- [x] Creación del mundo inicial.
- [x] Integración del robot.
- [x] Integración de sensores (distancia frontal, distancia al agua, GPS).
- [x] Programación del sistema de monitoreo.
- [x] Alertas por consola, LED y pantalla.
- [x] Comunicación por radio robot ↔ supervisor.
- [x] Compuerta de alivio automática (Avance 3).
- [ ] Pruebas finales y ajustes de detalle.

## 🚀 Avances

| Avance | Contenido |
|---|---|
| 1 | Mundo inicial del alcantarillado. |
| 2 | Robot con brazo y sensor de distancia; detección de nivel de agua y obstrucciones; alertas con LED. |
| 3 | Comunicación por radio con el supervisor y compuerta de alivio que se abre sola en nivel crítico. |

## 👥 Equipo de trabajo

- YULEISI CARRANZA
- ANDRUS LOPEZ
- LUIS RIVERA

