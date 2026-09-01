import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

export default function DigitalTwin3D(props) {

    const containerRef = useRef(null);
    const acRef = useRef(null);
    const fanRef = useRef(null);
    const temperatureRef = useRef(null);
    const [twinState, setTwinState] =
        useState({
            temperature: null,
            humidity: null,
            air_conditioner: null
        });

    const twinStateRef = useRef(twinState);
    twinStateRef.current = twinState;
    const [selectedObject, setSelectedObject] = useState(null);
    const selectedMeshRef = useRef(null);
    const selectedDevice = selectedObject?.deviceId;

    const handleObjectSelected = (
        object
    ) => {

        setSelectedObject(
            object
        );
        props.onObjectSelected(object.userData);

        if (selectedMeshRef.current) {
            selectedMeshRef.current.scale.set(1, 1, 1);

        }
        object.scale.set(1.2, 1.2, 1.2);
        selectedMeshRef.current = object;

    };



    useEffect(() => {

        const socket =
            new WebSocket("ws://127.0.0.1:8000/ws");

        socket.onopen = () => {
            console.log("Connected to Digital Twin");
        };

        socket.onmessage = (event) => {

            const message = JSON.parse(event.data);

            console.log("Twin message:", message);

            if (message.type === "twin_state") {
                setTwinState(message.data);
            }

        };

        socket.onclose = () => {
            console.log("Twin disconnected");
        };

        return () => {
            socket.close();
        };

    }, []);



    useEffect(() => {

        if (!acRef.current) {
            return;
        }

        if (twinState.air_conditioner === "ON") {
            acRef.current.material.emissive = new THREE.Color(0x3366ff);
        } else {
            acRef.current.material.emissive = new THREE.Color(0x000000);
        }

    }, [twinState]);

    useEffect(() => {

        const temperature = twinState.temperature;

        if (temperatureRef.current === null || temperature === null) {
            return;
        }

        if (temperature > 30) {
            temperatureRef.current.material.color.set(0xff0000);
        } else {
            temperatureRef.current.material.color.set(0x00ff00);
        }

    }, [twinState]);

    useEffect(() => {

        const container = containerRef.current;

        // Scene
        const scene = new THREE.Scene();

        scene.background = new THREE.Color(0x202020);

        // Camera
        const camera = new THREE.PerspectiveCamera(
            60,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );

        camera.position.set(8, 6, 10);

        camera.lookAt(0, 1, 0);

        // Renderer
        const renderer = new THREE.WebGLRenderer({
            antialias: true
        });

        renderer.setSize(
            container.clientWidth,
            container.clientHeight
        );

        container.appendChild(
            renderer.domElement
        );

        const controls = new OrbitControls(camera, renderer.domElement);

        controls.enableDamping = true;

        controls.target.set(
            0,
            1,
            0
        );

        const raycaster =
            new THREE.Raycaster();

        const mouse =
            new THREE.Vector2();
        function onMouseClick(event) {
            const rect =
                renderer.domElement
                    .getBoundingClientRect();

            mouse.x =
                (
                    (event.clientX - rect.left)
                    / rect.width
                ) * 2 - 1;

            mouse.y =
                -(
                    (event.clientY - rect.top)
                    / rect.height
                ) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            const intersects =
                raycaster.intersectObjects(scene.children, true);

            if (intersects.length > 0) {
                const object = intersects[0].object;

                console.log("Clicked:", object);
                console.log("Twin metadata:", object.userData);

                if (
                    object.userData &&
                    object.userData.deviceId
                ) {
                    handleObjectSelected(object);
                }
            }
        }
        renderer.domElement.addEventListener("click", onMouseClick);


        // Light
        const light = new THREE.DirectionalLight(0xffffff, 2);
        light.position.set(5, 10, 5);
        scene.add(light);

        // Ambient light
        const ambient = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambient);

        const floorGeometry = new THREE.BoxGeometry(10, 0.2, 8);
        const floorMaterial = new THREE.MeshStandardMaterial({ color: 0x808080 });
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.position.y = -0.1;
        scene.add(floor);

        const wallMaterial = new THREE.MeshStandardMaterial({ color: 0xcccccc });
        const backWall = new THREE.Mesh(new THREE.BoxGeometry(10, 4, 0.2), wallMaterial);
        backWall.position.set(0, 2, -4);
        scene.add(backWall);

        const sideWall = new THREE.Mesh(new THREE.BoxGeometry(0.2, 4, 8), wallMaterial);
        sideWall.position.set(-5, 2, 0);
        scene.add(sideWall);

        const table = new THREE.Mesh(
            new THREE.BoxGeometry(4, 0.3, 2),
            new THREE.MeshStandardMaterial({ color: 0x8b5a2b })
        );
        table.position.y = 1.2;
        scene.add(table);

        const ac = new THREE.Mesh(
            new THREE.BoxGeometry(2, 0.5, 0.5),
            new THREE.MeshStandardMaterial({ color: 0xffffff })
        );
        ac.position.set(0, 3.2, -3.7);
        scene.add(ac);
        acRef.current = ac;
        ac.userData = {
            deviceId: "ac-001",
            type: "air_conditioner",
            room: "meeting_room"
        };


        const fan = new THREE.Mesh(
            new THREE.CylinderGeometry(0.25, 0.25, 0.1, 32),
            new THREE.MeshStandardMaterial({ color: 0x444444 })
        );
        fan.position.set(0, 3.2, -3.4);
        scene.add(fan);
        fanRef.current = fan;

        const temperatureIndicator = new THREE.Mesh(
            new THREE.SphereGeometry(0.4, 32, 32),
            new THREE.MeshStandardMaterial({ color: 0xffffff })
        );
        temperatureIndicator.position.set(4, 1, 0);
        scene.add(temperatureIndicator);
        temperatureRef.current = temperatureIndicator;
        temperatureIndicator.userData = {

            deviceId: "sensor-001",
            type: "temperature_sensor",
            room: "meeting_room"
        };

        // Animation
        function animate() {

            requestAnimationFrame(
                animate
            );
            if (
                fanRef.current &&
                twinStateRef.current.air_conditioner
                === "ON"
            ) {

                fanRef.current.rotation.z
                    += 0.15;
            }

            controls.update();

            renderer.render(
                scene,
                camera
            );
        }
        animate();

        return () => {

            renderer.dispose();

            container.removeChild(
                renderer.domElement
            );

        };

    }, []);

    return (
        <div
            ref={containerRef}
            style={{
                width: "100%",
                height: "600px"
            }}
        />
    );
}