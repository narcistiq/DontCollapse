"use client";

import { Environment, Float } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { geoEquirectangular, geoPath } from "d3-geo";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { feature, mesh } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import usAtlas from "us-atlas/states-10m.json";
import worldAtlas from "world-atlas/countries-110m.json";
import { useEffect, useMemo, useRef } from "react";
import { AdditiveBlending, BackSide, CanvasTexture, SRGBColorSpace, Vector3 } from "three";
import type { Group, Mesh, MeshBasicMaterial, MeshStandardMaterial, PointLight } from "three";

gsap.registerPlugin(ScrollTrigger);

const GLOBE_RADIUS = 1.35;

type AnimState = {
  rotationX: number;
  rotationY: number;
  positionX: number;
  positionY: number;
  positionZ: number;
  scale: number;
  glowIntensity: number;
  globeOpacity: number;
  infraReveal: number;
  popupProgress: number;
  spinSpeed: number;
};

function latLonToVector(lat: number, lon: number, radius = GLOBE_RADIUS + 0.02) {
  const phi = ((90 - lat) * Math.PI) / 180;
  const theta = ((lon + 180) * Math.PI) / 180;

  return new Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

function buildEarthTextures(detail: "base" | "high" = "base") {
  const width = detail === "high" ? 4096 : 2048;
  const height = width / 2;

  const colorCanvas = document.createElement("canvas");
  colorCanvas.width = width;
  colorCanvas.height = height;
  const colorCtx = colorCanvas.getContext("2d");

  const nightCanvas = document.createElement("canvas");
  nightCanvas.width = width;
  nightCanvas.height = height;
  const nightCtx = nightCanvas.getContext("2d");

  if (!colorCtx || !nightCtx) {
    return { colorTexture: null, nightTexture: null };
  }

  const projection = geoEquirectangular().scale(width / (2 * Math.PI)).translate([width / 2, height / 2]);
  const path = geoPath(projection, colorCtx);
  const nightPath = geoPath(projection, nightCtx);

  const ocean = colorCtx.createLinearGradient(0, 0, width, height);
  ocean.addColorStop(0, "#0a2352");
  ocean.addColorStop(0.45, "#0f3f86");
  ocean.addColorStop(1, "#071a3f");
  colorCtx.fillStyle = ocean;
  colorCtx.fillRect(0, 0, width, height);

  const world = worldAtlas as unknown as Topology<{ countries: GeometryCollection }>;
  const us = usAtlas as unknown as Topology<{ states: GeometryCollection }>;

  const worldGeo = feature(world, world.objects.countries);
  const countryBorders = mesh(world, world.objects.countries, (a, b) => a !== b);

  colorCtx.save();
  colorCtx.fillStyle = "#3e6f4a";
  colorCtx.strokeStyle = "rgba(9, 29, 45, 0.95)";
  colorCtx.lineWidth = 0.65;
  path(worldGeo as never);
  colorCtx.fill();
  path(countryBorders as never);
  colorCtx.stroke();
  colorCtx.restore();

  const usStatesGeo = feature(us, us.objects.states);
  const florida = {
    ...usStatesGeo,
    features: usStatesGeo.features.filter((f) => Number(f.id) === 12)
  };

  colorCtx.save();
  colorCtx.strokeStyle = "rgba(120, 168, 220, 0.55)";
  colorCtx.lineWidth = 1;
  path(usStatesGeo as never);
  colorCtx.stroke();
  colorCtx.restore();

  if (detail === "high") {
    colorCtx.save();
    colorCtx.fillStyle = "rgba(34, 224, 112, 1)";
    colorCtx.strokeStyle = "rgba(210, 255, 229, 1)";
    colorCtx.lineWidth = 2;
    path(florida as never);
    colorCtx.fill();
    colorCtx.stroke();
    colorCtx.restore();
  }

  nightCtx.fillStyle = "#030712";
  nightCtx.fillRect(0, 0, width, height);

  if (detail === "high") {
    nightCtx.save();
    nightCtx.fillStyle = "rgba(54, 255, 139, 0.98)";
    nightCtx.strokeStyle = "rgba(188, 255, 214, 1)";
    nightCtx.lineWidth = 3.2;
    nightPath(florida as never);
    nightCtx.fill();
    nightCtx.stroke();
    nightCtx.restore();
  }

  const colorTexture = new CanvasTexture(colorCanvas);
  colorTexture.colorSpace = SRGBColorSpace;
  const nightTexture = new CanvasTexture(nightCanvas);
  nightTexture.colorSpace = SRGBColorSpace;

  return { colorTexture, nightTexture };
}

export function ResilienceModel() {
  const groupRef = useRef<Group>(null);
  const globeRef = useRef<Mesh>(null);
  const atmosphereRef = useRef<Mesh>(null);
  const floridaGlowRef = useRef<PointLight>(null);
  const keyLightRef = useRef<PointLight>(null);
  const globeMaterialRef = useRef<MeshStandardMaterial>(null);
  const detailMaterialRef = useRef<MeshStandardMaterial>(null);
  const infraGroupRef = useRef<Group>(null);
  const infraMarkerRefs = useRef<Array<Group | null>>([]);

  const earthTextures = useMemo(() => buildEarthTextures("base"), []);
  const earthDetailTextures = useMemo(() => buildEarthTextures("high"), []);

  const animationState = useRef<AnimState>({
    rotationX: 0.12,
    rotationY: -1.05,
    positionX: 0,
    positionY: 0,
    positionZ: 0,
    scale: 0.88,
    glowIntensity: 0.8,
    globeOpacity: 0.2,
    infraReveal: 0,
    popupProgress: 0,
    spinSpeed: 0.08
  });

  const infrastructureZones = [
    { lat: 27.95, lon: -82.46, color: "#22c55e", w: 0.018, h: 0.012, d: 0.014, label: "roads" },
    { lat: 28.04, lon: -82.61, color: "#22c55e", w: 0.016, h: 0.01, d: 0.013, label: "intersections" },
    { lat: 27.9, lon: -82.38, color: "#22c55e", w: 0.017, h: 0.011, d: 0.013, label: "drainage" },
    { lat: 27.82, lon: -82.52, color: "#22c55e", w: 0.016, h: 0.01, d: 0.013, label: "access" }
  ];

  const { floridaRotationX, floridaRotationY } = useMemo(() => {
    const floridaFocus = latLonToVector(27.95, -82.46, GLOBE_RADIUS);
    return {
      floridaRotationY: Math.PI * 4 + Math.atan2(-floridaFocus.x, floridaFocus.z),
      floridaRotationX: Math.atan2(floridaFocus.y, Math.sqrt(floridaFocus.x ** 2 + floridaFocus.z ** 2))
    };
  }, []);

  useEffect(() => {
    const timeline = gsap.timeline({
      scrollTrigger: {
        trigger: "#landing-root",
        start: "top top",
        end: "bottom bottom",
        scrub: 1.8
      }
    });

    timeline
      .to(animationState.current, {
        globeOpacity: 1,
        scale: 1.02,
        rotationY: Math.PI * 1.55,
        duration: 1.35,
        ease: "power2.out"
      })
      .to(
        animationState.current,
        {
          rotationY: Math.PI * 3.1,
          positionX: 1.75,
          positionY: 0.1,
          glowIntensity: 2.1,
          spinSpeed: 0.18,
          duration: 1.25,
          ease: "power3.inOut"
        },
        ">"
      )
      .to(
        animationState.current,
        {
          rotationY: floridaRotationY + 0.45,
          positionX: 0.65,
          positionY: 0.08,
          scale: 1.6,
          spinSpeed: 0.09,
          duration: 1,
          ease: "power2.inOut"
        },
        ">"
      )
      .to(
        animationState.current,
        {
          scale: 2.45,
          positionX: 0,
          positionY: 0.06,
          positionZ: 1.12,
          rotationX: floridaRotationX,
          rotationY: floridaRotationY,
          infraReveal: 1,
          popupProgress: 1,
          spinSpeed: 0.001,
          duration: 2.5,
          ease: "power4.inOut"
        },
        ">"
      )
      .to(
        animationState.current,
        {
          scale: 2.42,
          positionX: 0,
          positionY: 0.06,
          positionZ: 1.1,
          rotationX: floridaRotationX,
          rotationY: floridaRotationY,
          infraReveal: 1,
          popupProgress: 1,
          spinSpeed: 0,
          glowIntensity: 1.7,
          duration: 3.2,
          ease: "none"
        },
        ">"
      );

    return () => {
      timeline.kill();
    };
  }, [floridaRotationX, floridaRotationY]);

  useFrame((_, delta) => {
    const group = groupRef.current;
    if (!group) {
      return;
    }

    group.rotation.x += (animationState.current.rotationX - group.rotation.x) * 4 * delta;
    group.rotation.y += (animationState.current.rotationY - group.rotation.y) * 4 * delta;

    group.position.x += (animationState.current.positionX - group.position.x) * 4 * delta;
    group.position.y += (animationState.current.positionY - group.position.y) * 4 * delta;
    group.position.z += (animationState.current.positionZ - group.position.z) * 4 * delta;

    group.scale.x += (animationState.current.scale - group.scale.x) * 4 * delta;
    group.scale.y += (animationState.current.scale - group.scale.y) * 4 * delta;
    group.scale.z += (animationState.current.scale - group.scale.z) * 4 * delta;

    group.rotation.y += animationState.current.spinSpeed * delta;

    if (globeMaterialRef.current) {
      globeMaterialRef.current.opacity += (animationState.current.globeOpacity - globeMaterialRef.current.opacity) * 3 * delta;
    }

    if (detailMaterialRef.current) {
      const detailOpacity = animationState.current.globeOpacity * animationState.current.infraReveal * 0.95;
      detailMaterialRef.current.opacity += (detailOpacity - detailMaterialRef.current.opacity) * 5 * delta;
    }

    if (keyLightRef.current) {
      keyLightRef.current.intensity += (animationState.current.glowIntensity - keyLightRef.current.intensity) * 3 * delta;
    }

    if (floridaGlowRef.current) {
      const pulse = 1 + Math.sin(performance.now() / 170) * 0.14 * animationState.current.infraReveal;
      const target = (0.7 + animationState.current.infraReveal * 6.2) * pulse;
      floridaGlowRef.current.intensity += (target - floridaGlowRef.current.intensity) * 4 * delta;
    }

    if (infraGroupRef.current) {
      const targetScale = 0.001 + animationState.current.infraReveal * 0.75;
      infraGroupRef.current.scale.x += (targetScale - infraGroupRef.current.scale.x) * 5 * delta;
      infraGroupRef.current.scale.y += (targetScale - infraGroupRef.current.scale.y) * 5 * delta;
      infraGroupRef.current.scale.z += (targetScale - infraGroupRef.current.scale.z) * 5 * delta;
    }

    for (let i = 0; i < infraMarkerRefs.current.length; i += 1) {
      const marker = infraMarkerRefs.current[i];
      if (!marker) {
        continue;
      }

      const delay = i * 0.12;
      const t = Math.max(0, Math.min(1, (animationState.current.popupProgress - delay) / (1 - delay)));
      const pulse = 1 + Math.sin((performance.now() / 180) + i) * 0.06 * t;
      const targetY = Math.max(0.001, t * pulse * 0.9);

      marker.scale.y += (targetY - marker.scale.y) * 8 * delta;
      marker.scale.x += (Math.max(0.001, t) - marker.scale.x) * 8 * delta;
      marker.scale.z += (Math.max(0.001, t) - marker.scale.z) * 8 * delta;
    }

    if (atmosphereRef.current) {
      const material = atmosphereRef.current.material as MeshBasicMaterial;
      material.opacity += (0.14 * animationState.current.globeOpacity - material.opacity) * 3 * delta;
    }
  });

  return (
    <>
      <ambientLight intensity={0.25} />
      <directionalLight position={[4.8, 5.2, 2.6]} intensity={2.35} color="#cfe5ff" />
      <directionalLight position={[-4.4, 2.1, -2.7]} intensity={1.05} color="#8ed6ff" />
      <pointLight position={[0.35, 1, 2.5]} intensity={1.55} color="#ffffff" />
      <pointLight position={[-1.4, -0.6, 2.1]} intensity={0.75} color="#9ed0ff" />
      <pointLight ref={keyLightRef} position={[0, -2, 2]} intensity={0.8} color="#60a5fa" />
      <pointLight ref={floridaGlowRef} position={[-0.24, 0.35, 1.74]} intensity={1.1} color="#43ff96" />

      <Float speed={0.9} rotationIntensity={0.14} floatIntensity={0.25}>
        <group ref={groupRef}>
          <mesh ref={globeRef} castShadow receiveShadow>
            <sphereGeometry args={[GLOBE_RADIUS, 160, 160]} />
            <meshStandardMaterial
              ref={globeMaterialRef}
              map={earthTextures.colorTexture ?? undefined}
              emissiveMap={earthTextures.nightTexture ?? undefined}
              emissive="#7aaee3"
              emissiveIntensity={0.82}
              roughness={0.92}
              metalness={0.03}
              transparent
              opacity={0.2}
            />
          </mesh>

          <mesh>
            <sphereGeometry args={[GLOBE_RADIUS + 0.003, 196, 196]} />
            <meshStandardMaterial
              ref={detailMaterialRef}
              map={earthDetailTextures.colorTexture ?? undefined}
              emissiveMap={earthDetailTextures.nightTexture ?? undefined}
              emissive="#6df2a1"
              emissiveIntensity={1.05}
              roughness={0.9}
              metalness={0.02}
              transparent
              opacity={0}
              depthWrite={false}
            />
          </mesh>

          <mesh ref={atmosphereRef}>
            <sphereGeometry args={[GLOBE_RADIUS + 0.04, 96, 96]} />
            <meshBasicMaterial
              color="#f5fbff"
              transparent
              opacity={0.02}
              blending={AdditiveBlending}
              side={BackSide}
              depthWrite={false}
            />
          </mesh>

          <group ref={infraGroupRef} scale={[0.001, 0.001, 0.001]}>
            {infrastructureZones.map((zone, idx) => {
              const p = latLonToVector(zone.lat, zone.lon, GLOBE_RADIUS + 0.05);
              return (
                <group
                  key={`zone-${zone.label}`}
                  ref={(node) => {
                    infraMarkerRefs.current[idx] = node;
                  }}
                  position={p}
                  rotation={[0.25, 0.12, 0.08]}
                  scale={[0.001, 0.001, 0.001]}
                >
                  <mesh position={[0, 0, 0]}>
                    <boxGeometry args={[zone.w, zone.h, zone.d]} />
                    <meshStandardMaterial color={zone.color} emissive={zone.color} emissiveIntensity={0.75} transparent opacity={0.85} />
                  </mesh>
                  <mesh position={[0, zone.h * 0.55, 0]}>
                    <boxGeometry args={[zone.w * 0.65, zone.h * 0.75, zone.d * 0.65]} />
                    <meshStandardMaterial color={zone.color} emissive={zone.color} emissiveIntensity={0.85} transparent opacity={0.9} />
                  </mesh>
                  <mesh position={[0, zone.h * 1.05, 0]}>
                    <boxGeometry args={[zone.w * 0.35, zone.h * 0.55, zone.d * 0.35]} />
                    <meshStandardMaterial color={zone.color} emissive={zone.color} emissiveIntensity={0.95} transparent opacity={0.95} />
                  </mesh>
                </group>
              );
            })}
          </group>
        </group>
      </Float>

      <Environment preset="night" />
    </>
  );
}
