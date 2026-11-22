# Free Build de Fortnite 43.10

Recursos del personaje humanoide en tercera persona, extraídos de la instalación local. El catálogo incluye 1.793 animaciones con pistas de huesos, además de las herramientas, las piezas de construcción, los sonidos y las miras.

## Dónde está cada cosa

| Carpeta | Contenido |
| --- | --- |
| `01_Movimiento` | Reposo, caminar, trote, carrera, sprint táctico, saltos, aterrizajes, agacharse, deslizarse, giros y obstáculos. Incluye los clips de `Motion_Matching` y las familias clásicas. |
| `02_Pico` | Sacar el pico, poses, golpes encadenados, salidas a reposo, variantes de agarre y mallas del punto débil. |
| `03_Construccion_y_edicion` | Animaciones del plano, mallas y texturas de casillas, y recursos de la mira. |
| `04_Modelos` | Esqueletos, pico predeterminado, papel del plano, lápiz y estructuras de madera, ladrillo y metal. |
| `05_Sonidos` | Golpes y movimientos del pico, confirmación de edición y sonidos de construcción. |
| `06_Referencias` | Catálogo con FPS, duración, pistas de huesos y ruta de cada animación. Incluye datos exportados de montajes y tablas de selección. |

## Montaje en Blender

1. Activa UEFormat o el complemento de Fortnite Porting en Blender. Importa el esqueleto `Fortnite_M_Avg_Player_Skeleton.uemodel` o un personaje con un rig compatible. Selecciona la armadura antes de importar el `.ueanim` con **Archivo → Importar → Unreal Animation**. Cuando cambies de personaje, comprueba que los huesos coinciden o retargetea la acción a su rig. [UEFormat](https://github.com/h4lfheart/UEFormat)
2. Para caminar, combina `NoWep_Walk_Start_N_Lfoot`, `NoWep_Walk_Loop_N` y `NoWep_Walk_Stop_N_Lfoot`. Usa los sufijos de dirección para escoger laterales o diagonales y las variantes `Lfoot` y `Rfoot` para emparejar el apoyo del pie. En el editor NLA, convierte cada acción en una tira con **Push Down** y ajusta la mezcla donde cambie el movimiento. En las carpetas `Run` y `TacSprint` están los ciclos equivalentes. [Tiras NLA de Blender](https://docs.blender.org/manual/en/latest/editors/nla/strips.html)
3. Comprueba si el hueso `root` desplaza el personaje. Si el clip ya lleva el desplazamiento, usa ese movimiento o transfiérelo a la trayectoria. Si el clip se reproduce en el sitio, anima la trayectoria por separado y ajusta la velocidad para que los pies no resbalen. Epic emplea Motion Matching para seleccionar poses según el movimiento en tiempo real. Los clips del paquete se pueden montar manualmente para vídeo. [Motion Matching en Unreal](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-matching-in-unreal-engine)
4. Para el salto, sincroniza despegue, caída y aterrizaje con la altura de la trayectoria. Para agacharse y levantarse, usa los clips `NoWep_Idle2Crouch` y `NoWep_Crouch2Idle` de `01_Movimiento/Transiciones`. Los que terminan en `_InMotion` son las variantes en movimiento. Estas cuatro transiciones aditivas se convirtieron usando el fotograma de referencia local según el comportamiento documentado por Unreal. [Tipos de pose base aditiva](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/EAdditiveBasePoseType)

## Pico y edición

| Acción | Clip o referencia | Cómo usarlo en el vídeo |
| --- | --- | --- |
| Sacar el pico | `Melee_WideGrip_Equip_CMM`, usado por `Melee_Equip` | Alinea el pico con la mano durante el gesto. El montaje dura unos 0,667 s y la definición del pico fija `TimeToEquip` en 0,331 s. Son dos valores distintos. |
| Andar con el pico | `M_Jog_Melee_Twohanded_N` o `Jog_N_Melee_TwoHanded_CMF` | Mantén la postura de agarre mientras avanzan las piernas. Usa las variantes direccionales para cambios de rumbo. |
| Golpear con el pico | `TwoHanded_Loop_Swing1_InMotion_120fps` y `TwoHanded_Loop_Swing2_InMotion_120fps` | El montaje alterna Swing1 y Swing2. Usa la salida `2Idle` que corresponde al último golpe y coloca el WAV de impacto en el contacto. |
| Quitar el pico | Transición al equipar la siguiente herramienta | El pico genérico tiene un montaje de equipamiento identificado. Para un corte al plano, cambia la visibilidad del pico y reproduce `Blueprint_Equip`. Las salidas `2Idle` terminan el golpe. |
| Sacar el plano | `Blueprint_Equip` | Construcción y edición comparten esta entrada de unos 0,533 s. Importa el papel y el lápiz como objetos aparte. |
| Mantener el plano | `M_BluePrint_Place` y `M_BluePrint_Edit` | Usa la pose que corresponda y conserva el ciclo de desplazamiento en las piernas. |
| Colocar o confirmar una edición | `BluePrint_Edit_ConfirmCheck` | Los montajes `Blueprint_Place` y `Blueprint_Edit` enlazan al mismo clip de unos 0,533 s. Cambia la pieza en el fotograma de confirmación que elijas para el plano del vídeo. |

Los archivos `.ueanim` llevan la animación esquelética. Las reglas de construcción, la selección del HUD y las mezclas que hace el juego se consultan como referencias en `06_Referencias`. Para la pared azul, usa los archivos de `03_Construccion_y_edicion/Casillas` y las miras del subdirectorio `HUD`.

## Repetir la extracción

Con Fortnite Porting abierto y listo, ejecuta esto desde la carpeta del proyecto.

```powershell
python extraer_free_build.py
```

El script lee `06_Referencias/Inventario_43.10.json`, comprueba la caché, solicita por MCP los recursos que falten y copia los archivos por categorías. Puedes ejecutar `python extraer_free_build.py --solo-organizar` si ya está todo en la caché, o usar `--destino` para crear la biblioteca en otra ubicación.
