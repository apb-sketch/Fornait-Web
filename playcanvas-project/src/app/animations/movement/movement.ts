/** Animation order embedded in src/app/skins/F_MED_ShoneStays/body.glb. */
export const MOVEMENT_CLIP_INDEX: Readonly<Record<string, number>> = {
    N: 0,
    NE: 1,
    E: 2,
    SE: 3,
    S: 4,
    SW: 5,
    W: 6,
    NW: 7,
    idle: 8
};

export function getMovementAnimationName(x: number, z: number): string {
    if (z > 0) return x > 0 ? 'NE' : x < 0 ? 'NW' : 'N';
    if (z < 0) return x > 0 ? 'SE' : x < 0 ? 'SW' : 'S';
    return x > 0 ? 'E' : x < 0 ? 'W' : 'idle';
}
