import type { AppBase } from 'playcanvas';
import { BLEND_NORMAL, Color, Entity, Mesh, MeshInstance, PRIMITIVE_LINES, StandardMaterial } from 'playcanvas';

const GROUND_SIZE = 10000;
const GRID_SIZE = 120;
const GRID_DIVISIONS = 240;
const GRID_OPACITY = 0.12;
// The large PlayCanvas floor needs more depth separation than the original plane.
const GRID_HEIGHT = 0.024;
const FLOOR_ROUGHNESS = 0.94;

function createGrid(app: AppBase, ground: Entity): void {
    const extent = GRID_SIZE / 2;
    const axisColor = new Color().fromString('#716281').linear();
    const lineColor = new Color().fromString('#62566d').linear();
    const positions: number[] = [];
    const colors: number[] = [];
    for (let index = 0; index <= GRID_DIVISIONS; index++) {
        const offset = (index * GRID_SIZE) / GRID_DIVISIONS - extent;
        const color = index === GRID_DIVISIONS / 2 ? axisColor : lineColor;
        const rgb = [color.r, color.g, color.b].map((channel) => Math.round(channel * 255));
        positions.push(-extent, GRID_HEIGHT, offset, extent, GRID_HEIGHT, offset);
        positions.push(offset, GRID_HEIGHT, -extent, offset, GRID_HEIGHT, extent);
        for (let vertex = 0; vertex < 4; vertex++) colors.push(...rgb, 255);
    }

    const mesh = new Mesh(app.graphicsDevice);
    mesh.setPositions(positions);
    mesh.setColors32(colors);
    mesh.update(PRIMITIVE_LINES);

    const material = new StandardMaterial();
    material.useLighting = false;
    material.emissive = new Color(1, 1, 1);
    material.emissiveVertexColor = true;
    material.blendType = BLEND_NORMAL;
    material.opacity = GRID_OPACITY;
    material.depthWrite = false;
    material.update();

    const grid = new Entity('ground-grid');
    grid.addComponent('render', {
        meshInstances: [new MeshInstance(mesh, material, grid)],
        castShadows: false,
        receiveShadows: false
    });
    // Keep the grid independent of the scale of the larger floor plane.
    app.root.addChild(grid);
    grid.setPosition(ground.getPosition());
    app.once('destroy', () => material.destroy());
}

export function createMap(app: AppBase): void {
    const material = new StandardMaterial();
    material.diffuse.fromString('#3c344a');
    material.useMetalness = true;
    material.metalness = 0;
    material.gloss = 1 - FLOOR_ROUGHNESS;
    material.update();

    const ground = new Entity('ground');
    ground.addComponent('render', {
        type: 'plane',
        material,
        isStatic: true,
        castShadows: false,
        receiveShadows: true
    });
    ground.setLocalScale(GROUND_SIZE, 1, GROUND_SIZE);
    ground.setPosition(0, -0.01, 0);
    app.root.addChild(ground);
    createGrid(app, ground);
    app.once('destroy', () => material.destroy());
}
