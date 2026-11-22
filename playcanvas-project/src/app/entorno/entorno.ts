import type { AppBase, Entity } from 'playcanvas';

import { configureLighting } from './lighting/lighting';
import { configureShadows } from './shadows/shadows';

/** Configure the lighting and shadows for the environment. */
export function configureEnvironment(app: AppBase, character: Entity): void {
    configureLighting(app);
    configureShadows(app, character);
}
