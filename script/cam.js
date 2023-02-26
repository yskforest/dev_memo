import * as THREE from "../three.js/build/three.module.js";
import { OrbitControls } from "../three.js/examples/jsm/controls/OrbitControls.js";
import { GUI } from "../three.js/examples/jsm/libs/lil-gui.module.min.js";
import { TransformControls } from "../three.js/examples/jsm/controls/TransformControls.js";

let mesh;
let cameraRig, activeCamera, activeHelper;
let cameraPerspective, cameraOrtho;
let cameraPerspectiveHelper, cameraOrthoHelper;
let frustumSize = 50;
let cameraFovH = 90.0;
let cameraW = 1280;
let cameraH = 720;
let cameraAspect = cameraW / cameraH;
let tfControl;
const localWorld = new THREE.Group();

window.addEventListener("DOMContentLoaded", init);

function init() {
    const scene = new THREE.Scene();

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.autoClear = false;
    document.body.appendChild(renderer.domElement);

    // camera -----------------------------------------------------
    const screenAspect = window.innerWidth / window.innerHeight;
    const camera = new THREE.PerspectiveCamera(60, 0.5 * screenAspect, 1, 10000);
    camera.position.set(-25, 25, 25);

    const aspect = cameraW / cameraH;
    const cameraFovV = fovH2V(cameraFovH, aspect);
    cameraPerspective = new THREE.PerspectiveCamera(cameraFovV, aspect, 0.01, 300);
    cameraPerspectiveHelper = new THREE.CameraHelper(cameraPerspective);
    scene.add(cameraPerspectiveHelper);

    cameraOrtho = new THREE.OrthographicCamera(
        -frustumSize,
        frustumSize,
        frustumSize / aspect,
        -frustumSize / aspect,
        0.01,
        300
    );
    cameraOrthoHelper = new THREE.CameraHelper(cameraOrtho);
    scene.add(cameraOrthoHelper);

    activeCamera = cameraPerspective;
    activeHelper = cameraPerspectiveHelper;

    cameraRig = new THREE.Group();
    cameraRig.add(cameraPerspective);
    cameraRig.add(cameraOrtho);
    scene.add(cameraRig);

    const orbit = new OrbitControls(camera, renderer.domElement);
    orbit.minZoom = 0.5;
    orbit.maxZoom = 2;

    // light
    const light = new THREE.DirectionalLight(0xffffff, 2);
    light.position.set(-1, 1, -1);
    scene.add(light);
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    // set world object -----------------------------------------------------
    // const boxGeo = new THREE.BoxGeometry(10, 10, 10);
    // var mat = new THREE.MeshBasicMaterial({ wireframe: true });
    // const box = new THREE.Mesh(boxGeo, mat);
    // // scene.add(box);

    const clipPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
    renderer.localClippingEnabled = true;

    const matEq = new THREE.MeshBasicMaterial({
        side: THREE.DoubleSide,
        // opacity: 0.5,
        // transparent: true,
        clippingPlanes: [clipPlane],
        clipShadows: true,
    });

    const textureLoader = new THREE.TextureLoader();
    textureLoader.load("sample.png", function (map) {
        map.anisotropy = 8;
        // map.encoding = THREE.sRGBEncoding;
        matEq.map = map;
        matEq.needsUpdate = true;
    });

    const meshEq = new THREE.Mesh(new THREE.SphereGeometry(10, 36, 18), matEq);
    meshEq.rotateY(Math.PI / 2);
    scene.add(meshEq);

    mesh = new THREE.Mesh(
        new THREE.SphereGeometry(1, 16, 8),
        new THREE.MeshBasicMaterial({ color: 0xffff00, wireframe: true })
    );
    scene.add(mesh);

    const mesh2 = new THREE.Mesh(
        new THREE.SphereGeometry(0.5, 16, 8),
        new THREE.MeshBasicMaterial({ color: 0x00ff00, wireframe: true })
    );
    mesh.add(mesh2);

    const mesh3 = new THREE.Mesh(
        new THREE.SphereGeometry(5, 16, 8),
        new THREE.MeshBasicMaterial({ color: 0x0000ff, wireframe: true })
    );
    mesh3.position.z = 150;
    cameraRig.add(mesh3);

    tfControl = new TransformControls(camera, renderer.domElement);
    tfControl.addEventListener("change", render);
    tfControl.addEventListener("dragging-changed", function (event) {
        orbit.enabled = !event.value;
    });

    tfControl.attach(cameraPerspective);
    scene.add(tfControl);
    // tfControl.setMode('rotate');
    tfControl.showX = !tfControl.showX;
    tfControl.showY = !tfControl.showY;
    tfControl.showZ = !tfControl.showZ;

    // tick -----------------------------------------------------
    window.addEventListener("resize", onWindowResize);
    document.addEventListener("keydown", onKeyDown);
    createGui();
    tick();

    // function -----------------------------------------------------
    function tick() {
        const r = Date.now() * 0.0005;

        mesh.position.x = 10 * Math.cos(r);
        mesh.position.z = 10 * Math.sin(r);
        mesh.children[0].position.z = 70 * Math.sin(r);

        if (activeCamera === cameraPerspective) {
            cameraPerspective.updateProjectionMatrix();
            cameraPerspectiveHelper.update();
            cameraPerspectiveHelper.visible = true;
            cameraOrthoHelper.visible = false;
        } else {
            cameraOrtho.updateProjectionMatrix();
            cameraOrthoHelper.update();
            cameraOrthoHelper.visible = true;
            cameraPerspectiveHelper.visible = false;
        }

        // cameraRig.lookAt(localWorld.position);
        // cameraPerspective.rotation.y = Math.PI;
        // cameraPerspective.rotation.y = Math.PI;

        const w = window.innerWidth;
        const h = window.innerHeight;
        renderer.clear();
        renderer.setViewport(w / 2, 0, w / 2, h);
        renderer.render(scene, camera);
        const capCamH = w / 2 / cameraAspect;
        renderer.setViewport(0, h / 2 - capCamH / 2, w / 2, capCamH);
        renderer.render(scene, activeCamera);
        requestAnimationFrame(tick);
    }

    function onKeyDown(event) {
        switch (event.keyCode) {
            case 79: // O
                activeCamera = cameraOrtho;
                activeHelper = cameraOrthoHelper;
                break;
            case 80: // P
                activeCamera = cameraPerspective;
                activeHelper = cameraPerspectiveHelper;
                break;
            case 81: // Q
                tfControl.setSpace(tfControl.space === "local" ? "world" : "local");
                break;
            case 16: // Shift
                break;
            case 87: // W
                tfControl.setMode("translate");
                break;
            case 69: // E
                tfControl.setMode("rotate");
                break;
            case 82: // Rwer
                tfControl.setMode("scale");
                break;
            case 67: // C
                break;
            case 86: // V
                break;
            case 88: // X
                tfControl.showX = !tfControl.showX;
                break;
            case 89: // Y
                tfControl.showY = !tfControl.showY;
                break;
            case 90: // Z
                tfControl.showZ = !tfControl.showZ;
                break;
            case 32: // Spacebar
                tfControl.enabled = !tfControl.enabled;
                break;
            case 27: // Esc
                tfControl.reset();
                break;
        }
    }

    function onWindowResize() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        const aspect = w / h;
        renderer.setSize(w, h);
        camera.aspect = aspect / 2;
        camera.updateProjectionMatrix();

        cameraOrtho.left = (-0.5 * frustumSize * aspect) / 2;
        cameraOrtho.right = (0.5 * frustumSize * aspect) / 2;
        cameraOrtho.top = frustumSize / 2;
        cameraOrtho.bottom = -frustumSize / 2;
        cameraOrtho.updateProjectionMatrix();
    }

    function createGui() {
        const panel = new GUI();

        const roll = cameraPerspective.rotation.z * (180 / Math.PI);
        const pitch = cameraPerspective.rotation.x * (180 / Math.PI);
        const yaw = cameraPerspective.rotation.y * (180 / Math.PI);

        const folder0 = panel.addFolder("camera setting").close();
        let params = {
            fovH: cameraFovH,
            cameraW: cameraW,
            cameraH: cameraH,
            roll: roll,
            pitch: pitch,
            yaw: yaw,
        };
        folder0.add(params, "fovH", 1.0, 180.0, 0.1).onChange(function () {
            cameraPerspective.fov = fovH2V(params.fovH, cameraAspect);
            cameraPerspective.updateProjectionMatrix();
        });
        folder0.add(params, "cameraW", 10, 10000, 1).onChange(function () {
            cameraW = params.cameraW;
            cameraAspect = cameraW / cameraH;
            cameraPerspective.aspect = cameraW / cameraH;
            cameraPerspective.updateProjectionMatrix();
        });
        folder0.add(params, "cameraH", 10, 10000, 1).onChange(function () {
            cameraH = params.cameraH;
            cameraAspect = cameraW / cameraH;
            cameraPerspective.aspect = cameraW / cameraH;
            cameraPerspective.updateProjectionMatrix();
        });
        folder0.add(cameraPerspective.position, "x", -10, 10);
        folder0.add(cameraPerspective.position, "y", -10, 10);
        folder0.add(cameraPerspective.position, "z", -10, 10);
        folder0.add(params, "roll", -180, 180).onChange(function () {
            cameraPerspective.rotation.x = params.pitch * (Math.PI / 180);
            cameraPerspective.rotation.y = params.yaw * (Math.PI / 180);
            cameraPerspective.rotation.z = params.roll * (Math.PI / 180);
        });
        folder0.add(params, "pitch", -180, 180).onChange(function () {
            cameraPerspective.rotation.x = params.pitch * (Math.PI / 180);
            cameraPerspective.rotation.y = params.yaw * (Math.PI / 180);
            cameraPerspective.rotation.z = params.roll * (Math.PI / 180);
        });
        folder0.add(params, "yaw", -180, 180).onChange(function () {
            cameraPerspective.rotation.x = params.pitch * (Math.PI / 180);
            cameraPerspective.rotation.y = params.yaw * (Math.PI / 180);
            cameraPerspective.rotation.z = params.roll * (Math.PI / 180);
        });

        const folder1 = panel.addFolder("test setting").close();
        let paramsTest = {
            color: 0x00ff00,
            scale: 1,
        };
        folder1.add(matEq, "wireframe").onChange(function () {
            // meshEq.material();
        });
        folder1.addColor(paramsTest, "color").onChange(function () {
            cube.material.color.set(params.color);
        });
        folder1.add(paramsTest, "scale", 1.0, 4.0).onChange(function () {
            cube.scale.set(params.scale, params.scale, params.scale);
        });
    }

    function render() {}
}

function fovH2V(fovH, aspect) {
    const fovV = (Math.atan(Math.tan((fovH * Math.PI) / 360) / aspect) * 360) / Math.PI;
    return fovV;
}
