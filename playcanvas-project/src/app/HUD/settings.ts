import type { AppBase } from 'playcanvas';

import type { CameraMode } from '../camera/camera';

export function createSettings(
    app: AppBase,
    canvas: HTMLCanvasElement,
    controls: { setMode: (mode: CameraMode) => void; capturePointer: () => Promise<void> },
    playDance: () => void
) {
    const dialog = document.createElement('dialog');
    dialog.className = 'settings-panel';
    dialog.setAttribute('aria-labelledby', 'settings-title');
    dialog.innerHTML = `
            <h1 id="settings-title">Settings</h1>
            <div class="settings-options" aria-label="Camera mode">
                <button class="settings-option" type="button" data-camera-mode="free" aria-pressed="true">
                    <span>Free camera</span><small>WASD moves the camera</small>
                </button>
                <button class="settings-option" type="button" data-camera-mode="player" aria-pressed="false">
                    <span>Player POV</span><small>WASD moves the character</small>
                </button>
            </div>
            <h2 class="settings-section-title" lang="es">Baile</h2>
            <button class="settings-option settings-dance" type="button" lang="es" aria-keyshortcuts="P" disabled>
                <span>Caderas fiesteras</span><kbd>P</kbd>
            </button>
            <button class="settings-resume" type="button">Continue</button>
    `;
    document.body.appendChild(dialog);

    const options = [...dialog.querySelectorAll<HTMLButtonElement>('[data-camera-mode]')];
    const danceButton = dialog.querySelector<HTMLButtonElement>('.settings-dance')!;
    let wasLocked = document.pointerLockElement === canvas;
    const open = () => {
        if (dialog.open) return;
        document.body.classList.add('settings-open');
        if (document.pointerLockElement === canvas) {
            wasLocked = false;
            document.exitPointerLock();
        }
        dialog.showModal();
        options.find((option) => option.getAttribute('aria-pressed') === 'true')?.focus();
    };

    const close = () => {
        dialog.close();
        document.body.classList.remove('settings-open');
    };
    const resume = () => {
        close();
        void controls.capturePointer();
    };
    const keydown = (event: KeyboardEvent) => {
        if (event.code !== 'Escape') return;
        event.preventDefault();
        if (event.repeat) return;
        if (dialog.open) close();
        else open();
    };
    const pointerLockChanged = () => {
        const locked = document.pointerLockElement === canvas;
        const justUnlocked = wasLocked && !locked;
        wasLocked = locked;
        // Browsers can consume Escape themselves while the pointer is locked.
        if (justUnlocked) open();
    };

    for (const option of options) {
        option.addEventListener('click', () => {
            const mode = option.dataset.cameraMode;
            if (mode !== 'free' && mode !== 'player') return;
            controls.setMode(mode);
            for (const button of options) {
                button.setAttribute('aria-pressed', String(button === option));
            }
            resume();
        });
    }

    danceButton.addEventListener('click', () => {
        close();
        playDance();
    });
    dialog.querySelector('.settings-resume')?.addEventListener('click', resume);
    window.addEventListener('keydown', keydown);
    document.addEventListener('pointerlockchange', pointerLockChanged);
    app.once('destroy', () => {
        window.removeEventListener('keydown', keydown);
        document.removeEventListener('pointerlockchange', pointerLockChanged);
        dialog.remove();
        document.body.classList.remove('settings-open');
    });

    return { enableDance: () => { danceButton.disabled = false; } };
}
