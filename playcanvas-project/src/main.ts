import {
    AppBase, AnimComponentSystem, AppOptions, CameraComponentSystem, ContainerHandler,
    FILLMODE_FILL_WINDOW, LightComponentSystem, RenderComponentSystem,
    RESOLUTION_AUTO, TextureHandler, createGraphicsDevice
} from 'playcanvas';

import { createScene } from './app/engine/scene';
import './starter.css';

const canvas = document.getElementById('application-canvas') as HTMLCanvasElement;
const device = await createGraphicsDevice(canvas);
device.maxPixelRatio = Math.min(window.devicePixelRatio, 2);

const options = new AppOptions();
options.graphicsDevice = device;
options.componentSystems = [RenderComponentSystem, CameraComponentSystem, LightComponentSystem, AnimComponentSystem];
options.resourceHandlers = [TextureHandler, ContainerHandler];

const app = new AppBase(canvas);
app.init(options);
app.start();
app.setCanvasFillMode(FILLMODE_FILL_WINDOW);
app.setCanvasResolution(RESOLUTION_AUTO);

const resize = () => app.resizeCanvas();
window.addEventListener('resize', resize);
app.on('destroy', () => window.removeEventListener('resize', resize));

await createScene(app, canvas);
