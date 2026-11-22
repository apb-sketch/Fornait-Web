# PlayCanvas · Proyecto Fortnite (visor experimental)

Proyecto TypeScript con PlayCanvas Engine y Vite. Los recursos de referencia se conservan
separados de las funcionalidades implementadas: **no se presupone que el comportamiento
sea idéntico al de Fortnite**.

## Inicio

Requiere Node.js >=22.23.2 (ver `package.json`). El proyecto incluye `bun.lock`.

```bash
bun install
bun run dev
```

También están disponibles `bun run typecheck`, `bun run lint` y `bun run build`.

## Organización

- `src/main.ts`: inicializa PlayCanvas y arranca la escena.
- `src/app/engine/scene.ts`: crea las entidades y conecta los módulos; no reimplementa el motor.
- `src/app/camera/`: control de cámara, FOV, POV e información de referencia.
- `src/app/player/`: desplazamiento del jugador; no hay físicas ni colisiones implementadas.
- `src/app/skins/`: rig y recursos agrupados por skin.
- `src/app/animations/`: reproducción de animaciones, movimiento, emotes y sprays.
- `src/app/entorno/`: mapa, iluminación y sombras.
- `src/app/builds/`: modelos y JSON de referencia de construcción; aún sin sistema jugable.
- `src/app/HUD/`: FPS y menú de configuración.

Los archivos `provenance.json` documentan el origen y hashes de los recursos. Los JSON
importados en carpetas `reference/` son **referencias**, no ajustes activos del motor.

## Controles existentes

- `WASD`: desplazar la cámara libre o el personaje, según el modo elegido.
- Ratón con captura de puntero: orientar la cámara.
- `Escape`: abrir/cerrar el menú de ajustes.
- `P`: reproducir el baile «Caderas fiesteras».

## Inspector

Existe `src/inspector.ts`, pero la configuración actual de Vite **no lo carga automáticamente**.
No se ha cambiado esta funcionalidad durante la reorganización.

## Alcance

Esta reorganización traslada código, modelos, texturas y JSON por **concepto**.
No introduce física, construcción, apuntado ni equivalencias de Fortnite que no estén
respaldadas por los datos presentes. Los recursos originales y sus procedencias se conservan.
