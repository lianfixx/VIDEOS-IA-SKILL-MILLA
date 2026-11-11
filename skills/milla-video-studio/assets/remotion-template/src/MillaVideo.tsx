import React from 'react';
import {AbsoluteFill, Img, interpolateColors, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {frameOf, validateManifest} from './manifest-validation.mjs';
import type {Beat, Diagram, Manifest, Scene} from './types';

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

// ---- Planos (beats): piezas dibujadas con código que entran con la voz. Sin partículas ni anillos; solo marfil, azul y dorado.
type Tone = {ink: string; paper: string; dark: boolean};
const grow = (frame: number, from: number, length: number) => smooth((frame - from) / length);
/** Cuadro en que entra la pieza k de un plano: su `at` real o, sin él, a ritmo fijo tras el plano. */
const pieceFrame = (at: number | undefined, beatFrame: number, k: number, step: number, fps: number) => at == null ? beatFrame + 8 + step * k : frameOf(at, fps);

function QuoteBeat({beat, t, tone}: {beat: Extract<Beat, {kind: 'quote'}>; t: number; tone: Tone}) {
  const cut = beat.highlight ? beat.text.indexOf(beat.highlight) : -1;
  const size = beat.text.length <= 80 ? 46 : beat.text.length <= 120 ? 41 : 37;
  const drawn = clamp((t - 12) / Math.max(14, (beat.highlight?.length ?? 0) * 0.7));
  return <div style={{width: '100%', background: tone.dark ? '#1F3145' : '#FFFDF7', borderLeft: `12px solid ${C.gold}`, padding: '34px 40px 38px', boxShadow: '0 18px 0 rgba(23,38,54,0.10)'}}>
    <div style={{display: 'inline-block', fontSize: 25, fontWeight: 800, letterSpacing: 3, textTransform: 'uppercase', color: C.navy, background: C.gold, padding: '5px 14px', marginBottom: 20}}>{beat.source}</div>
    <div style={{fontSize: size, lineHeight: 1.34, fontWeight: 600, fontFamily: 'Georgia, "Times New Roman", serif'}}>
      «{cut < 0 ? beat.text : beat.text.slice(0, cut)}
      {cut >= 0 && <span style={{backgroundImage: `linear-gradient(${C.gold}88, ${C.gold}88)`, backgroundRepeat: 'no-repeat', backgroundSize: `${drawn * 100}% 84%`, backgroundPosition: '0 60%'}}>{beat.highlight}</span>}
      {cut >= 0 && beat.text.slice(cut + beat.highlight!.length)}»
    </div>
  </div>;
}

function ListBeat({beat, frame, at, fps, tone, height}: {beat: Extract<Beat, {kind: 'list'}>; frame: number; at: number; fps: number; tone: Tone; height: number}) {
  const row = Math.min(132, height / beat.items.length);
  return <div style={{width: '100%'}}>
    {beat.items.map((item, k) => {
      const t = frame - pieceFrame(item.at, at, k, 9, fps);
      if (t < 0) return <div key={k} style={{height: row}} />;
      const p = grow(t, 0, 8); const draw = clamp((t - 5) / 7); const no = item.mark === 'no';
      return <div key={k} style={{height: row, display: 'flex', alignItems: 'center', gap: 28, opacity: p, transform: `translateX(${(1 - p) * -60}px)`}}>
        <div style={{flex: 'none', width: row * 0.6, height: row * 0.6, border: `6px solid ${tone.ink}`, background: item.mark === 'yes' ? C.gold : 'transparent'}}>
          <svg viewBox="0 0 40 40" width="100%" height="100%">
            {item.mark === 'yes' && draw > 0 && <path d="M8 21 l9 9 l16 -20" fill="none" stroke={C.navy} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />}
            {no && draw > 0 && <path d="M9 9 L31 31 M31 9 L9 31" fill="none" stroke={tone.ink} strokeWidth={6} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />}
          </svg>
        </div>
        <div style={{position: 'relative', fontSize: Math.min(row * 0.46, 62), fontWeight: 800, letterSpacing: -0.5, whiteSpace: 'nowrap'}}>
          {item.text}
          {no && <div style={{position: 'absolute', left: -6, top: '52%', height: 7, width: `${draw * 104}%`, background: C.gold}} />}
        </div>
      </div>;
    })}
  </div>;
}

function CalendarBeat({beat, t, span, tone, height}: {beat: Extract<Beat, {kind: 'calendar'}>; t: number; span: number; tone: Tone; height: number}) {
  const cells = beat.cells ?? Array.from({length: beat.days ?? 0}, (_, n) => ({label: String(n + 1), state: 'crossed' as const}));
  const cols = cells.length <= 7 ? cells.length : 5; const rows = Math.ceil(cells.length / cols);
  const foot = beat.caption ? 76 : 0;
  const side = Math.min(770 / cols - 14, (height - foot - 20) / rows - 14, 170);
  const step = Math.min(6, Math.max(0.6, (span - 34) / Math.max(1, cells.length)));
  return <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
    <div style={{display: 'grid', gridTemplateColumns: `repeat(${cols}, ${side}px)`, gap: 14}}>
      {cells.map((cell, n) => {
        const tt = t - 10 - n * step; const draw = clamp(tt / 5); const on = cell.state === 'marked' && tt >= 0;
        return <div key={n} style={{position: 'relative', width: side, height: side, border: `4px solid ${tone.ink}`, background: on ? C.gold : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${on ? 1 + 0.12 * Math.sin(Math.PI * clamp(tt / 10)) : 1})`}}>
          <span style={{position: 'relative', zIndex: 1, fontSize: side * 0.44, fontWeight: 800, color: on ? C.navy : tone.ink}}>{cell.label}</span>
          {cell.state === 'crossed' && draw > 0 && <svg viewBox="0 0 40 40" width="100%" height="100%" style={{position: 'absolute', inset: 0}}><path d="M6 7 L34 33 M34 7 L6 33" fill="none" stroke={C.gold} strokeWidth={4} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} /></svg>}
        </div>;
      })}
    </div>
    {beat.caption && <div style={{marginTop: 22, fontSize: 36, fontWeight: 600, fontStyle: 'italic'}}>{beat.caption}</div>}
  </div>;
}

function FigureBeat({beat, t, tone, height}: {beat: Extract<Beat, {kind: 'figure'}>; t: number; tone: Tone; height: number}) {
  const m = /^(\D*)(\d+)(\D*)$/.exec(beat.value);
  const up = clamp((t - 3) / 14);
  const shown = m ? `${m[1]}${String(Math.round(Number(m[2]) * up)).padStart(up < 1 ? 1 : m[2].length, '0')}${m[3]}` : beat.value;
  const strike = clamp((t - 20) / 7);
  const size = Math.min((height - (beat.caption ? 120 : 20)) * 0.62, 900 / Math.max(2, beat.value.length));
  return <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
    <div style={{position: 'relative', fontSize: size, lineHeight: 1.05, fontWeight: 800, letterSpacing: -4, fontVariantNumeric: 'tabular-nums', color: tone.ink}}>
      {shown}
      {beat.strike && strike > 0 && <div style={{position: 'absolute', left: '-6%', top: '50%', width: `${strike * 112}%`, height: Math.max(12, size * 0.09), background: C.gold, transform: 'rotate(-8deg)', transformOrigin: 'left center'}} />}
    </div>
    <div style={{width: 120 + 60 * smooth(t / 20), height: 6, background: C.gold, marginTop: 6}} />
    {beat.caption && <div style={{marginTop: 22, fontSize: 40, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase'}}>{beat.caption}</div>}
  </div>;
}

function TimelineBeat({beat, frame, at, fps, tone, height}: {beat: Extract<Beat, {kind: 'timeline'}>; frame: number; at: number; fps: number; tone: Tone; height: number}) {
  const row = Math.min(190, height / beat.milestones.length);
  const frames = beat.milestones.map((m, k) => pieceFrame(m.at, at, k, 16, fps));
  const reach = frames.reduce((sum, f, k) => (k === 0 ? 0 : sum + clamp((frame - (f - 9)) / 9)), 0);
  return <div style={{position: 'relative', width: '100%', height: row * beat.milestones.length}}>
    <div style={{position: 'absolute', left: 27, top: row * 0.5, width: 8, height: row * (beat.milestones.length - 1), background: `${tone.ink}22`}} />
    <div style={{position: 'absolute', left: 27, top: row * 0.5, width: 8, height: row * reach, background: C.gold}} />
    {beat.milestones.map((m, k) => {
      const t = frame - frames[k];
      if (t < 0) return null;
      const p = grow(t, 0, 8);
      return <div key={k} style={{position: 'absolute', left: 0, top: row * k, height: row, width: '100%', display: 'flex', alignItems: 'center', gap: 30}}>
        <div style={{flex: 'none', width: 62, height: 62, borderRadius: '50%', background: k === beat.milestones.length - 1 ? C.gold : tone.paper, border: `8px solid ${tone.ink}`, transform: `scale(${0.6 + 0.4 * p})`}} />
        <div style={{opacity: p, transform: `translateX(${(1 - p) * 40}px)`}}>
          <div style={{display: 'inline-block', fontSize: Math.min(40, row * 0.24), fontWeight: 800, letterSpacing: 2, color: C.navy, background: C.gold, padding: '4px 14px'}}>{m.date}</div>
          <div style={{fontSize: Math.min(44, row * 0.26), lineHeight: 1.15, fontWeight: 700, marginTop: 8}}>{m.text}</div>
        </div>
      </div>;
    })}
  </div>;
}

function BarsBeat({beat, frame, at, fps, tone, height}: {beat: Extract<Beat, {kind: 'bars'}>; frame: number; at: number; fps: number; tone: Tone; height: number}) {
  const max = Math.max(...beat.bars.map((b) => b.value));
  const row = Math.min(210, (height - 70) / beat.bars.length);
  const figure = row * 0.36;
  const written = (b: {value: number; text?: string}) => b.text || String(b.value);
  const decimals = (v: number) => (String(v).split('.')[1] ?? '').length;
  // Sitio fijo para la cifra más larga: la barra nunca se encoge y la proporción dibujada es la de los datos.
  const track = Math.max(120, 810 - Math.max(...beat.bars.map((b) => written(b).length)) * figure * 0.6 - 40);
  return <div style={{width: '100%'}}>
    {beat.bars.map((b, k) => {
      const t = frame - pieceFrame(b.at, at, k, 10, fps);
      if (t < 0) return <div key={k} style={{height: row}} />;
      const up = smooth(t / 24);
      return <div key={k} style={{height: row}}>
        <div style={{fontSize: Math.min(40, row * 0.24), fontWeight: 800, letterSpacing: 1, textTransform: 'uppercase'}}>{b.label}</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 8}}>
          <div style={{flex: 'none', width: Math.max(6, (b.value / max) * track * up), height: figure, background: b.value === max ? C.gold : tone.ink}} />
          <div style={{flex: 'none', fontSize: figure, fontWeight: 800, whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums'}}>{b.text ? (up > 0.6 ? b.text : '') : up >= 1 ? String(b.value) : (b.value * up).toFixed(decimals(b.value))}</div>
        </div>
      </div>;
    })}
    <div style={{fontSize: 28, fontStyle: 'italic', fontWeight: 500, marginTop: 4}}>Fuente: {beat.source}</div>
  </div>;
}

function Beats({scene, manifest, start, end, frame, fps, tone}: {scene: Scene; manifest: Manifest; start: number; end: number; frame: number; fps: number; tone: Tone}) {
  const beats = scene.beats ?? [];
  const height = 600;
  return <div style={{position: 'absolute', left: 120, right: 150, top: 755, height}}>
    {beats.map((beat, n) => {
      const at = n === 0 ? Math.min(start, frameOf(beat.at, fps)) : frameOf(beat.at, fps);
      const next = n + 1 < beats.length ? frameOf(beats[n + 1].at, fps) : end;
      const t = frame - at; const out = frame - next;
      if (t < 0 || out > 8) return null;
      const p = n === 0 ? 1 : grow(t, 0, 8);
      const leave = out > 0 ? smooth(out / 8) : 0;
      const noteAt = beat.note ? (beat.note.at == null ? at + 22 : frameOf(beat.note.at, fps)) : 0;
      return <div key={n} style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: p * (1 - leave), transform: `translateY(${(1 - p) * 46 - leave * 60}px)`}}>
        {beat.kind === 'quote' && <QuoteBeat beat={beat} t={t} tone={tone} />}
        {beat.kind === 'list' && <ListBeat beat={beat} frame={frame} at={at} fps={fps} tone={tone} height={height} />}
        {beat.kind === 'calendar' && <CalendarBeat beat={beat} t={t} span={next - at} tone={tone} height={height} />}
        {beat.kind === 'figure' && <FigureBeat beat={beat} t={t} tone={tone} height={height} />}
        {beat.kind === 'timeline' && <TimelineBeat beat={beat} frame={frame} at={at} fps={fps} tone={tone} height={height} />}
        {beat.kind === 'bars' && <BarsBeat beat={beat} frame={frame} at={at} fps={fps} tone={tone} height={height} />}
        {beat.kind === 'image' && <Img src={byId(manifest, beat.asset_id)} style={{objectFit: 'contain', width: '100%', height: '100%', filter: 'drop-shadow(0 20px 16px rgba(23,38,54,0.12))', transform: `translateY(${Math.sin(t / 70) * 4}px)`}} />}
        {beat.note && frame >= noteAt && <div style={{position: 'absolute', left: 0, right: 0, top: height + 14, fontSize: 36, fontStyle: 'italic', fontWeight: 600, textAlign: 'center', clipPath: `inset(-10% ${(1 - grow(frame, noteAt, 12)) * 100}% -10% 0)`}}><span style={{borderBottom: `5px solid ${C.gold}`, paddingBottom: 4}}>{beat.note.text}</span></div>}
      </div>;
    })}
  </div>;
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
    {scene.beats && <Beats scene={scene} manifest={manifest} start={start} end={end} frame={frame} fps={30} tone={{ink, paper: dark ? C.navy : C.ivory, dark}} />}
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
