import React from 'react';
import {AbsoluteFill, Img, interpolateColors, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {frameOf, validateManifest} from './manifest-validation.mjs';
import type {Diagram, Manifest, Scene} from './types';

const C = {ivory: '#F6F0E4', navy: '#172636', gold: '#D6A72C'};
const clamp = (n: number) => Math.min(1, Math.max(0, n));
const smooth = (n: number) => {const p = clamp(n); return p * p * (3 - 2 * p);};
const byId = (m: Manifest, id: string) => {
  const asset = m.assets.find((a) => a.id === id);
  if (!asset) throw new Error(`Asset no encontrado: ${id}`);
  return staticFile(asset.path);
};

function entrance(family: Scene['transition']['family'], progress: number): React.CSSProperties {
  const p = smooth(progress);
  switch (family) {
    case 'wipe': return {clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`};
    case 'push': return {transform: `translateX(${(1 - p) * 1080}px)`};
    case 'mask': return {clipPath: `inset(${(1 - p) * 100}% 0 0 0)`};
    case 'depth': return {opacity: p, transform: `perspective(1800px) translateZ(${(1 - p) * -180}px) rotateY(${(1 - p) * -8}deg)`};
    case 'pan': return {opacity: p, transform: `translateY(${(1 - p) * 110}px)`};
    case 'zoom': return {opacity: p, transform: `scale(${1.06 - p * 0.06})`};
    case 'fade': return {opacity: p};
  }
}

function NativeDiagram({diagram, age, dark, id}: {diagram: Diagram; age: number; dark: boolean; id: string}) {
  const nodes = new Map(diagram.nodes.map((n) => [n.id, n]));
  const color = dark ? C.ivory : C.navy;
  const markerId = `arrow-${id.replace(/[^a-zA-Z0-9_-]/g, '')}`;
  return <svg viewBox="0 0 840 480" width="100%" height="100%" role="img" aria-label="Diagrama de relaciones">
    <defs><marker id={markerId} markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="none" stroke={C.gold} strokeWidth="1.7" /></marker></defs>
    {diagram.edges.map((edge, i) => {
      const a = nodes.get(edge.from)!; const b = nodes.get(edge.to)!;
      const ax = a.x * 8.4; const ay = a.y * 4.8; const bx = b.x * 8.4; const by = b.y * 4.8;
      const dx = bx - ax; const dy = by - ay;
      const bound = Math.min(104 / Math.max(Math.abs(dx), 0.001), 48 / Math.max(Math.abs(dy), 0.001));
      const x1 = ax + dx * bound; const y1 = ay + dy * bound;
      const x2 = bx - dx * bound; const y2 = by - dy * bound;
      const p = smooth((age - 8 - i * 3) / 18);
      return <g key={`${edge.from}-${edge.to}-${i}`} opacity={p}>
        <path d={`M ${x1},${y1} L ${x2},${y2}`} pathLength="1" stroke={C.gold} strokeWidth="3" fill="none" strokeDasharray="1" strokeDashoffset={1 - p} markerEnd={`url(#${markerId})`} />
        {edge.label && <text x={(ax + bx) / 2} y={(ay + by) / 2 - 15} textAnchor="middle" fill={color} fontSize="22" fontWeight="700" paintOrder="stroke" stroke={dark ? C.navy : C.ivory} strokeWidth="8">{edge.label}</text>}
      </g>;
    })}
    {diagram.nodes.map((node, i) => {
      const p = smooth((age - i * 3) / 16);
      const words = node.label.split(' '); const lines: string[] = [''];
      for (const word of words) {
        if ((lines[lines.length - 1] + ' ' + word).trim().length > 15 && lines[lines.length - 1]) lines.push(word);
        else lines[lines.length - 1] = `${lines[lines.length - 1]} ${word}`.trim();
      }
      return <g key={node.id} opacity={p} transform={`translate(${node.x * 8.4},${node.y * 4.8 + (1 - p) * 12})`}>
        <rect x="-103" y="-47" width="206" height="94" rx="9" fill={dark ? C.navy : C.ivory} stroke={color} strokeOpacity="0.38" strokeWidth="2" />
        {lines.map((line, n) => <text key={n} x="0" y={(n - (lines.length - 1) / 2) * 26 + 8} fill={color} fontSize="24" fontWeight="700" textAnchor="middle">{line}</text>)}
      </g>;
    })}
  </svg>;
}

function SceneLayer({scene, manifest, index, start, end, overlap, frame}: {scene: Scene; manifest: Manifest; index: number; start: number; end: number; overlap: number; frame: number}) {
  const age = frame - start;
  const dark = scene.theme === 'navy';
  const ink = dark ? C.ivory : C.navy;
  const p = overlap ? clamp(age / (overlap - 1)) : 1;
  // Continues gently after entrance. No random/time-dependent state or particles.
  const travel = (age / Math.max(1, end - start - 1));
  const images = scene.asset_ids;
  return <AbsoluteFill style={{backgroundColor: dark ? C.navy : C.ivory, color: ink, overflow: 'hidden', ...entrance(scene.transition.family, p)}}>
    <div style={{position: 'absolute', left: 120, right: 150, top: 364}}>
      <div style={{fontSize: 25, fontWeight: 700, letterSpacing: 4, marginBottom: 22, color: dark ? C.gold : C.navy}}>{scene.kicker ?? `${String(index + 1).padStart(2, '0')} / ${String(manifest.scenes.length).padStart(2, '0')}`}</div>
      <div style={{fontSize: scene.title.length > 48 ? 66 : 76, lineHeight: 1.08, fontWeight: 800, letterSpacing: -2.2, textWrap: 'balance', textShadow: dark ? '0 4px 0 rgba(0,0,0,0.18)' : '0 4px 0 rgba(23,38,54,0.09)'}}>{scene.title}</div>
      <div style={{marginTop: 30, width: 90 + 36 * smooth(age / 24), height: 5, backgroundColor: C.gold}} />
    </div>
    {images.length > 0 && <div style={{position: 'absolute', left: 120, right: 150, top: 720, height: scene.diagram ? 540 : 760, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 20, transform: `translateY(${-8 * travel}px)`}}>
      {images.map((id, i) => <Img key={id} src={byId(manifest, id)} style={{objectFit: 'contain', objectPosition: 'center', width: `${100 / images.length}%`, minWidth: 0, height: '100%', transform: `perspective(1800px) translateY(${Math.sin((age + i * 12) / 70) * 4}px) scale(${0.97 + travel * 0.02})`, filter: 'drop-shadow(0 20px 16px rgba(23,38,54,0.12))'}} />)}
    </div>}
    {scene.diagram && <div style={{position: 'absolute', left: 120, right: 150, top: images.length ? 1260 : 755, height: images.length ? 380 : 600}}>
      <NativeDiagram diagram={scene.diagram} age={age} dark={dark} id={scene.id} />
    </div>}
    {scene.body && <div style={{position: 'absolute', left: 120, right: 150, top: 1530, fontSize: 35, lineHeight: 1.34, fontWeight: 500}}>{scene.body}</div>}
  </AbsoluteFill>;
}

export const MillaVideo: React.FC<Manifest> = (manifest) => {
  const frame = useCurrentFrame();
  const {durationInFrames, fps} = useVideoConfig();
  const timeline = React.useMemo(() => validateManifest(manifest), [manifest]);
  const cue = manifest.subtitleCues?.find((c) => frame >= frameOf(c.start, fps) && frame < frameOf(c.end, fps));
  const topSceneIndex = timeline.scenes.findLastIndex((s: {start: number; end: number}) => frame >= s.start && frame < s.end);
  const currentIndex = Math.max(0, topSceneIndex);
  const dark = manifest.scenes[currentIndex]?.theme === 'navy';
  const previousDark = manifest.scenes[Math.max(0, currentIndex - 1)]?.theme === 'navy';
  const timing = timeline.scenes[currentIndex];
  const brandProgress = timing.overlap ? smooth((frame - timing.start) / Math.max(1, timing.overlap - 1)) : 1;
  const brandInk = interpolateColors(brandProgress, [0, 1], [previousDark ? C.ivory : C.navy, dark ? C.ivory : C.navy]);
  const audio = manifest.audio;
  const musicEnvelope = (f: number) => Math.min(clamp(f / 15), clamp((durationInFrames - 1 - f) / 30));
  return <AbsoluteFill style={{background: C.ivory, fontFamily: 'Arial, Helvetica, sans-serif'}}>
    {manifest.scenes.map((scene, i) => {
      const timing = timeline.scenes[i];
      if (frame < timing.start || frame >= timing.end) return null;
      return <SceneLayer key={scene.id} scene={scene} manifest={manifest} index={i} {...timing} frame={frame} />;
    })}
    <div style={{position: 'absolute', top: 105, left: 120, right: 150, color: brandInk, fontSize: 25, fontWeight: 800, letterSpacing: 5}}>{manifest.branding?.name ?? 'MILLA ABOGADOS'}</div>
    {cue && <div style={{position: 'absolute', top: 183, left: 120, right: 150, minHeight: 118, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', fontSize: 36, lineHeight: 1.18, fontWeight: 700, color: C.ivory, background: C.navy, padding: '16px 24px', borderRadius: 10}}>
      <div>{cue.words ? cue.words.map((word, i) => {
        const active = frame >= frameOf(word.start, fps) && frame < frameOf(word.end, fps);
        return <React.Fragment key={`${word.start}-${i}`}><span style={{color: active ? C.gold : C.ivory}}>{word.text}</span>{i < cue.words!.length - 1 ? ' ' : ''}</React.Fragment>;
      }) : cue.text}</div>
    </div>}
    {manifest.branding?.footer && <div style={{position: 'absolute', left: 120, right: 150, bottom: 170, color: brandInk, fontSize: 26, letterSpacing: 1, fontWeight: 600}}>{manifest.branding.footer}</div>}
    {audio?.voice && <Audio src={byId(manifest, audio.voice)} volume={audio.voiceVolume ?? 1} />}
    {audio?.music && <Audio src={byId(manifest, audio.music)} volume={(f) => (audio.musicVolume ?? 0.14) * musicEnvelope(f)} />}
    {audio?.sfx?.map((effect, i) => <Audio key={`${effect.asset_id}-${i}`} src={byId(manifest, effect.asset_id)} from={frameOf(effect.start, fps)} durationInFrames={effect.duration == null ? undefined : frameOf(effect.duration, fps)} volume={effect.volume ?? 0.25} />)}
  </AbsoluteFill>;
};
