import type { AppBase, Entity } from 'playcanvas';
import { Vec3 } from 'playcanvas';

import { createPlayerMovement } from '../player/movement';

export type CameraMode = 'free' | 'player';

const MOVE_SPEED = 4;
const MOUSE_SENSITIVITY = 0.15;
const PLAYER_CAMERA_DISTANCE = 3.5;
const PLAYER_CAMERA_HEIGHT = 1.3;
const PLAYER_LOOK_HEIGHT = 0.95;
const PLAYER_FRAME_WIDTH = 1.45;

export function enableCameraMovement(
    app: AppBase,
    camera: Entity,
    player: Entity,
    canvas: HTMLCanvasElement,
    setMovement: (x: number, z: number) => void
) {
    const held = new Set<string>();
    const direction = new Vec3();
    const position = new Vec3();
    const movePlayer = createPlayerMovement(player);
    let mode: CameraMode = 'free';
    let yaw = 0;
    let pitch = -7;
    let playerYaw = 180;
    let playerPitch = (-Math.atan2(PLAYER_CAMERA_HEIGHT - PLAYER_LOOK_HEIGHT, PLAYER_CAMERA_DISTANCE) * 180) / Math.PI;

    const placePlayerCamera = () => {
        const radians = (yaw * Math.PI) / 180;
        const playerPosition = player.getPosition();
        const verticalFov = camera.camera?.fov ?? 45;
        const aspect = Math.max(1, canvas.clientWidth) / Math.max(1, canvas.clientHeight);
        const frustumWidthPerUnit = 2 * Math.tan((verticalFov * Math.PI) / 360) * aspect;
        const distance = Math.max(PLAYER_CAMERA_DISTANCE, PLAYER_FRAME_WIDTH / frustumWidthPerUnit);
        camera.setPosition(
            playerPosition.x + Math.sin(radians) * distance,
            playerPosition.y + PLAYER_CAMERA_HEIGHT,
            playerPosition.z + Math.cos(radians) * distance
        );
        camera.setEulerAngles(pitch, yaw, 0);
    };

    const setMode = (nextMode: CameraMode) => {
        if (nextMode === mode) return;
        if (mode === 'player') {
            playerYaw = yaw;
            playerPitch = pitch;
        }
        mode = nextMode;
        held.clear();
        if (mode === 'player') {
            yaw = playerYaw;
            pitch = playerPitch;
            placePlayerCamera();
        }
    };

    const down = (event: KeyboardEvent) => {
        if (document.body.classList.contains('settings-open')) return;
        if (['KeyW', 'KeyA', 'KeyS', 'KeyD'].includes(event.code)) {
            event.preventDefault();
            held.add(event.code);
        }
    };
    const up = (event: KeyboardEvent) => held.delete(event.code);
    const clear = () => held.clear();
    const capturePointer = async () => {
        if (document.body.classList.contains('settings-open') || document.pointerLockElement === canvas) return;
        try {
            await canvas.requestPointerLock();
        } catch {
            // Some embedded browsers reject pointer lock. WASD can still work.
        }
    };
    const look = (event: MouseEvent) => {
        if (document.pointerLockElement !== canvas) return;
        yaw -= event.movementX * MOUSE_SENSITIVITY;
        pitch = Math.max(-75, Math.min(60, pitch - event.movementY * MOUSE_SENSITIVITY));
        camera.setEulerAngles(pitch, yaw, 0);
    };
    const move = (dt: number) => {
        if (document.body.classList.contains('settings-open')) {
            held.clear();
            setMovement(0, 0);
            return;
        }

        const moveX = Number(held.has('KeyD')) - Number(held.has('KeyA'));
        const moveZ = Number(held.has('KeyW')) - Number(held.has('KeyS'));
        direction.set(0, 0, 0);
        if (mode === 'free') {
            setMovement(0, 0);
            if (held.has('KeyW')) direction.add(camera.forward);
            if (held.has('KeyS')) direction.sub(camera.forward);
            if (held.has('KeyD')) direction.add(camera.right);
            if (held.has('KeyA')) direction.sub(camera.right);
            if (direction.lengthSq() > 0) {
                position.copy(camera.getPosition()).add(direction.normalize().mulScalar(MOVE_SPEED * dt));
                camera.setPosition(position);
            }
            return;
        }

        setMovement(moveX, moveZ);
        movePlayer(moveX, moveZ, yaw, dt);
        placePlayerCamera();
    };

    window.addEventListener('keydown', down);
    window.addEventListener('keyup', up);
    window.addEventListener('blur', clear);
    canvas.addEventListener('click', capturePointer);
    document.addEventListener('mousemove', look);
    app.on('update', move);
    app.once('destroy', () => {
        window.removeEventListener('keydown', down);
        window.removeEventListener('keyup', up);
        window.removeEventListener('blur', clear);
        canvas.removeEventListener('click', capturePointer);
        document.removeEventListener('mousemove', look);
        if (document.pointerLockElement === canvas) document.exitPointerLock();
        app.off('update', move);
    });

    return { setMode, capturePointer };
}
