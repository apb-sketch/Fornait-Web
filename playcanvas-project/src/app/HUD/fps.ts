import type { AppBase } from 'playcanvas';

/** Adds a small, low-overhead FPS counter to the upper-left corner. */
export function createFpsCounter(app: AppBase): void {
    const counter = document.createElement('div');
    counter.className = 'fps-counter';
    counter.setAttribute('role', 'status');
    counter.setAttribute('aria-label', 'Frames per second');
    counter.innerHTML = '<span>FPS</span><strong>--</strong>';
    document.body.appendChild(counter);

    const value = counter.querySelector('strong');
    let frames = 0;
    let elapsed = 0;

    const update = (dt: number) => {
        frames += 1;
        elapsed += dt;
        if (elapsed < 0.25 || !value) return;

        value.textContent = String(Math.round(frames / elapsed));
        frames = 0;
        elapsed = 0;
    };

    app.on('update', update);
    app.once('destroy', () => {
        app.off('update', update);
        counter.remove();
    });
}
