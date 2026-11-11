import React from 'react';
import {AbsoluteFill, Composition, Still, useCurrentFrame, useVideoConfig} from 'remotion';
import {Portada, Vox, type VideoVox} from './Vox';
import {FotoTratada, Objeto3DVista, type Objeto3D, type Paleta} from './Tres';
import demo from './data/demo.json';

// Horno: rinde aparte, con fondo transparente, lo que necesita WebGL (un objeto 3D o una foto
// tratada). El video principal solo pega esas imágenes, así que no depende de WebGL ni se frena.
export type HornoProps = {
  modo: 'objeto' | 'foto'; colores: Paleta; lado: number; alto: number; frames: number; inicio?: number;
  objeto3d: Objeto3D | null; src: string; tratamiento: string;
};
const Horno: React.FC<HornoProps> = (p) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{backgroundColor: 'transparent', alignItems: 'center', justifyContent: 'center'}}>
      {p.modo === 'objeto' && p.objeto3d
        ? <Objeto3DVista o={p.objeto3d} c={p.colores} f={frame + (p.inicio ?? 0)} fps={fps} lado={p.lado} />
        : <FotoTratada src={p.src} c={p.colores} tratamiento={p.tratamiento} anchoMax={p.lado} altoMax={p.alto} />}
    </AbsoluteFill>
  );
};
const hornoBase: HornoProps = {modo: 'objeto', colores: demo.perfil.colores, lado: 720, alto: 720, frames: 30, objeto3d: {tipo: 'caja'}, src: '', tratamiento: 'semitono'};

// Se rinde con `vox.py render`, que hornea el 3D y los tratamientos y pasa `src/data/_render.json`.
// Rendir `video.json` directo deja sin dibujar las escenas con `objeto3d` o `tratamiento`.
export const Root: React.FC = () => (
  <>
  <Composition
    id="Vox"
    component={Vox}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={demo.frames}
    defaultProps={demo as VideoVox}
    calculateMetadata={({props}) => ({durationInFrames: props.frames, fps: props.fps, width: props.ancho, height: props.alto})}
  />
  <Still id="Portada" component={Portada} width={1080} height={1920} defaultProps={demo as VideoVox} />
  <Composition
    id="Horno"
    component={Horno}
    width={720}
    height={720}
    fps={30}
    durationInFrames={30}
    defaultProps={hornoBase}
    calculateMetadata={({props}) => ({durationInFrames: Math.max(1, props.frames), width: props.lado, height: props.alto})}
  />
  </>
);
