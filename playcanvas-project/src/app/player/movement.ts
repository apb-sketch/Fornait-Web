import type { Entity } from 'playcanvas';
import { Vec3 } from 'playcanvas';

// Matches the original character movement speed in camera.ts.
const MOVE_SPEED = 4;

/** Update player rotation and position using camera-relative WASD axes. */
export function createPlayerMovement(player: Entity) {
    const forward = new Vec3();
    const right = new Vec3();
    const direction = new Vec3();
    const position = new Vec3();

    return (x: number, z: number, yaw: number, dt: number): void => {
        const radians = (yaw * Math.PI) / 180;
        forward.set(-Math.sin(radians), 0, -Math.cos(radians));
        right.set(Math.cos(radians), 0, -Math.sin(radians));
        direction.set(0, 0, 0);
        if (z > 0) direction.add(forward);
        if (z < 0) direction.sub(forward);
        if (x > 0) direction.add(right);
        if (x < 0) direction.sub(right);
        player.setEulerAngles(0, yaw - 180, 0);
        if (direction.lengthSq() > 0) {
            position.copy(player.getPosition()).add(direction.normalize().mulScalar(MOVE_SPEED * dt));
            position.y = player.getPosition().y;
            player.setPosition(position);
        }
    };
}
