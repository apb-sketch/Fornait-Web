import type { AppBase } from 'playcanvas';
import { BoundingBox, Color, Entity, SHADOW_PCF3_32F, Vec3 } from 'playcanvas';

const SHADOW_HALF_EXTENT = 4;
const SHADOW_MAP_SIZE = 2048;
const SHADOW_INTENSITY = 0.34;

export function configureShadows(app: AppBase, character: Entity): void {
    const sun = new Entity('shadow-sun');
    sun.addComponent('light', {
        type: 'directional',
        color: new Color().fromString('#fff5f1'),
        intensity: 1.65,
        castShadows: true,
        shadowType: SHADOW_PCF3_32F,
        shadowResolution: SHADOW_MAP_SIZE,
        shadowIntensity: SHADOW_INTENSITY,
        normalOffsetBias: 0.023,
        // PlayCanvas converts 0.02 to a depth bias of -0.0002.
        shadowBias: 0.02
    });
    sun.setPosition(4, 7, 3);
    sun.lookAt(Vec3.ZERO);
    sun.rotateLocal(90, 0, 0);
    app.root.addChild(sun);

    const light = sun.light;
    if (!light) throw new Error('Could not create the directional light');
    const bounds = new BoundingBox(new Vec3(), new Vec3(SHADOW_HALF_EXTENT, SHADOW_HALF_EXTENT, SHADOW_HALF_EXTENT));
    const follow = () => {
        const position = character.getPosition();
        if (light.shadowBounds && bounds.center.equals(position)) return;
        bounds.center.copy(position);
        light.shadowBounds = bounds;
    };
    follow();
    app.on('prerender', follow);
    app.once('destroy', () => app.off('prerender', follow));
}
