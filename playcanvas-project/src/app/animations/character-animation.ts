import type { AppBase, Asset, AnimTrack, ContainerResource, Entity } from 'playcanvas';

import { getMovementAnimationName, MOVEMENT_CLIP_INDEX } from './movement/movement';

function findTrack(resource: ContainerResource, name: string, index: number): AnimTrack {
    const animation = resource.animations[index] as Asset<'animation', AnimTrack> | undefined;
    if (!animation?.resource) {
        throw new Error(`Animation "${name}" was not found. Available clips: ${resource.animations.map((asset) => asset.name).join(', ')}`);
    }
    return animation.resource;
}

export function createCharacterAnimationController(
    app: AppBase,
    character: Entity,
    characterResource: ContainerResource,
    danceResource: ContainerResource
) {
    character.addComponent('anim', { activate: true });
    const animation = character.anim;
    if (!animation) throw new Error('Could not create the character animation component');

    for (const [state, index] of Object.entries(MOVEMENT_CLIP_INDEX)) {
        animation.assignAnimation(state, findTrack(characterResource, state, index), undefined, 1, true);
    }
    animation.assignAnimation('Dance', findTrack(danceResource, 'dance', 0), undefined, 1, false);
    const layer = animation.baseLayer;
    if (!layer) throw new Error('The character animation layer was not created');
    layer.play('idle');

    let nextLocomotion = 'idle';
    const setLocomotion = (x: number, z: number) => {
        nextLocomotion = getMovementAnimationName(x, z);
        if (layer.activeState === 'Dance' && nextLocomotion === 'idle') return;
        if (layer.activeState === nextLocomotion) return;
        layer.transition(nextLocomotion, 0.12);
    };

    const playDance = () => {
        if (layer.activeState === 'Dance') {
            layer.activeStateCurrentTime = 0;
        } else {
            layer.transition('Dance', 0.16);
        }
    };
    const keydown = (event: KeyboardEvent) => {
        if (event.code !== 'KeyP' || event.repeat || document.body.classList.contains('settings-open')) return;
        event.preventDefault();
        playDance();
    };
    const update = () => {
        if (layer.activeState === 'Dance' && layer.activeStateCurrentTime >= layer.activeStateDuration) {
            layer.transition(nextLocomotion, 0.16);
        }
    };

    window.addEventListener('keydown', keydown);
    app.on('update', update);
    app.once('destroy', () => {
        window.removeEventListener('keydown', keydown);
        app.off('update', update);
    });

    return { setLocomotion, playDance };
}
