# Sensibilidad de ratón de Fortnite para un videojuego propio

Para reproducir el giro de cámara sin apuntar con la mira en Fortnite para PC, usa **`0.005555` grados por cuenta del ratón por cada punto porcentual de sensibilidad**. Una cuenta es una unidad de desplazamiento que reporta el ratón. El valor procede de la escala *Fortnite Percent* publicada por KovaaK’s en mayo de 2020. Su conversor web seguía usando `Sens * 0.005555` al revisar su código público en noviembre de 2026. Es una referencia de terceros para reproducir el giro. [Notas de KovaaK’s](https://steamcommunity.com/games/824270/announcements/detail/2201641989738342680) · [Conversor de KovaaK’s](https://www.kovaaks.com/kovaaks/sens-converter/fortnite)

## Deslizadores y fórmula

Usa dos deslizadores lineales, **Sensibilidad X (%)** para el giro horizontal y **Sensibilidad Y (%)** para la inclinación vertical. Un paso de **0,1 puntos porcentuales** permite introducir valores como `6,2 %`. Epic documenta ambos ajustes como porcentajes y un desarrollador de KovaaK’s confirma que la escala permite usar valores distintos en cada eje. [Guía de Epic Games](https://store.epicgames.com/news/fortnite-on-pc-best-settings-for-competitive-play-in-2026) · [Explicación del desarrollador de KovaaK’s](https://steamcommunity.com/app/824270/discussions/0/2248929785830436504/)

```text
giroHorizontalGrados = deltaX * sensibilidadXPorcentaje * 0.005555
giroVerticalGrados   = deltaY * sensibilidadYPorcentaje * 0.005555
```

- Si la interfaz muestra `6,2 %`, pasa `6.2` a esta fórmula. Si el control ya entrega `0.062` en una escala de 0 a 1, usa `0.5555` como coeficiente. [Formatos de sensibilidad en KovaaK’s](https://www.kovaak.com/fpsaimtrainer-faq/#fortnite)
- Usa desplazamiento relativo bruto. Puedes sumar todos los deltas de un fotograma y aplicar el resultado una vez. Omite `deltaTime` y la aceleración para que el mismo desplazamiento produzca el mismo ángulo. Aplica el signo y la inversión vertical según la cámara del motor. Si la API de rotación espera radianes, convierte los grados al final. [Entrada bruta de ratón en Windows](https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-rawmouse)
- En un juego web como PlayCanvas, solicita `canvas.requestPointerLock({ unadjustedMovement: true })` tras un gesto del usuario. Usa los deltas relativos de `mousemove` mientras el lienzo tenga el bloqueo. Si el navegador solo admite el bloqueo estándar, comprueba la distancia real antes de dar por igualada la sensibilidad. [Especificación Pointer Lock](https://w3c.github.io/pointerlock/) · [Entrada de ratón en PlayCanvas](https://api.playcanvas.com/engine/classes/Mouse.html)

## Casos de comprobación

Con **800 DPI** y **6,2 % en X**, un giro completo requiere aproximadamente **33,19 cm**. El DPI sirve para convertir las cuentas en distancia física. El giro por evento ya parte de cuentas del ratón. [Calculadora de Mouse Sensitivity](https://www.mouse-sensitivity.com/n/fortnite/)

```text
cuentasPorVuelta = 360 / (sensibilidadXPorcentaje * 0.005555)
cmPorVuelta     = 914.4 / (DPI * sensibilidadXPorcentaje * 0.005555)
```

| Entrada | Resultado esperado |
| --- | --- |
| 1.000 cuentas en X al 6,2 % | 34,441° de giro |
| 1.000 cuentas en Y al 4,8 % | 26,664° de inclinación antes de aplicar el límite vertical |
| 800 DPI y 6,2 % en X | 33,19 cm por vuelta |
| 800 DPI y 10,0 % en X | 20,58 cm por vuelta |

Para comparar ambos juegos, usa el mismo ratón y perfil de DPI. Coloca la cámara frente a un punto fijo, mueve el ratón en horizontal hasta volver al punto tras una vuelta completa y mide el recorrido. Repite varias veces sin activar el zoom. Si la distancia coincide pero la cámara se siente diferente, compara el campo de visión (FOV). Para trasladar también la sensibilidad al apuntar, repite la medición con la mira concreta que quieras igualar. [Ajustes de FOV de Epic](https://www.epicgames.com/help/c-34254770/c-Tutorials_Settings/a17762816) · [Miras y modos de apuntado en Mouse Sensitivity](https://www.mouse-sensitivity.com/n/fortnite/)

## Ejemplo para un vídeo

> Con 800 DPI y la sensibilidad de Fortnite al 6,2 %, la escala de KovaaK’s predice unos 33 centímetros de movimiento del ratón para dar una vuelta completa. Pon el mismo porcentaje en los dos juegos y comprueba si la cámara vuelve al mismo punto después de recorrer esa distancia.

Muestra el porcentaje y el DPI en pantalla, marca el recorrido con una regla y graba la vuelta en cada juego. Si presentas un dato medido, usa la distancia que obtengas en la grabación.
