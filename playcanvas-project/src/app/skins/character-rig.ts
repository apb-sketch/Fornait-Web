import type { AppBase, Entity, GraphNode } from 'playcanvas';
import { Mat4, Quat, Vec3 } from 'playcanvas';

function collectJoints(part: Entity): Map<string, GraphNode> {
    const joints = new Map<string, GraphNode>();
    for (const render of part.findComponents('render')) {
        for (const mesh of render.meshInstances) {
            for (const joint of mesh.skinInstance?.bones ?? []) {
                joints.set(joint.path.slice(part.path.length + 1), joint);
            }
        }
    }
    return joints;
}

export function followCharacterRig(app: AppBase, body: Entity, parts: Entity[]): void {
    const bodyJoints = collectJoints(body);
    const bindings = parts.flatMap((part) =>
        [...collectJoints(part)].flatMap(([path, target]) => {
            const source = bodyJoints.get(path);
            const parent = target.parent;
            if (!source || !parent) return [];

            // The separate exports can have different bind transforms for the same joint.
            const bindOffset = new Mat4()
                .copy(source.getWorldTransform()).invert().mul(target.getWorldTransform());
            return [{ source, target, parent, bindOffset, depth: path.split('/').length }];
        })
    ).sort((a, b) => a.depth - b.depth);

    const local = new Mat4();
    const translation = new Vec3();
    const rotation = new Quat();
    const scale = new Vec3();
    const sync = () => {
        for (const { source, target, parent, bindOffset } of bindings) {
            local.copy(parent.getWorldTransform()).invert().mul(source.getWorldTransform()).mul(bindOffset);
            target.setLocalPosition(local.getTranslation(translation));
            target.setLocalRotation(rotation.setFromMat4(local));
            target.setLocalScale(local.getScale(scale));
        }
    };

    app.on('prerender', sync);
    app.once('destroy', () => app.off('prerender', sync));
}
