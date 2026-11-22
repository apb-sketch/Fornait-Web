import type { AppBase } from 'playcanvas';
import { Color } from 'playcanvas';

/** Broad sky-like fill, with no local light source. */
export function configureLighting(app: AppBase): void {
    app.scene.ambientLight = new Color(0.78, 0.82, 0.9);
}
