# Blender en el proyecto (Avance 1)

Los objetos (arboles, farolas, baliza, rejilla del canal, tapa de alcantarilla y tragante) se
modelan en Blender con `crear_modelos_blender.py` y se exportan a `worlds/meshes/*.obj` (+ `.mtl`).
Webots los carga con nodos `Mesh { url [ "meshes/arbol_0.obj" ] }`.

## Generar los modelos y el .blend
1. Abre Blender (2.8 o superior).
2. Pestana **Scripting** > **Open** > `blender/crear_modelos_blender.py` > **Run Script**.
3. Resultado: `worlds/meshes/*.obj` y `blender/ciudad_alcantarillado.blend` (modelos en filas).
4. Vuelve a abrir el mundo en Webots.

## Ejes de exportacion
Forward = Y, Up = Z (igual que el mundo ENU de Webots). Origen en el suelo.
Para editar a mano: abre el .blend, modifica el objeto y exporta con File > Export > Wavefront (.obj)
con el mismo nombre de archivo en `worlds/meshes/`.
