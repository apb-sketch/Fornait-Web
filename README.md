# Catálogo de recursos

Abre `Abrir catálogo.cmd` con doble clic en Windows. La aplicación usa Python 3.10 o posterior con Tkinter y no requiere paquetes adicionales.

1. Añade una **carpeta** para buscar también en sus subcarpetas o añade uno o varios **ZIP** de recursos que puedas utilizar.
2. Escribe palabras del nombre o de la ruta. Por ejemplo, `rejilla azul`, `skin scout` o `emote saludo`. Puedes filtrar por tipo y previsualizar PNG y GIF.
3. Selecciona archivos con Ctrl o Mayús y pulsa **Exportar selección…**. Cada exportación crea una carpeta nueva y conserva las rutas relativas agrupadas por fuente.

La detección por extensión y nombre incluye modelos, animaciones, audio, texturas, materiales y archivos de código. Los `.uasset` sueltos se copian como archivos de Unreal, con el tipo estimado a partir de su prefijo. El catálogo lee carpetas y ZIP sin cifrar. [Convención de nombres de Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/recommended-asset-naming-conventions-in-unreal-engine-projects).

## Rejilla de edición

`recursos/Rejilla_de_edicion_azul.png` es una textura original de 1024 × 1024 px con canal alfa. En la pestaña **Rejilla de edición**, arrastra por las dos casillas inferiores de la columna central y pulsa **Aplicar edición** para ver una abertura. Pulsa una casilla vacía y aplica otra vez para recuperarla.

En un motor 3D, puedes proyectar la textura sobre un plano alineado a la pared. Usa el punto de impacto en las coordenadas locales del plano para identificar una de las nueve casillas. Guarda la selección pendiente por separado y actualiza la geometría y la colisión de la pared al confirmar.

Para sacar otra variante de color, ajusta `FILL_TOP`, `FILL_BOTTOM`, `LINE` y `ACCENT` en `generar_rejilla.py` y ejecuta `python generar_rejilla.py`. El generador usa Pillow y actualiza el PNG de ejemplo.

## Fuentes para el proyecto

- Texturas y modelos CC0. [Poly Haven](https://polyhaven.com/license).
- Personajes y animaciones CC0. [Kenney Animated Characters](https://kenney.nl/assets/animated-characters-protagonists).
- Sonido y música. Comprueba la licencia que figura en la ficha de cada archivo. [Freesound](https://freesound.org/help/faq/).
- Si el proyecto es una isla de Fortnite, UEFN ofrece materiales oficiales en el explorador de contenido. [Biblioteca de materiales de UEFN](https://dev.epicgames.com/documentation/fortnite/material-library-in-unreal-editor-for-fortnite).
