#!/usr/bin/env python3
"""Rinde con Blender (módulo `bpy`, sin interfaz) un objeto 3D con fondo transparente para usarlo como recorte.

Se ejecuta en un proceso aparte: `python3 blender_objeto.py ESPEC.json`. Lo llama `vox.py blender`.
ESPEC: {tipo, texto?, modelo?, colores{papel,tinta,acento,apoyo}, acabado, salida, giro, tam, muestras, fuente?}

Dos acabados, y ninguno usa el aspecto por defecto de Blender:
  plano  sombreado de caricatura en dos tonos con el color de la marca y contorno de tinta (Freestyle).
         Encaja con el papel y los recortes; es el que se usa casi siempre.
  real   materiales físicos con luz de estudio suave. Solo para espacios con imágenes tipo foto.
El color se rinde con transformación «Standard» para que los tonos de la marca salgan exactos.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

TIPOS = ["texto", "moneda", "caja", "modelo"]


def rgb(hexa: str, alfa: float = 1.0):
    h = hexa.lstrip("#")
    # sRGB -> lineal: Blender trabaja en lineal y así el color final coincide con el de la marca
    lin = lambda v: (v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (*[lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)], alfa)


def material(nombre: str, color: str, acabado: str, metal: float = 0.0):
    m = bpy.data.materials.new(nombre)
    if hasattr(m, 'use_nodes') and not m.node_tree:
        m.use_nodes = True
    nodos, enlaces = m.node_tree.nodes, m.node_tree.links
    nodos.clear()
    salida = nodos.new("ShaderNodeOutputMaterial")
    if acabado == "plano":
        base = nodos.new("ShaderNodeEmission")       # color exacto de la marca, sin depender de la luz
        base.inputs["Color"].default_value = rgb(color)
        sombra = nodos.new("ShaderNodeBsdfToon")     # una sola banda de sombra, como tinta diluida
        sombra.inputs["Color"].default_value = rgb(color)
        sombra.inputs["Size"].default_value = 0.55
        sombra.inputs["Smooth"].default_value = 0.02
        mezcla = nodos.new("ShaderNodeMixShader")
        mezcla.inputs[0].default_value = 0.42
        enlaces.new(base.outputs[0], mezcla.inputs[1])
        enlaces.new(sombra.outputs[0], mezcla.inputs[2])
        enlaces.new(mezcla.outputs[0], salida.inputs["Surface"])
    else:
        p = nodos.new("ShaderNodeBsdfPrincipled")
        p.inputs["Base Color"].default_value = rgb(color)
        p.inputs["Roughness"].default_value = 0.38
        p.inputs["Metallic"].default_value = metal
        enlaces.new(p.outputs[0], salida.inputs["Surface"])
    return m


def construir(e: dict) -> list:
    c, acabado = e["colores"], e["acabado"]
    objetos = []
    if e["tipo"] == "texto":
        curva = bpy.data.curves.new("texto", type="FONT")
        curva.body = str(e.get("texto") or "?")
        curva.align_x, curva.align_y = "CENTER", "CENTER"
        curva.extrude, curva.bevel_depth, curva.bevel_resolution = 0.16, 0.012, 2
        if e.get("fuente"):
            curva.font = bpy.data.fonts.load(e["fuente"])
        o = bpy.data.objects.new("texto", curva)
        bpy.context.collection.objects.link(o)
        o.rotation_euler = (math.radians(90), 0, 0)  # el texto nace acostado: se levanta para que mire a la cámara
        o.data.materials.append(material("frente", c["acento"], acabado))
        objetos.append(o)
    elif e["tipo"] == "moneda":
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=1.0, depth=0.16)
        o = bpy.context.object
        o.rotation_euler = (math.radians(90), 0, 0)
        bisel = o.modifiers.new("bisel", "BEVEL")
        bisel.width, bisel.segments = 0.03, 3
        o.data.materials.append(material("moneda", c["apoyo"], acabado, metal=1.0))
        bpy.ops.object.shade_auto_smooth()
        bpy.ops.mesh.primitive_torus_add(major_radius=0.72, minor_radius=0.035, major_segments=96)
        aro = bpy.context.object
        aro.rotation_euler = (math.radians(90), 0, 0)
        aro.location = (0, -0.08, 0)
        aro.data.materials.append(material("aro", c["tinta"], acabado))
        objetos += [o, aro]
    elif e["tipo"] == "caja":
        bpy.ops.mesh.primitive_cube_add(size=1.6)
        o = bpy.context.object
        bisel = o.modifiers.new("bisel", "BEVEL")
        bisel.width, bisel.segments = 0.04, 3
        o.data.materials.append(material("caja", c["acento"], acabado))
        objetos.append(o)
    elif e["tipo"] == "modelo":
        ruta = Path(e["modelo"])
        antes = set(bpy.data.objects)
        ext = ruta.suffix.lower()
        if ext in (".glb", ".gltf"):
            bpy.ops.import_scene.gltf(filepath=str(ruta))
        elif ext == ".obj":
            bpy.ops.wm.obj_import(filepath=str(ruta))
        elif ext == ".stl":
            bpy.ops.wm.stl_import(filepath=str(ruta))
        else:
            raise SystemExit(f"formato de modelo no admitido: {ext} (usa .glb, .gltf, .obj o .stl)")
        objetos = [o for o in bpy.data.objects if o not in antes and o.type == "MESH"]
        if not objetos:
            raise SystemExit("el modelo no trae ninguna malla")
        # En «real» se respetan los materiales del archivo; una malla que no trae ninguno (.stl, .obj sin .mtl)
        # recibe el color de la marca para no salir gris.
        m = material("modelo", c["acento"], acabado)
        for o in objetos:
            if acabado == "plano":
                o.data.materials.clear()
            if not any(o.data.materials):
                o.data.materials.clear()
                o.data.materials.append(m)
    return objetos


def encuadrar(objetos: list, giro: bool):
    """Centra el conjunto, lo cuelga de un eje para girarlo y coloca la cámara para que quepa completo."""
    bpy.context.view_layer.update()
    puntos = [o.matrix_world @ Vector(v) for o in objetos for v in o.bound_box]
    centro = sum(puntos, Vector()) / len(puntos)
    radio = max((p - centro).length for p in puntos) or 1.0
    eje = bpy.data.objects.new("eje", None)
    bpy.context.collection.objects.link(eje)
    # Se cuelga del eje la raíz de cada malla (un .glb casi siempre trae un nodo padre): así el conjunto
    # entero queda centrado y gira, tenga o no jerarquía.
    raices = []
    for o in objetos:
        r = o
        while r.parent is not None:
            r = r.parent
        if r not in raices:
            raices.append(r)
    for r in raices:
        m = r.matrix_world.copy()
        m.translation -= centro
        r.parent = eje
        r.matrix_world = m
    bpy.context.view_layer.update()
    cam_datos = bpy.data.cameras.new("camara")
    cam_datos.lens = 70
    cam = bpy.data.objects.new("camara", cam_datos)
    bpy.context.collection.objects.link(cam)
    dist = radio / math.tan(math.radians(0.5 * 2 * math.degrees(math.atan(18 / cam_datos.lens)))) * 1.12
    cam.location = (0, -dist, radio * 0.18)
    mira = bpy.data.objects.new("mira", None)
    bpy.context.collection.objects.link(mira)
    seguir = cam.constraints.new("TRACK_TO")
    seguir.target, seguir.track_axis, seguir.up_axis = mira, "TRACK_NEGATIVE_Z", "UP_Y"
    bpy.context.scene.camera = cam
    if not giro:
        eje.rotation_euler = (0, 0, math.radians(-24))  # tres cuartos: se lee el volumen
    return eje, radio, dist


def luces(radio: float, dist: float):
    for nombre, pos, fuerza, tam in (("principal", (-1.2, -1.0, 1.4), 520, 4.0), ("relleno", (1.5, -0.9, 0.3), 180, 6.0), ("contra", (0.2, 1.3, 1.1), 260, 3.0)):
        datos = bpy.data.lights.new(nombre, "AREA")
        datos.energy, datos.size = fuerza * radio * radio, tam * radio
        luz = bpy.data.objects.new(nombre, datos)
        luz.location = Vector(pos) * dist * 0.75
        bpy.context.collection.objects.link(luz)
        seguir = luz.constraints.new("TRACK_TO")
        seguir.target = bpy.data.objects["mira"]
        seguir.track_axis, seguir.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"


def main() -> None:
    e = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if e["tipo"] not in TIPOS:
        raise SystemExit(f"tipo desconocido: {e['tipo']}; opciones {TIPOS}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    escena = bpy.context.scene
    escena.render.engine = "CYCLES"
    escena.cycles.device = "CPU"
    escena.cycles.samples = int(e.get("muestras") or (24 if e["acabado"] == "plano" else 64))
    escena.cycles.use_denoising = e["acabado"] != "plano"
    escena.render.film_transparent = True
    escena.render.resolution_x = escena.render.resolution_y = int(e.get("tam") or 1024)
    escena.render.image_settings.file_format = "PNG"
    escena.render.image_settings.color_mode = "RGBA"
    escena.view_settings.view_transform = "Standard"
    escena.view_settings.look = "None"
    mundo = bpy.data.worlds.new("mundo")
    if not mundo.node_tree:
        mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35 if e["acabado"] == "real" else 0.0
    escena.world = mundo
    giro = int(e.get("giro") or 0)
    objetos = construir(e)
    eje, radio, dist = encuadrar(objetos, giro > 0)
    luces(radio, dist)
    if e["acabado"] == "plano":  # contorno de tinta, como los recortes del compositor
        escena.render.use_freestyle = True
        escena.render.line_thickness = max(1.6, escena.render.resolution_x / 300)
        capa = bpy.context.view_layer
        conjunto = capa.freestyle_settings.linesets.new("tinta") if not capa.freestyle_settings.linesets else capa.freestyle_settings.linesets[0]
        conjunto.select_silhouette = conjunto.select_border = conjunto.select_crease = True
        if conjunto.linestyle is None:  # con la escena vacía de fábrica el conjunto nace sin estilo de línea
            conjunto.linestyle = bpy.data.linestyles.new("tinta")
        conjunto.linestyle.color = rgb(e["colores"]["tinta"])[:3]
        conjunto.linestyle.thickness = escena.render.line_thickness
    salida = Path(e["salida"])
    if giro > 0:
        salida.mkdir(parents=True, exist_ok=True)
        # Sin fotogramas clave: el ángulo se fija a mano en cada cuadro, así el giro es constante de verdad.
        # El cuadro `giro` (360°) no se rinde: el bucle cierra sin repetir el primero.
        for n in range(giro):
            eje.rotation_euler = (0, 0, math.radians(360 * n / giro))
            bpy.context.view_layer.update()
            escena.render.filepath = str(salida / f"{n:04d}.png")
            bpy.ops.render.render(write_still=True)
    else:
        salida.parent.mkdir(parents=True, exist_ok=True)
        escena.render.filepath = str(salida)
        bpy.ops.render.render(write_still=True)
    esperados = [salida / f"{n:04d}.png" for n in range(giro)] if giro > 0 else [salida]
    faltan = [str(f) for f in esperados if not f.is_file()]
    if faltan:
        raise SystemExit(f"Blender no escribió {len(faltan)} archivo(s): {faltan[0]}")
    print(json.dumps({"ok": True, "blender": bpy.app.version_string, "cuadros": max(1, giro)}))


if __name__ == "__main__":
    main()
