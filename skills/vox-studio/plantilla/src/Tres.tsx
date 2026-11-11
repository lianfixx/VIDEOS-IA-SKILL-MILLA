import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {continueRender, delayRender, spring, staticFile} from 'remotion';
import * as THREE from 'three';

// 3D y sombreadores al servicio del estilo de papel: colores planos de la marca, contorno de tinta
// y luz fija. Nada de reflejos, brillos ni degradados: si se nota «render», está mal usado.
// Todo es función del cuadro (f): ningún estado depende de cuadros anteriores.

export type Paleta = {papel: string; tinta: string; acento: string; apoyo: string};
export type Objeto3D = {tipo: string; valores?: number[]; resaltar?: number};
export const OBJETOS_3D = ['moneda', 'monedas', 'barras', 'caja', 'globo'] as const;
export const TRATAMIENTOS = ['semitono', 'duotono'] as const;

const tinta = (color: string) => <meshBasicMaterial color={color} side={THREE.BackSide} />;
const plano = (color: string) => <meshToonMaterial color={color} />;

/** Malla con contorno de tinta (casco invertido): se lee como dibujo, no como plástico. */
const Pieza: React.FC<{geometria: React.ReactNode; casco?: React.ReactNode; color: string; c: Paleta; grosor?: number} & Record<string, unknown>> = ({geometria, casco, color, c, grosor = 1.06, ...resto}) => (
  <group {...resto}>
    <mesh>{geometria}{plano(color)}</mesh>
    {/* `casco`: contorno de grosor fijo para piezas alargadas, donde escalar daría un borde desigual */}
    <mesh scale={casco ? 1 : grosor}>{casco ?? geometria}{tinta(c.tinta)}</mesh>
  </group>
);

const Moneda: React.FC<{c: Paleta; y?: number; giro: number}> = ({c, y = 0, giro}) => (
  <group position={[0, y, 0]} rotation={[0, giro, 0]}>
    <Pieza c={c} color={c.apoyo} rotation={[Math.PI / 2, 0, 0]} geometria={<cylinderGeometry args={[1.5, 1.5, 0.26, 48]} />} grosor={1.05} />
    {[0.14, -0.14].map((z) => (
      <mesh key={z} position={[0, 0, z]}>
        <torusGeometry args={[1.02, 0.07, 12, 48]} />
        <meshBasicMaterial color={c.tinta} />
      </mesh>
    ))}
  </group>
);

const Escena3D: React.FC<{o: Objeto3D; c: Paleta; f: number; fps: number}> = ({o, c, f, fps}) => {
  const entra = spring({frame: f, fps, config: {damping: 13, stiffness: 150, mass: 1}});
  const valores = (o.valores && o.valores.length ? o.valores : [3, 5, 8]).slice(0, 5);
  let cuerpo: React.ReactNode = null;
  if (o.tipo === 'moneda') {
    cuerpo = <group rotation={[0.25, 0, 0.12]}><Moneda c={c} giro={f * 0.06} /></group>;
  } else if (o.tipo === 'monedas') {
    const n = Math.max(2, Math.min(8, Math.round(valores[0])));
    cuerpo = (
      <group rotation={[0.42, f * 0.012, 0]} position={[0, -n * 0.17, 0]}>
        {Array.from({length: n}).map((_, i) => {
          const cae = spring({frame: f - 4 - i * 3, fps, config: {damping: 14, stiffness: 180}});
          return (
            <group key={i} position={[Math.sin(i * 2.4) * 0.09, i * 0.34 + (1 - cae) * 6, Math.cos(i * 1.7) * 0.09]} rotation={[Math.PI / 2, 0, 0]}>
              <Pieza c={c} color={i % 2 ? c.apoyo : c.acento} geometria={<cylinderGeometry args={[1.25, 1.25, 0.26, 40]} />} grosor={1.05} rotation={[-Math.PI / 2, 0, 0]} />
            </group>
          );
        })}
      </group>
    );
  } else if (o.tipo === 'barras') {
    const max = Math.max(...valores, 1e-6);
    const paso = 1.25;
    const cabe = Math.min(1, 3.3 / (valores.length * paso)); // el conjunto nunca se sale del cuadro
    cuerpo = (
      <group scale={cabe}><group rotation={[0.28, -0.5 + Math.sin(f / 60) * 0.08, 0]} position={[-((valores.length - 1) * paso) / 2, -1.6, 0]}>
        {valores.map((v, i) => {
          const sube = spring({frame: f - 6 - i * 5, fps, config: {damping: 16, stiffness: 120}});
          const alto = Math.max(0.05, (v / max) * 3.2 * sube);
          const fuerte = i === (o.resaltar ?? valores.length - 1);
          return <Pieza key={i} c={c} color={fuerte ? c.acento : c.papel} position={[i * paso, alto / 2, 0]} geometria={<boxGeometry args={[0.85, alto, 0.85]} />} casco={<boxGeometry args={[0.95, alto + 0.1, 0.95]} />} />;
        })}
      </group></group>
    );
  } else if (o.tipo === 'caja') {
    cuerpo = <Pieza c={c} color={c.acento} rotation={[0.5, f * 0.03, 0.15]} geometria={<boxGeometry args={[2.1, 2.1, 2.1]} />} casco={<boxGeometry args={[2.22, 2.22, 2.22]} />} />;
  } else if (o.tipo === 'globo') {
    cuerpo = (
      <group rotation={[0.35, f * 0.02, 0.2]}>
        <Pieza c={c} color={c.apoyo} geometria={<sphereGeometry args={[1.7, 40, 28]} />} grosor={1.04} />
        <lineSegments>
          <edgesGeometry args={[new THREE.SphereGeometry(1.715, 12, 8)]} />
          <lineBasicMaterial color={c.tinta} />
        </lineSegments>
      </group>
    );
  }
  return (
    <>
      <ambientLight intensity={1.6} />
      <directionalLight position={[3, 5, 6]} intensity={1.4} />
      <group scale={0.25 + 0.75 * entra}>{cuerpo}</group>
    </>
  );
};

export const Objeto3DVista: React.FC<{o: Objeto3D; c: Paleta; f: number; fps: number; lado: number}> = ({o, c, f, fps, lado}) => (
  <ThreeCanvas width={lado} height={lado} style={{background: 'transparent'}} camera={{fov: 30, position: [0, 0, 8.4]}} gl={{alpha: true, antialias: true}}>
    <Escena3D o={o} c={c} f={f} fps={fps} />
  </ThreeCanvas>
);

// ---------- sombreadores: tratamiento de imprenta para fotos y recortes ----------

const VERTICE = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }';
const FRAGMENTO = `
precision highp float;
uniform sampler2D mapa; uniform vec3 tinta; uniform vec3 papel; uniform vec3 acento;
uniform vec2 tam; uniform float modo; varying vec2 vUv;
void main(){
  vec4 t = texture2D(mapa, vUv);
  // La foto se aclara antes de tramarla: una trama fiel a la luz real sale casi negra sobre papel.
  float luz = pow(clamp(dot(t.rgb, vec3(0.299, 0.587, 0.114)), 0.0, 1.0), 0.55);
  vec3 color;
  if (modo < 0.5) {            // semitono: puntos de imprenta girados 45 grados
    vec2 p = vUv * tam;
    float s = 0.70710678;
    vec2 r = vec2(p.x * s - p.y * s, p.x * s + p.y * s) / 9.0;
    float d = length(fract(r) - 0.5);
    float radio = 0.66 * sqrt(clamp(1.0 - luz, 0.0, 1.0));
    float punto = 1.0 - smoothstep(radio - 0.07, radio + 0.07, d);
    color = mix(papel, tinta, punto);
  } else {                     // duotono: sombras en tinta, medios en el acento, luces en papel
    float a = smoothstep(0.05, 0.5, luz), b = smoothstep(0.5, 0.95, luz);
    color = mix(mix(tinta, acento, a), papel, b);
  }
  gl_FragColor = vec4(color * t.a, t.a);   // respeta la transparencia del recorte
}`;

const Lamina: React.FC<{textura: THREE.Texture; c: Paleta; modo: number; ancho: number; alto: number}> = ({textura, c, modo, ancho, alto}) => {
  const uniformes = React.useMemo(() => ({
    mapa: {value: textura}, tinta: {value: new THREE.Color(c.tinta)}, papel: {value: new THREE.Color(c.papel)}, acento: {value: new THREE.Color(c.acento)},
    tam: {value: new THREE.Vector2(ancho, alto)}, modo: {value: modo},
  }), [textura, c.tinta, c.papel, c.acento, ancho, alto, modo]);
  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      <shaderMaterial vertexShader={VERTICE} fragmentShader={FRAGMENTO} uniforms={uniformes} transparent premultipliedAlpha />
    </mesh>
  );
};

/** Foto o recorte pasado por un sombreador de imprenta. Mismo tamaño que tendría la imagen normal. */
export const FotoTratada: React.FC<{src: string; c: Paleta; tratamiento: string; altoMax: number; anchoMax: number; estilo?: React.CSSProperties}> = ({src, c, tratamiento, altoMax, anchoMax, estilo}) => {
  const [textura, setTextura] = React.useState<THREE.Texture | null>(null);
  const [espera] = React.useState(() => delayRender(`textura ${src}`));
  React.useEffect(() => {
    new THREE.TextureLoader().load(staticFile(src), (t) => {
      t.colorSpace = THREE.NoColorSpace; // se trabaja con los valores tal cual: los colores de marca no deben convertirse
      t.minFilter = THREE.LinearFilter;
      setTextura(t);
      continueRender(espera);
    }, undefined, () => continueRender(espera));
  }, [src, espera]);
  if (!textura) return null;
  const img = textura.image as {width: number; height: number};
  const k = Math.min(anchoMax / img.width, altoMax / img.height);
  const ancho = Math.round(img.width * k), alto = Math.round(img.height * k);
  return (
    <div style={{width: ancho, height: alto, ...estilo}}>
      <ThreeCanvas width={ancho} height={alto} orthographic camera={{left: -1, right: 1, top: 1, bottom: -1, near: 0, far: 2, position: [0, 0, 1]}} gl={{alpha: true, premultipliedAlpha: true}} style={{background: 'transparent'}} flat linear>
        <Lamina textura={textura} c={c} modo={tratamiento === 'duotono' ? 1 : 0} ancho={ancho} alto={alto} />
      </ThreeCanvas>
    </div>
  );
};
