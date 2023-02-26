import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";

export function spawnCar(group, color = 0xff0000, x = 0, y = 0, z = 0, rot_x = 0, rot_y = 0, rot_z = 0) {
    const wheels = [];

    const shadow = new THREE.TextureLoader().load("assets/models/gltf/ferrari_ao.png");

    const dracoLoader = new DRACOLoader();
    dracoLoader.setDecoderPath("three/addons/libs/draco/gltf/");

    const loader = new GLTFLoader();
    loader.setDRACOLoader(dracoLoader);

    const bodyMaterial = new THREE.MeshPhysicalMaterial({
        color: color,
        metalness: 1.0,
        roughness: 0.5,
        clearcoat: 1.0,
        clearcoatRoughness: 0.03,
        sheen: 0.5,
    });

    const detailsMaterial = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        metalness: 1.0,
        roughness: 0.5,
    });

    const glassMaterial = new THREE.MeshPhysicalMaterial({
        color: 0xffffff,
        metalness: 0.25,
        roughness: 0,
        transmission: 1.0,
    });

    loader.load("assets/models/gltf/ferrari.glb", function (gltf) {
        let carModel = gltf.scene.children[0];
        carModel.getObjectByName("body").material = bodyMaterial;

        carModel.getObjectByName("rim_fl").material = detailsMaterial;
        carModel.getObjectByName("rim_fr").material = detailsMaterial;
        carModel.getObjectByName("rim_rr").material = detailsMaterial;
        carModel.getObjectByName("rim_rl").material = detailsMaterial;
        carModel.getObjectByName("trim").material = detailsMaterial;

        carModel.getObjectByName("glass").material = glassMaterial;

        wheels.push(
            carModel.getObjectByName("wheel_fl"),
            carModel.getObjectByName("wheel_fr"),
            carModel.getObjectByName("wheel_rl"),
            carModel.getObjectByName("wheel_rr")
        );

        // shadow
        const mesh = new THREE.Mesh(
            new THREE.PlaneGeometry(0.655 * 4, 1.3 * 4),
            new THREE.MeshBasicMaterial({
                map: shadow,
                blending: THREE.MultiplyBlending,
                toneMapped: false,
                transparent: true,
            })
        );
        mesh.rotation.x = -Math.PI / 2;
        mesh.renderOrder = 2;
        carModel.add(mesh);

        carModel.position.set(x, y, z);
        carModel.rotation.set(rot_x, rot_y, rot_z);
        group.add(carModel);
    });
}
