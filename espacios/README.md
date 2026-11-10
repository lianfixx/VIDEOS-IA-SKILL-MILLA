# Espacios

Cada marca tiene su carpeta y no se mezcla con las demás:

| Espacio | Carpeta | Producciones (privadas) |
|---|---|---|
| Personal de Emi | `espacios/personal/` | `productions/personal/` |
| MILLA ABOGADOS | `espacios/milla/` | `productions/milla/` |
| Castorena Abogados | `espacios/castorena/` | `productions/castorena/` |
| PAN / Acción Juvenil | `espacios/pan/` | `productions/pan/` |

En cada una: `perfil.json` (colores, voz, tono; lo lee `vox.py`), `ideas.md` (temas pendientes) y, cuando exista, `MARCA.md` con la guía de identidad y sus fuentes. `vox.py proyecto` se niega a crear una producción fuera de la carpeta de su espacio.
