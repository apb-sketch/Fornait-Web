import type { AppBase, Asset, ContainerResource } from 'playcanvas';
import { Color, Entity } from 'playcanvas';

import danceUrl from '../animations/emotes/caderas-fiesteras/dance.glb?url';
import { createFpsCounter } from '../HUD/fps';
import { createSettings } from '../HUD/settings';
import { createMap } from '../entorno/map/map';
import { configureEnvironment } from '../entorno/entorno';
import accessoryUrl from '../skins/F_MED_ShoneStays/accessory.glb?url';
import bodyUrl from '../skins/F_MED_ShoneStays/body.glb?url';
import headUrl from '../skins/F_MED_ShoneStays/head.glb?url';

import { enableCameraMovement } from '../camera/camera';
import { createCharacterAnimationController } from '../animations/character-animation';
import { followCharacterRig } from '../skins/character-rig';

function loadContainer(app: AppBase, name: string, url: string): Promise<ContainerResource> {
    return new Promise((resolve, reject) => {
        app.assets.loadFromUrl(url, 'container', (error: string | null, asset?: Asset) => {
            if (error || !asset?.resource) {
                reject(new Error(`Could not load ${name}: ${error ?? 'missing resource'}`));
                return;
            }
            resolve(asset.resource as ContainerResource);
        });
    });
}

async function loadPart(app: AppBase, name: string, url: string): Promise<Entity> {
    const resource = await loadContainer(app, name, url);
    const entity = resource.instantiateRenderEntity() as Entity;
    entity.name = name;
    return entity;
}

function enableShadowCasting(entity: Entity): void {
    if (entity.render) entity.render.castShadows = true;
    for (const child of entity.children) enableShadowCasting(child as Entity);
}

export async function createScene(app: AppBase, canvas: HTMLCanvasElement): Promise<void> {
    createFpsCounter(app);
    const camera = new Entity('camera');
    camera.addComponent('camera', { clearColor: new Color(0.54, 0.69, 0.82), farClip: 1000 });
    camera.setPosition(0, 1.5, 3.6);
    camera.setEulerAngles(-7, 0, 0);
    app.root.addChild(camera);
    createMap(app);

    const character = new Entity('character');
    app.root.addChild(character);
    configureEnvironment(app, character);
    let animation: ReturnType<typeof createCharacterAnimationController> | undefined = undefined;
    const controls = enableCameraMovement(app, camera, character, canvas, (x, z) => {
        animation?.setLocomotion(x, z);
    });
    const settings = createSettings(app, canvas, controls, () => animation?.playDance());

    const [bodyResource, danceResource, head, accessory] = await Promise.all([
        loadContainer(app, 'body', bodyUrl),
        loadContainer(app, 'dance', danceUrl),
        loadPart(app, 'head', headUrl),
        loadPart(app, 'accessory', accessoryUrl)
    ]);
    const body = bodyResource.instantiateRenderEntity() as Entity;
    body.name = 'body';
    const parts = [body, head, accessory];
    for (const part of parts) {
        enableShadowCasting(part);
        character.addChild(part);
    }
    followCharacterRig(app, body, [head, accessory]);
    animation = createCharacterAnimationController(app, body, bodyResource, danceResource);
    settings.enableDance();
}
