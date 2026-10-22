#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelado 3D del proyecto "Monitoreo Inteligente del Alcantarillado" (Webots + Blender)

Que hace este script
--------------------
1. En BLENDER: construye con bpy todos los modelos 3D de la ciudad (carros, peatones, edificios,
   arboles, farolas, semaforos, baliza de alerta, rejilla del canal, tapa de alcantarilla y
   tragante), les asigna materiales, los EXPORTA como .obj/.mtl a  ../worlds/meshes/  y guarda
   una escena de muestra  ciudad_alcantarillado.blend  en esta misma carpeta.
2. SIN Blender (python3 crear_modelos_blender.py): escribe los mismos .obj/.mtl con un escritor
   OBJ minimo, para poder abrir el mundo en Webots aunque no tengas Blender a la mano.

Como usarlo en Blender (2 minutos)
----------------------------------
  Opcion A:  Blender > pestana "Scripting" > Open > este archivo > boton "Run Script" (play).
  Opcion B:  blender --background --python crear_modelos_blender.py

Las medidas estan en metros, el eje Z va hacia arriba (igual que el mundo de Webots, ENU),
el origen de cada modelo esta en el suelo y los carros miran hacia +X.
"""
import os
import sys
import math
import random

try:
    import bpy
    EN_BLENDER = True
except ImportError:
    EN_BLENDER = False

# ----------------------------------------------------------------------------------------
# Materiales: nombre -> (r, g, b, emisivo)
# ----------------------------------------------------------------------------------------
MATERIALES = {
    "carro_rojo": (0.80, 0.10, 0.10, False), "carro_azul": (0.10, 0.30, 0.70, False),
    "carro_blanco": (0.90, 0.90, 0.90, False), "carro_negro": (0.15, 0.15, 0.15, False),
    "carro_amarillo": (0.90, 0.70, 0.10, False), "carro_verde": (0.20, 0.60, 0.30, False),
    "vidrio": (0.15, 0.25, 0.35, False), "llanta": (0.05, 0.05, 0.05, False),
    "parachoques": (0.12, 0.12, 0.13, False),
    "camisa_roja": (0.80, 0.20, 0.20, False), "camisa_azul": (0.20, 0.40, 0.80, False),
    "camisa_amarilla": (0.90, 0.70, 0.10, False), "camisa_verde": (0.30, 0.70, 0.40, False),
    "camisa_morada": (0.70, 0.30, 0.70, False), "pantalon": (0.15, 0.15, 0.30, False),
    "piel": (0.90, 0.70, 0.55, False), "pelo": (0.12, 0.08, 0.05, False),
    "ventana_on": (1.00, 0.85, 0.40, True), "ventana_off": (0.20, 0.30, 0.40, False),
    "techo": (0.30, 0.30, 0.32, False), "puerta": (0.35, 0.22, 0.12, False),
    "pared_0": (0.85, 0.75, 0.60, False), "pared_1": (0.70, 0.80, 0.85, False),
    "pared_2": (0.85, 0.60, 0.55, False), "pared_3": (0.75, 0.85, 0.70, False),
    "pared_4": (0.90, 0.85, 0.60, False), "pared_5": (0.65, 0.65, 0.80, False),
    "tronco": (0.40, 0.27, 0.15, False),
    "hojas_0": (0.20, 0.50, 0.20, False), "hojas_1": (0.25, 0.55, 0.25, False),
    "hojas_2": (0.30, 0.60, 0.20, False),
    "metal": (0.25, 0.25, 0.27, False), "metal_oscuro": (0.10, 0.10, 0.10, False),
    "luz_farola": (1.00, 0.90, 0.55, True),
    "amarillo_seguridad": (0.85, 0.70, 0.10, False),
    "rejilla": (0.22, 0.22, 0.24, False), "tapa": (0.28, 0.28, 0.30, False),
}

# ----------------------------------------------------------------------------------------
# Definicion de los modelos con primitivas:
#   ("box",  (cx, cy, cz), (sx, sy, sz), material)
#   ("ball", (cx, cy, cz), (rx, ry, rz), material)     # elipsoide (esfera escalada)
# ----------------------------------------------------------------------------------------
def B(c, s, m):
    return ("box", c, s, m)

def S(c, r, m):
    return ("ball", c, r, m)


def modelo_carro(color):
    p = [B((0, 0, 0.6), (4.2, 1.8, 0.6), color),
         B((-0.3, 0, 1.15), (2.3, 1.6, 0.5), "vidrio"),
         B((-0.3, 0, 1.43), (2.1, 1.5, 0.06), color),
         B((2.08, 0, 0.40), (0.12, 1.7, 0.2), "parachoques"),
         B((-2.08, 0, 0.40), (0.12, 1.7, 0.2), "parachoques")]
    for wx in (-1.3, 1.3):
        for wy in (-0.9, 0.9):
            p.append(S((wx, wy, 0.35), (0.35, 0.13, 0.35), "llanta"))
    return p


def modelo_peaton(camisa):
    return [B((0, 0.10, 0.40), (0.14, 0.14, 0.80), "pantalon"),
            B((0, -0.10, 0.40), (0.14, 0.14, 0.80), "pantalon"),
            B((0, 0, 1.10), (0.24, 0.40, 0.60), camisa),
            B((0, 0.26, 1.08), (0.10, 0.12, 0.55), camisa),
            B((0, -0.26, 1.08), (0.10, 0.12, 0.55), camisa),
            S((0, 0, 1.55), (0.15, 0.15, 0.15), "piel"),
            B((-0.03, 0, 1.64), (0.20, 0.22, 0.08), "pelo")]


# Disenos de edificios: (ancho_x, fondo_y, alto, pared)
DISENOS_EDIFICIO = [(6.5, 6.5, 12.0, 0), (7.0, 6.0, 18.0, 1), (5.8, 7.2, 9.0, 2),
                    (7.2, 7.0, 22.0, 3), (6.0, 6.0, 14.0, 4), (7.4, 5.8, 10.0, 5)]


def modelo_edificio(k):
    w, d, h, pared = DISENOS_EDIFICIO[k]
    rng = random.Random(100 + k)
    p = [B((0, 0, h / 2), (w, d, h), f"pared_{pared}"),
         B((0, 0, h + 0.15), (w + 0.3, d + 0.3, 0.3), "techo"),
         B((0, -(d / 2 + 0.03), 1.0), (1.4, 0.06, 2.0), "puerta"),
         B((0, -(d / 2 + 0.35), 2.15), (2.2, 0.8, 0.08), "techo")]       # marquesina de la entrada
    filas = []
    z = 2.9
    while z < h - 1.2:
        filas.append(z)
        z += 3.0
    for cara, largo in (("x", d), ("y", w)):
        n = max(1, int((largo - 1) / 2.2))
        for i in range(n):
            off = (i - (n - 1) / 2) * 2.2
            for z in filas:
                for sg in (-1, 1):
                    mat = "ventana_on" if rng.random() < 0.4 else "ventana_off"
                    if cara == "x":
                        p.append(B((sg * (w / 2 + 0.03), off, z), (0.06, 1.1, 1.4), mat))
                    else:
                        p.append(B((off, sg * (d / 2 + 0.03), z), (1.1, 0.06, 1.4), mat))
    return p


def modelo_arbol(k):
    return [B((0, 0, 1.0), (0.3, 0.3, 2.0), "tronco"),
            S((0, 0, 3.3), (1.4, 1.4, 1.4), f"hojas_{k}"),
            S((0.5, 0.3, 2.7), (0.9, 0.9, 0.9), f"hojas_{k}")]


def modelo_farola():            # el brazo apunta hacia -Y
    return [B((0, 0, 2.5), (0.12, 0.12, 5.0), "metal"),
            B((0, -0.5, 5.0), (0.12, 1.0, 0.10), "metal"),
            S((0, -1.0, 4.9), (0.22, 0.22, 0.22), "luz_farola"),
            B((0, 0, 0.1), (0.35, 0.35, 0.2), "metal")]


def modelo_semaforo():          # los lentes miran hacia +X
    p = [B((0, 0, 2.0), (0.15, 0.15, 4.0), "metal"),
         B((0, 0, 4.2), (0.30, 0.35, 1.2), "metal_oscuro")]
    for dz in (0.55, 0.0, -0.55):
        p.append(B((0.17, 0, 4.2 + dz + 0.16), (0.22, 0.30, 0.04), "metal_oscuro"))   # visera
    return p


def modelo_baliza():            # columna con 3 lentes (los lentes de colores los pone Webots)
    p = [B((0, 0, 1.9), (0.14, 0.14, 3.8), "metal"),
         B((0, 0, 0.1), (0.5, 0.5, 0.2), "metal")]
    for z in (3.45, 3.95, 4.45, 4.95):
        p.append(B((0, 0, z), (0.6, 0.6, 0.06), "metal_oscuro"))
    p.append(B((0, 0, 4.2), (0.12, 0.12, 1.5), "metal_oscuro"))
    return p


RejillaL, RejillaW = 15.75, 2.0


def modelo_rejilla_canal():     # rejilla que cubre el canal en el separador central de la avenida
    p = [B((0, 0.95, 0.01), (RejillaL, 0.10, 0.06), "amarillo_seguridad"),
         B((0, -0.95, 0.01), (RejillaL, 0.10, 0.06), "amarillo_seguridad"),
         B((RejillaL / 2 - 0.05, 0, 0.01), (0.10, RejillaW, 0.06), "amarillo_seguridad"),
         B((-RejillaL / 2 + 0.05, 0, 0.01), (0.10, RejillaW, 0.06), "amarillo_seguridad"),
         B((0, 0, 0.005), (RejillaL, 0.06, 0.05), "rejilla")]
    n = int((RejillaL - 0.3) / 0.42)
    for i in range(n + 1):
        x = -RejillaL / 2 + 0.2 + i * (RejillaL - 0.4) / n
        p.append(B((x, 0, 0.015), (0.10, 1.80, 0.05), "rejilla"))
    return p


def modelo_tapa():              # tapa de alcantarilla (disco con aro)
    return [S((0, 0, 0.02), (0.50, 0.50, 0.03), "tapa"),
            S((0, 0, 0.035), (0.38, 0.38, 0.02), "metal_oscuro")]


def modelo_tragante():          # sumidero de la calle
    p = [B((0, 0, 0.01), (1.0, 0.5, 0.04), "metal_oscuro")]
    for i in range(7):
        p.append(B((-0.42 + i * 0.14, 0, 0.03), (0.06, 0.42, 0.02), "rejilla"))
    return p


def construir_modelos():
    """AVANCE 1: solo carretera/alcantarillado, arboles y farolas.
    (carros, peatones, edificios y semaforos se agregan en avances posteriores)"""
    m = {}
    for k in range(3):
        m[f"arbol_{k}"] = modelo_arbol(k)
    m["farola"] = modelo_farola()
    m["baliza"] = modelo_baliza()
    m["rejilla_canal"] = modelo_rejilla_canal()
    m["tapa_alcantarilla"] = modelo_tapa()
    m["tragante"] = modelo_tragante()
    return m


# ----------------------------------------------------------------------------------------
# Salida sin Blender: escritor OBJ/MTL minimo (misma geometria)
# ----------------------------------------------------------------------------------------
CARAS_CAJA = [  # indices de esquinas (x,y,z) con signos, antihorario visto desde afuera
    ((+1, -1, -1), (+1, +1, -1), (+1, +1, +1), (+1, -1, +1), (1, 0, 0)),
    ((-1, +1, -1), (-1, -1, -1), (-1, -1, +1), (-1, +1, +1), (-1, 0, 0)),
    ((+1, +1, -1), (-1, +1, -1), (-1, +1, +1), (+1, +1, +1), (0, 1, 0)),
    ((-1, -1, -1), (+1, -1, -1), (+1, -1, +1), (-1, -1, +1), (0, -1, 0)),
    ((-1, -1, +1), (+1, -1, +1), (+1, +1, +1), (-1, +1, +1), (0, 0, 1)),
    ((-1, +1, -1), (+1, +1, -1), (+1, -1, -1), (-1, -1, -1), (0, 0, -1)),
]


def escribir_obj(nombre, prims, carpeta):
    v, vn, grupos = [], [], {}
    for tipo, c, s, mat in prims:
        caras = grupos.setdefault(mat, [])
        if tipo == "box":
            for a, b, cc, d, n in CARAS_CAJA:
                idx = []
                for sg in (a, b, cc, d):
                    v.append((c[0] + sg[0] * s[0] / 2, c[1] + sg[1] * s[1] / 2, c[2] + sg[2] * s[2] / 2))
                    idx.append(len(v))
                vn.append(n)
                caras.append([(i, len(vn)) for i in idx])
        else:
            anillos, seg = 8, 12
            def normal(x, y, z):
                nx, ny, nz = x / s[0], y / s[1], z / s[2]
                l = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
                return (nx / l, ny / l, nz / l)
            def vert(x, y, z):
                v.append((c[0] + x, c[1] + y, c[2] + z)); vn.append(normal(x, y, z))
                return (len(v), len(vn))
            top = vert(0, 0, s[2])
            rings = []
            for i in range(1, anillos):
                phi = math.pi * i / anillos
                rings.append([vert(s[0] * math.sin(phi) * math.cos(2 * math.pi * j / seg),
                                   s[1] * math.sin(phi) * math.sin(2 * math.pi * j / seg),
                                   s[2] * math.cos(phi)) for j in range(seg)])
            bot = vert(0, 0, -s[2])
            for j in range(seg):
                j2 = (j + 1) % seg
                caras.append([top, rings[0][j], rings[0][j2]])
                caras.append([bot, rings[-1][j2], rings[-1][j]])
                for i in range(len(rings) - 1):
                    A, Bq, C, Dq = rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]
                    caras.append([A, Dq, C, Bq])
    with open(os.path.join(carpeta, nombre + ".obj"), "w") as f:
        f.write(f"# {nombre} - modelo del proyecto Alcantarillado (generado sin Blender)\n")
        f.write(f"mtllib {nombre}.mtl\n")
        for x, y, z in v:
            f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for x, y, z in vn:
            f.write(f"vn {x:.4f} {y:.4f} {z:.4f}\n")
        for mat, caras in grupos.items():
            f.write(f"o {nombre}_{mat}\nusemtl {mat}\n")
            for cara in caras:
                f.write("f " + " ".join(f"{i}//{n}" for i, n in cara) + "\n")
    usados = sorted(grupos)
    with open(os.path.join(carpeta, nombre + ".mtl"), "w") as f:
        for mat in usados:
            r, g, b, em = MATERIALES[mat]
            f.write(f"newmtl {mat}\nKa 0 0 0\nKd {r} {g} {b}\nKs 0.05 0.05 0.05\n")
            f.write(f"Ke {r if em else 0} {g if em else 0} {b if em else 0}\nNs 10\nd 1\nillum 2\n\n")


# ----------------------------------------------------------------------------------------
# Salida con Blender (bpy)
# ----------------------------------------------------------------------------------------
def carpeta_del_script():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    if EN_BLENDER:
        try:
            ruta = bpy.context.space_data.text.filepath
            if ruta:
                return os.path.dirname(bpy.path.abspath(ruta))
        except Exception:
            pass
        if bpy.data.filepath:
            return os.path.dirname(bpy.data.filepath)
    return os.getcwd()


def exportar_blender(modelos, carpeta_blend, carpeta_obj):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    mats = {}
    for nombre, (r, g, b, em) in MATERIALES.items():
        m = bpy.data.materials.new(nombre)
        m.use_nodes = True
        m.diffuse_color = (r, g, b, 1.0)
        pb = m.node_tree.nodes.get("Principled BSDF")
        if pb is not None:
            pb.inputs["Base Color"].default_value = (r, g, b, 1.0)
            if em:
                for clave in ("Emission Color", "Emission"):
                    if clave in pb.inputs:
                        pb.inputs[clave].default_value = (r, g, b, 1.0)
                        break
                if "Emission Strength" in pb.inputs:
                    pb.inputs["Emission Strength"].default_value = 1.0
        mats[nombre] = m

    objetos = {}
    for nombre, prims in modelos.items():
        piezas = []
        for tipo, c, s, mat in prims:
            if tipo == "box":
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=c)
                o = bpy.context.active_object
                o.scale = s
            else:
                bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1.0, location=c)
                o = bpy.context.active_object
                o.scale = s
            o.data.materials.append(mats[mat])
            piezas.append(o)
        bpy.ops.object.select_all(action="DESELECT")
        for o in piezas:
            o.select_set(True)
        bpy.context.view_layer.objects.active = piezas[0]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.join()
        obj = bpy.context.active_object
        obj.name = nombre
        obj.data.name = nombre
        objetos[nombre] = obj

    os.makedirs(carpeta_obj, exist_ok=True)
    for nombre, obj in objetos.items():
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        ruta = os.path.join(carpeta_obj, nombre + ".obj")
        if hasattr(bpy.ops.wm, "obj_export"):                      # Blender 3.2 en adelante
            bpy.ops.wm.obj_export(filepath=ruta, export_selected_objects=True,
                                  forward_axis="Y", up_axis="Z", export_materials=True)
        else:                                                      # Blender 2.8 - 3.1
            bpy.ops.export_scene.obj(filepath=ruta, use_selection=True, axis_forward="Y",
                                     axis_up="Z", use_materials=True)
        print("[OK] exportado", ruta)

    # escena de muestra: todos los modelos en filas (despues de exportar)
    columnas, sep = 8, 12.0
    for i, (nombre, obj) in enumerate(objetos.items()):
        obj.location = ((i % columnas) * sep, -(i // columnas) * sep, 0.0)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(45, -30, -0.01))
    suelo = bpy.context.active_object
    suelo.name = "suelo_muestra"
    bpy.ops.object.light_add(type="SUN", location=(40, -20, 60))
    bpy.context.active_object.data.energy = 3.0
    bpy.context.active_object.rotation_euler = (0.8, 0.2, 0.6)
    os.makedirs(carpeta_blend, exist_ok=True)
    destino = os.path.join(carpeta_blend, "ciudad_alcantarillado.blend")
    bpy.ops.wm.save_as_mainfile(filepath=destino)
    print("[OK] escena guardada en", destino)


def main():
    base = carpeta_del_script()
    carpeta_obj = os.path.normpath(os.path.join(base, "..", "worlds", "meshes"))
    modelos = construir_modelos()
    if EN_BLENDER:
        exportar_blender(modelos, base, carpeta_obj)
    else:
        os.makedirs(carpeta_obj, exist_ok=True)
        for nombre, prims in modelos.items():
            escribir_obj(nombre, prims, carpeta_obj)
        print(f"[OK] {len(modelos)} modelos escritos en {carpeta_obj} (modo sin Blender)")


main()
