import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {loadFont} from '@remotion/fonts';
import antonUrl from '@fontsource/anton/files/anton-latin-400-normal.woff2';
import caveatUrl from '@fontsource/caveat/files/caveat-latin-700-normal.woff2';

// Fuentes empaquetadas en local: el render no depende de Google Fonts ni de la red.
loadFont({family: 'Anton', url: antonUrl, weight: '400'});
loadFont({family: 'Caveat', url: caveatUrl, weight: '700'});

export type Colores = {papel: string; tinta: string; acento: string; apoyo: string};
export type Escena = {
  id: string; desde: number; dur: number; keyword: string; resaltar: string; kicker: string;
  nota: string; dato: string; fuente: string; imagen: string; foto: boolean; entrada: string;
};
export type Palabra = {t: string; a: number; b: number};
export type VideoVox = {
  fps: number; ancho: number; alto: number; frames: number; titulo: string;
  perfil: {nombre: string; handle: string; colores: Colores; cuadricula: boolean};
  voz: string; musica: string; sfx: boolean; escenas: Escena[]; palabras: Palabra[];
};

const W = 1080;
const H = 1920;
// Zona segura conservadora de TikTok: nada importante fuera de este marco.
const SEGURO = {izq: 90, der: 960, arriba: 230, abajo: 1440};
const PASO_Y = 2400; // separación entre escenas en el lienzo (mayor que la pantalla)

/** Movimiento "a doses": los elementos de papel se actualizan a 12 fps; la cámara, a 30. */
const doses = (frame: number) => Math.floor(frame / 2.5) * 2.5;
const azar = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
const lugar = (i: number) => ({x: (i % 2 === 0 ? -1 : 1) * 620, y: i * PASO_Y, giro: [-3, 2.5, -2, 3.5][i % 4]});

const Papel: React.FC<{c: Colores; cuadricula: boolean}> = ({c, cuadricula}) => {
  const frame = useCurrentFrame();
  const semilla = Math.floor(frame / 10) % 6; // el grano "hierve" 3 veces por segundo
  return (
    <AbsoluteFill style={{backgroundColor: c.papel}}>
      {cuadricula && (
        <AbsoluteFill style={{opacity: 0.09, backgroundImage: `linear-gradient(${c.tinta} 2px, transparent 2px), linear-gradient(90deg, ${c.tinta} 2px, transparent 2px)`, backgroundSize: '90px 90px'}} />
      )}
      <svg width={W} height={H} style={{position: 'absolute', mixBlendMode: 'multiply', opacity: 0.2}}>
        <filter id="grano">
          <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves={2} seed={semilla} />
          <feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.3  0 0 0 0 0.22  0 0 0 0.9 0" />
        </filter>
        <rect width={W} height={H} filter="url(#grano)" />
      </svg>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.16) 100%)'}} />
    </AbsoluteFill>
  );
};

/** Entrada de un elemento según su "verbo de papel". Devuelve estilos; nunca usa opacidad. */
const entrar = (verbo: string, f: number, fps: number): React.CSSProperties => {
  const s = spring({frame: f, fps, config: {damping: 13, stiffness: 190, mass: 0.7}});
  const duro = spring({frame: f, fps, config: {damping: 200, stiffness: 260}});
  if (f < 0) return {transform: 'translateX(-3000px)'};
  switch (verbo) {
    case 'sello':
      return {transform: `scale(${interpolate(duro, [0, 1], [1.9, 1])}) rotate(${interpolate(duro, [0, 1], [-9, 0])}deg)`, clipPath: duro < 0.02 ? 'inset(50%)' : undefined};
    case 'desliza-izq':
      return {transform: `translateX(${interpolate(s, [0, 1], [-1300, 0])}px) rotate(${interpolate(s, [0, 1], [-8, 0])}deg)`};
    case 'desliza-der':
      return {transform: `translateX(${interpolate(s, [0, 1], [1300, 0])}px) rotate(${interpolate(s, [0, 1], [8, 0])}deg)`};
    case 'cae':
      return {transform: `translateY(${interpolate(s, [0, 1], [-1500, 0])}px) rotate(${interpolate(s, [0, 1], [6, 0])}deg)`};
    case 'desdobla':
      return {transform: `perspective(1400px) rotateX(${interpolate(s, [0, 1], [-96, 0])}deg)`, transformOrigin: 'top center'};
    case 'mordidas': {
      const pasos = [0, 0.18, 0.31, 0.62, 0.74, 1];
      const k = pasos[Math.min(pasos.length - 1, Math.floor(f / 2.5))];
      return {clipPath: `inset(0 ${(1 - k) * 100}% 0 0)`};
    }
    default:
      return {transform: `scale(${s})`};
  }
};

const partir = (texto: string): string[] => {
  const palabras = texto.split(/\s+/).filter(Boolean);
  const lineas: string[] = [];
  let actual = '';
  for (const p of palabras) {
    if (actual && (actual + ' ' + p).length > 11) {
      lineas.push(actual);
      actual = p;
    } else actual = actual ? actual + ' ' + p : p;
  }
  if (actual) lineas.push(actual);
  return lineas;
};

const Titular: React.FC<{e: Escena; c: Colores; f: number; indice: number}> = ({e, c, f, indice}) => {
  const {fps} = useVideoConfig();
  const lineas = partir(e.keyword);
  const largo = Math.max(...lineas.map((l) => l.length));
  const tope = lineas.length >= 3 ? 170 : 215;
  const tam = Math.max(110, Math.min(tope, (SEGURO.der - SEGURO.izq) / (largo * 0.47)));
  const verbos = ['desliza-izq', 'cae', 'desliza-der', 'sello', 'mordidas', 'desdobla'];
  return (
    <div style={{position: 'absolute', left: SEGURO.izq, top: 350, width: SEGURO.der - SEGURO.izq}}>
      {lineas.map((linea, j) => {
        const verbo = j === 0 ? e.entrada : verbos[(indice + j) % verbos.length];
        const q = doses(f);
        const temblor = `rotate(${(azar(indice * 7 + j + q) - 0.5) * 0.9}deg)`;
        return (
          <div key={j} style={{...entrar(verbo, f - 3 - j * 4, fps), height: tam * 1.06}}>
            <div style={{transform: temblor, fontFamily: 'Anton', fontSize: tam, lineHeight: 1, color: c.tinta, whiteSpace: 'nowrap', letterSpacing: -1}}>
              {linea.split(' ').map((p, k) => {
                const marca = e.resaltar && p.replace(/[¿¡]/g, '') === e.resaltar.replace(/[¿¡]/g, '');
                const trazo = spring({frame: f - 16 - j * 4, fps, config: {damping: 200, stiffness: 140}});
                return (
                  <span key={k} style={{position: 'relative', display: 'inline-block', marginRight: tam * 0.22}}>
                    {marca && (
                      <span style={{position: 'absolute', left: -tam * 0.08, right: -tam * 0.08, top: tam * 0.1, bottom: -tam * 0.02, background: c.acento, transform: `rotate(-1.6deg) scaleX(${trazo})`, transformOrigin: 'left center', borderRadius: `${tam * 0.06}px ${tam * 0.16}px ${tam * 0.05}px ${tam * 0.14}px`}} />
                    )}
                    <span style={{position: 'relative'}}>{p}</span>
                    {marca && <span style={{position: 'absolute', left: 0, top: 0, color: c.papel, clipPath: `inset(-20% ${(1 - trazo) * 100}% -20% 0)`}}>{p}</span>}
                  </span>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};

const borde = (px: number, color: string) =>
  [[px, 0], [-px, 0], [0, px], [0, -px], [px * 0.7, px * 0.7], [-px * 0.7, px * 0.7], [px * 0.7, -px * 0.7], [-px * 0.7, -px * 0.7]]
    .map(([x, y]) => `drop-shadow(${x}px ${y}px 0 ${color})`).join(' ');

const Sticker: React.FC<{e: Escena; c: Colores; f: number; indice: number; arriba: number}> = ({e, c, f, indice, arriba}) => {
  const {fps} = useVideoConfig();
  const alto = 1215 - arriba;
  const q = doses(f);
  const vaiven = `translate(${(azar(q + indice) - 0.5) * 5}px, ${(azar(q * 1.7 + indice) - 0.5) * 5}px) rotate(${(indice % 2 ? 3 : -3) + (azar(q * 0.6 + indice) - 0.5) * 1.6}deg)`;
  const verbos = ['cae', 'desliza-der', 'sello', 'desliza-izq'];
  const entrada = entrar(verbos[indice % verbos.length], f - 8, fps);
  const medio = spring({frame: f - 4, fps, config: {damping: 200, stiffness: 120}});
  return (
    <div style={{position: 'absolute', left: SEGURO.izq, width: SEGURO.der - SEGURO.izq, top: arriba, height: alto, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
      {/* semitono de periódico detrás del sujeto */}
      <div style={{position: 'absolute', width: alto * 0.95, height: alto * 0.95, borderRadius: '50%', transform: `scale(${medio}) rotate(${q * 0.4}deg)`, backgroundColor: c.apoyo, backgroundImage: `radial-gradient(${c.tinta} 22%, transparent 24%)`, backgroundSize: '26px 26px', opacity: 0.9}} />
      <div style={{...entrada, position: 'relative', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{transform: vaiven}}>
          {e.imagen ? (
            e.foto ? (
              <div style={{background: '#fff', padding: '18px 18px 60px', boxShadow: `16px 16px 0 ${c.tinta}`}}>
                <Img src={staticFile(e.imagen)} style={{display: 'block', maxWidth: 620, maxHeight: alto - 150, filter: 'grayscale(1) contrast(1.25)'}} />
              </div>
            ) : (
              <Img src={staticFile(e.imagen)} style={{display: 'block', width: 'auto', height: alto * 0.98, maxWidth: 840, objectFit: 'contain', filter: `${borde(7, '#fff')} drop-shadow(14px 14px 0 ${c.tinta})`}} />
            )
          ) : e.dato ? (
            <div style={{fontFamily: 'Anton', fontSize: Math.min(alto * 0.62, 900 / Math.max(2, e.dato.length)), color: c.papel, background: c.tinta, padding: '10px 46px', boxShadow: `14px 14px 0 ${c.acento}`, border: `8px solid ${c.papel}`, outline: `6px solid ${c.tinta}`}}>{e.dato}</div>
          ) : null}
          {/* cinta adhesiva */}
          {(e.imagen || e.dato) && <div style={{position: 'absolute', top: -26, left: '38%', width: 190, height: 52, background: c.acento, opacity: 0.82, transform: 'rotate(-5deg)'}} />}
        </div>
      </div>
    </div>
  );
};

const Nota: React.FC<{e: Escena; c: Colores; f: number; indice: number}> = ({e, c, f, indice}) => {
  const {fps} = useVideoConfig();
  if (!e.nota) return null;
  const t = spring({frame: f - 22, fps, config: {damping: 200, stiffness: 110}});
  const der = indice % 2 === 0;
  return (
    <div style={{position: 'absolute', top: 1195, [der ? 'right' : 'left']: SEGURO.izq + 10, width: 560, transform: `rotate(${der ? -4 : 4}deg)`}}>
      <svg width={150} height={110} viewBox="0 0 150 110" style={{position: 'absolute', top: -105, [der ? 'left' : 'right']: 40, transform: der ? undefined : 'scaleX(-1)'}}>
        <path d="M130 100 C 110 40, 70 20, 22 18 M22 18 l 26 -14 M22 18 l 20 22" fill="none" stroke={c.tinta} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />
      </svg>
      <div style={{fontFamily: 'Caveat', fontSize: 64, lineHeight: 1, color: c.tinta, textAlign: der ? 'right' : 'left', clipPath: `inset(0 ${(1 - t) * 100}% 0 0)`}}>{e.nota}</div>
    </div>
  );
};

const EscenaVox: React.FC<{e: Escena; c: Colores; indice: number; f: number}> = ({e, c, indice, f}) => {
  const {fps} = useVideoConfig();
  const lineas = partir(e.keyword);
  const largo = Math.max(...lineas.map((l) => l.length));
  const tam = Math.max(110, Math.min(lineas.length >= 3 ? 170 : 215, (SEGURO.der - SEGURO.izq) / (largo * 0.47)));
  const finTitular = 350 + lineas.length * tam * 1.06;
  return (
    <div style={{position: 'absolute', width: W, height: H}}>
      {e.kicker && (
        <div style={{position: 'absolute', left: SEGURO.izq, top: SEGURO.arriba + 22, ...entrar('mordidas', f, fps)}}>
          <div style={{fontFamily: 'Anton', fontSize: 44, letterSpacing: 2, color: c.papel, background: c.tinta, padding: '6px 22px', transform: 'rotate(-2deg)', textTransform: 'uppercase'}}>{e.kicker}</div>
        </div>
      )}
      <Titular e={e} c={c} f={f} indice={indice} />
      <Sticker e={e} c={c} f={f} indice={indice} arriba={finTitular + 40} />
      <Nota e={e} c={c} f={f} indice={indice} />
      {e.fuente && <div style={{position: 'absolute', left: SEGURO.izq, top: SEGURO.abajo - 6, fontFamily: 'Caveat', fontSize: 34, color: c.tinta, opacity: 0.75}}>Fuente: {e.fuente}</div>}
    </div>
  );
};

/** Subtítulos por palabra con los tiempos reales de la narración (nunca repartidos a mano). */
const Subtitulos: React.FC<{palabras: Palabra[]; c: Colores}> = ({palabras, c}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const grupos = React.useMemo(() => {
    const g: Palabra[][] = [];
    let actual: Palabra[] = [];
    for (const p of palabras) {
      const letras = actual.reduce((n, x) => n + x.t.length + 1, 0) + p.t.length;
      const pausa = actual.length > 0 && p.a - actual[actual.length - 1].b > 0.35;
      if (actual.length > 0 && (actual.length >= 3 || letras > 18 || pausa)) {
        g.push(actual);
        actual = [];
      }
      actual.push(p);
      if (/[.?!…:]$/.test(p.t)) {
        g.push(actual);
        actual = [];
      }
    }
    if (actual.length) g.push(actual);
    return g;
  }, [palabras]);
  const i = grupos.findIndex((g, k) => t >= g[0].a - 0.04 && t < (grupos[k + 1] ? grupos[k + 1][0].a - 0.04 : g[g.length - 1].b + 0.4));
  if (i < 0) return null;
  const grupo = grupos[i];
  return (
    <div style={{position: 'absolute', left: SEGURO.izq, width: SEGURO.der - SEGURO.izq, top: 1320, display: 'flex', justifyContent: 'center'}}>
      <div style={{display: 'flex', gap: 16, background: c.papel, padding: '10px 22px 14px', boxShadow: `9px 9px 0 ${c.tinta}`, border: `5px solid ${c.tinta}`, transform: `rotate(${i % 2 ? 1 : -1}deg)`}}>
        {grupo.map((p, k) => {
          const dicha = t >= p.a - 0.04;
          const activa = dicha && t < p.b + 0.06;
          const golpe = spring({frame: frame - Math.round((p.a - 0.04) * fps), fps, config: {damping: 11, stiffness: 260, mass: 0.5}});
          return (
            <span key={k} style={{fontFamily: 'Anton', fontSize: 74, lineHeight: 1.05, textTransform: 'uppercase', color: activa ? c.papel : c.tinta, background: activa ? c.acento : 'transparent', padding: '0 10px', transform: `scale(${dicha ? interpolate(golpe, [0, 1], [0.55, 1]) : 0})`, display: 'inline-block'}}>
              {p.t}
            </span>
          );
        })}
      </div>
    </div>
  );
};

const SONIDOS = ['papel', 'deslizar', 'golpe', 'pop'];

export const Vox: React.FC<VideoVox> = (v) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const c = v.perfil.colores;
  const VIAJE = 9; // la cámara sale 9 frames antes del cambio de escena
  let k = 0;
  for (let i = 0; i < v.escenas.length; i++) if (frame >= v.escenas[i].desde - VIAJE) k = i;
  const actual = v.escenas[k];
  const a = lugar(Math.max(0, k - 1));
  const b = lugar(k);
  const viaje = k === 0 ? 1 : spring({frame: frame - (actual.desde - VIAJE), fps, config: {damping: 22, stiffness: 150, mass: 0.9}});
  const deriva = interpolate(frame, [actual.desde, actual.desde + actual.dur], [1, 1.05], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const cam = {
    x: interpolate(viaje, [0, 1], [a.x, b.x]),
    y: interpolate(viaje, [0, 1], [a.y, b.y]),
    giro: interpolate(viaje, [0, 1], [a.giro, b.giro]),
    zoom: (1 - 0.2 * Math.sin(Math.PI * Math.min(1, Math.max(0, viaje)))) * deriva, // retrocede a mitad del viaje
  };
  const avance = frame / v.frames;
  return (
    <AbsoluteFill style={{backgroundColor: c.papel, overflow: 'hidden'}}>
      <Papel c={c} cuadricula={v.perfil.cuadricula} />
      <div style={{position: 'absolute', left: W / 2, top: H / 2, transform: `scale(${cam.zoom}) rotate(${-cam.giro}deg) translate(${-cam.x}px, ${-cam.y}px)`}}>
        {v.escenas.map((e, i) => {
          if (Math.abs(i - k) > 1) return null;
          const p = lugar(i);
          // La primera escena arranca ya compuesta: el frame 0 debe detener el scroll.
          const f = frame - e.desde + (i === 0 ? 60 : VIAJE + 3);
          return (
            <div key={e.id} style={{position: 'absolute', left: p.x - W / 2, top: p.y - H / 2, width: W, height: H, transform: `rotate(${p.giro}deg)`}}>
              <EscenaVox e={e} c={c} indice={i} f={f} />
            </div>
          );
        })}
      </div>
      {v.palabras.length > 0 && <Subtitulos palabras={v.palabras} c={c} />}
      {/* barra de avance y firma, dentro de la zona segura */}
      <div style={{position: 'absolute', left: SEGURO.izq, top: SEGURO.arriba - 8, width: SEGURO.der - SEGURO.izq, height: 10, background: `${c.tinta}22`}}>
        <div style={{width: `${avance * 100}%`, height: '100%', background: c.acento}} />
      </div>
      {v.perfil.handle && <div style={{position: 'absolute', right: W - SEGURO.der, top: SEGURO.arriba + 26, fontFamily: 'Anton', fontSize: 34, color: c.tinta, opacity: 0.7}}>{v.perfil.handle}</div>}
      {v.voz && <Audio src={staticFile(v.voz)} />}
      {v.musica && <Audio src={staticFile(v.musica)} volume={0.1} loop />}
      {v.sfx && v.escenas.map((e, i) => (
        <React.Fragment key={e.id}>
          {i > 0 && <Audio src={staticFile(`sfx/${SONIDOS[i % SONIDOS.length]}.wav`)} from={Math.max(0, e.desde - VIAJE)} volume={0.32} />}
          {e.resaltar && <Audio src={staticFile('sfx/marcador.wav')} from={e.desde + 10} volume={0.22} />}
        </React.Fragment>
      ))}
      
    </AbsoluteFill>
  );
};
