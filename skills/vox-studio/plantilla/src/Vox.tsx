import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import {loadFont} from '@remotion/fonts';
import antonUrl from '@fontsource/anton/files/anton-latin-400-normal.woff2';
import caveatUrl from '@fontsource/caveat/files/caveat-latin-700-normal.woff2';
import gelasioUrl from '@fontsource/gelasio/files/gelasio-latin-700-normal.woff2';

// Fuentes empaquetadas en local: el render no depende de Google Fonts ni de la red.
loadFont({family: 'Anton', url: antonUrl, weight: '400'});
loadFont({family: 'Caveat', url: caveatUrl, weight: '700'});
loadFont({family: 'Gelasio', url: gelasioUrl, weight: '700'});

export type Colores = {papel: string; tinta: string; acento: string; apoyo: string};
export type Escena = {
  id: string; desde: number; dur: number; keyword: string; resaltar: string; kicker: string;
  nota: string; dato: string; fuente: string; imagen: string; foto: boolean; entrada: string; transicion?: string; sonido?: string; remate?: string;
};
export type Palabra = {t: string; a: number; b: number};
export type VideoVox = {
  fps: number; ancho: number; alto: number; frames: number; titulo: string;
  perfil: {nombre: string; handle: string; colores: Colores; cuadricula: boolean; titular?: string; subtitulos?: string};
  finVoz?: number; cierre?: string; volMusica?: number; volEfecto?: number; portada?: {texto: string; resaltar: string; imagen: string};
  voz: string; musica: string; sfx: boolean; escenas: Escena[]; palabras: Palabra[];
};

const W = 1080;
const H = 1920;
// Zona segura conservadora de TikTok: nada importante fuera de este marco.
const SEGURO = {izq: 90, der: 960, arriba: 230, abajo: 1440};
// De y=760 hacia abajo los botones de TikTok tapan la derecha: ahí el contenido termina antes,
// con holgura para giros y sombras.
const DER_BAJO = 900;
const PASO_Y = 2400; // separación entre escenas en el lienzo (mayor que la pantalla)

const azar = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
const lugar = (i: number) => ({x: (i % 2 === 0 ? -1 : 1) * 620, y: i * PASO_Y, giro: [-3, 2.5, -2, 3.5][i % 4]});

const Papel: React.FC<{c: Colores; cuadricula: boolean}> = ({c, cuadricula}) => {
  const frame = useCurrentFrame();
  const semilla = Math.floor(frame / 15) % 4; // el grano cambia 2 veces por segundo: vivo, sin distraer
  return (
    <AbsoluteFill style={{backgroundColor: c.papel}}>
      {cuadricula && (
        <AbsoluteFill style={{opacity: 0.09, backgroundImage: `linear-gradient(${c.tinta} 2px, transparent 2px), linear-gradient(90deg, ${c.tinta} 2px, transparent 2px)`, backgroundSize: '90px 90px'}} />
      )}
      <svg width={W} height={H} style={{position: 'absolute', mixBlendMode: 'multiply', opacity: 0.13}}>
        <filter id="grano">
          <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves={2} seed={semilla} />
          <feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.3  0 0 0 0 0.22  0 0 0 0.9 0" />
        </filter>
        <rect width={W} height={H} filter="url(#grano)" />
      </svg>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.09) 100%)'}} />
    </AbsoluteFill>
  );
};

/** Entrada de un elemento según su "verbo de papel". Devuelve estilos; nunca usa opacidad. */
const entrar = (verbo: string, f: number, fps: number): React.CSSProperties => {
  const s = spring({frame: f, fps, config: {damping: 18, stiffness: 170, mass: 0.8}});
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
      // Al terminar no queda recorte; mientras dura, el recorte deja pasar acentos y resaltador.
      return k >= 1 ? {} : {clipPath: `inset(-40% ${(1 - k) * 100}% -40% -10%)`};
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

const sinSignos = (p: string) => p.replace(/[¿¡?!.,;:]/g, '');
/** Tipografía del titular por espacio: Anton (condensada) o Gelasio (serif sobria). */
const FUENTES: Record<string, {ancho: number; tope: number; espacio: number}> = {
  Anton: {ancho: 0.47, tope: 176, espacio: -1},
  Gelasio: {ancho: 0.64, tope: 132, espacio: -2},
};
// Ancho real de cada mayúscula de Gelasio 700, en em (leído de la fuente): una media por letra
// dejaba salir del margen las líneas con M, N, O, D o G.
const ANCHOS: Record<string, Record<string, number>> = {
  Gelasio: {A: 0.76, B: 0.76, C: 0.72, D: 0.83, E: 0.72, F: 0.67, G: 0.81, H: 0.91, I: 0.45, J: 0.6, K: 0.82, L: 0.69, M: 1.02, N: 0.84, Ñ: 0.84, O: 0.82, P: 0.7, Q: 0.82, R: 0.8, S: 0.65, T: 0.68, U: 0.83, V: 0.76, W: 1.13, X: 0.81, Y: 0.73, Z: 0.69, Á: 0.76, É: 0.72, Í: 0.45, Ó: 0.82, Ú: 0.83, Ü: 0.83, '¿': 0.55, '?': 0.55, '¡': 0.38, '!': 0.38, '0': 0.7, '1': 0.49, '2': 0.63, '3': 0.62, '4': 0.65, '5': 0.6, '6': 0.65, '7': 0.55, '8': 0.68, '9': 0.65, $: 0.64, '%': 0.88, '.': 0.33, ',': 0.33, ':': 0.37},
};
const SEPARA = 0.22; // espacio entre palabras del titular, en em
/** Ancho de una línea del titular en em: con la tabla de la fuente si existe; si no, con su media por letra. */
const anchoLinea = (linea: string, fuente: string, media: number): number => {
  const tabla = ANCHOS[fuente];
  if (!tabla) return Math.max(linea.length, 3) * media;
  const palabras = linea.toUpperCase().split(' ');
  const letras = palabras.reduce((a, p) => a + [...p].reduce((b, ch) => b + (tabla[ch] ?? 0.84), 0), 0);
  // 0.16 em: lo que el resaltador sobresale a los lados.
  return Math.max(letras + SEPARA * (palabras.length - 1) + 0.16, 3 * media);
};
const FuenteCtx = React.createContext('Anton');
const ACENTUADA = /[ÁÉÍÓÚÜÑ]/;
/** En Gelasio la tilde de una mayúscula sube unos 0.3 em sobre la letra: hay que hacerle sitio. */
const tildeAlta = (texto: string, fuente: string) => fuente === 'Gelasio' && ACENTUADA.test(texto.toUpperCase());
const medidas = (keyword: string, fuente: string, kicker = '') => {
  const m = FUENTES[fuente] ?? FUENTES.Anton;
  const lineas = partir(keyword);
  // Titular en bloque: cada línea crece hasta llenar el ancho útil (como una portada de revista),
  // con tope por línea y sin que una línea corta supere 1.7 veces a la más pequeña.
  const tope = (lineas.length >= 3 ? 0.9 : 1.05) * m.tope;
  const libres = lineas.map((l) => Math.min(tope, (SEGURO.der - SEGURO.izq) / anchoLinea(l, fuente, m.ancho)));
  const menor = Math.min(...libres);
  const tams = libres.map((v) => Math.min(v, menor * 1.7));
  // Con etiqueta (kicker) encima, una tilde en la primera línea quedaría tapada: el titular baja.
  const inicio = 326 + (kicker && tildeAlta(lineas[0] ?? '', fuente) ? 44 : 0);
  return {lineas, tams, inicio, fin: inicio + tams.reduce((a, b) => a + b * 1.06, 0), espacio: m.espacio};
};

const Titular: React.FC<{e: Escena; c: Colores; f: number; indice: number}> = ({e, c, f, indice}) => {
  const {fps} = useVideoConfig();
  const fuente = React.useContext(FuenteCtx);
  const {lineas, tams, espacio, inicio} = medidas(e.keyword, fuente, e.kicker);
  const verbos = ['desliza-izq', 'cae', 'desliza-der', 'sello', 'mordidas', 'desdobla'];
  return (
    <div style={{position: 'absolute', left: SEGURO.izq, top: inicio, width: SEGURO.der - SEGURO.izq}}>
      {lineas.map((linea, j) => {
        const tam = tams[j];
        const verbo = j === 0 ? e.entrada : verbos[(indice + j) % verbos.length];
        const temblor = `rotate(${(azar(indice * 7 + j) - 0.5) * 1.2}deg)`; // inclinación fija por línea; no vibra
        return (
          <div key={j} style={{...entrar(verbo, f - 3 - j * 4, fps), height: tam * 1.06}}>
            <div style={{transform: temblor, fontFamily: fuente, fontWeight: fuente === 'Anton' ? 400 : 700, fontSize: tam, lineHeight: 1, color: c.tinta, whiteSpace: 'nowrap', letterSpacing: espacio}}>
              {linea.split(' ').map((p, k) => {
                const marca = !!e.resaltar && sinSignos(p) === sinSignos(e.resaltar);
                const trazo = spring({frame: f - 16 - j * 4, fps, config: {damping: 200, stiffness: 140}});
                return (
                  <span key={k} style={{position: 'relative', display: 'inline-block', marginRight: tam * SEPARA}}>
                    {marca && (
                      <span style={{position: 'absolute', left: -tam * 0.08, right: -tam * 0.08, top: fuente === 'Anton' ? tam * 0.1 : tam * (tildeAlta(p, fuente) ? -0.17 : 0.04), bottom: fuente === 'Anton' ? -tam * 0.02 : -tam * 0.12, background: c.acento, transform: `rotate(-1.6deg) scaleX(${trazo})`, transformOrigin: 'left center', borderRadius: `${tam * 0.06}px ${tam * 0.16}px ${tam * 0.05}px ${tam * 0.14}px`}} />
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
  const alto = (e.nota ? 1150 : 1265) - arriba;
  // Flotación lenta y continua (antes vibraba a 12 fps: Emi lo percibió como temblor).
  const vaiven = `translateY(${Math.sin(f / 24) * 5}px) rotate(${(indice % 2 ? 2 : -2) + Math.sin(f / 37 + indice) * 0.7}deg)`;
  const verbos = ['cae', 'desliza-der', 'sello', 'desliza-izq'];
  const entrada = entrar(verbos[indice % verbos.length], f - 8, fps);
  const medio = spring({frame: f - 4, fps, config: {damping: 200, stiffness: 120}});
  // Escenas de más de 5 s: a la mitad el recorte da un pulso para que el plano no se quede quieto.
  const golpe = e.dur > 150 ? spring({frame: f - Math.round(e.dur / 2), fps, config: {damping: 200, stiffness: 90}}) : 0;
  const pulso = 1 + 0.07 * Math.sin(Math.PI * golpe);
  return (
    <div style={{position: 'absolute', left: SEGURO.izq, width: DER_BAJO - SEGURO.izq, top: arriba, height: alto, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
      {/* semitono de periódico detrás del sujeto */}
      {(e.imagen || e.dato) && <div style={{position: 'absolute', width: alto * 0.95, height: alto * 0.95, borderRadius: '50%', transform: `scale(${medio}) rotate(${f * 0.06}deg)`, backgroundColor: c.apoyo, backgroundImage: `radial-gradient(${c.tinta} 22%, transparent 24%)`, backgroundSize: '26px 26px', opacity: 0.9}} />}
      {(e.imagen || e.dato) && <svg width={alto * 1.3} height={alto * 1.3} viewBox="-100 -100 200 200" style={{position: 'absolute'}}>
        {Array.from({length: 12}).map((_, n) => {
          const ang = (n / 12) * Math.PI * 2 + indice;
          const t = spring({frame: f - 12 - (n % 3), fps, config: {damping: 200, stiffness: 160}});
          return <line key={n} x1={Math.cos(ang) * 72} y1={Math.sin(ang) * 72} x2={Math.cos(ang) * (72 + 20 * t)} y2={Math.sin(ang) * (72 + 20 * t)} stroke={c.tinta} strokeWidth={2.6} strokeLinecap="round" />;
        })}
      </svg>}
      <div style={{...entrada, position: 'relative', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{transform: `${vaiven} scale(${pulso})`}}>
          {e.imagen ? (
            e.foto ? (
              <div style={{background: '#fff', padding: '18px 18px 60px', boxShadow: `16px 16px 0 ${c.tinta}`}}>
                <Img src={staticFile(e.imagen)} style={{display: 'block', maxWidth: 620, maxHeight: alto - 150, filter: 'grayscale(1) contrast(1.25)'}} />
              </div>
            ) : (
              <Img src={staticFile(e.imagen)} style={{display: 'block', width: 'auto', height: alto * 0.98, maxWidth: DER_BAJO - SEGURO.izq - 60, objectFit: 'contain', filter: `${borde(7, '#fff')} drop-shadow(14px 14px 0 ${c.tinta})`}} />
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
    <div style={{position: 'absolute', top: 1188, [der ? 'right' : 'left']: der ? W - DER_BAJO + 20 : SEGURO.izq + 10, width: 540, transform: `rotate(${der ? -4 : 4}deg)`}}>
      <svg width={150} height={110} viewBox="0 0 150 110" style={{position: 'absolute', top: -105, [der ? 'left' : 'right']: 40, transform: der ? undefined : 'scaleX(-1)'}}>
        <path d="M130 100 C 110 40, 70 20, 22 18 M22 18 l 26 -14 M22 18 l 20 22" fill="none" stroke={c.tinta} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />
      </svg>
      <div style={{fontFamily: 'Caveat', fontSize: 60, lineHeight: 1, color: c.tinta, textAlign: der ? 'right' : 'left', clipPath: `inset(0 ${(1 - t) * 100}% 0 0)`}}>{e.nota}</div>
    </div>
  );
};

/** Remate visual tipo meme: un sello de goma que cae a media escena, junto con su sonido. */
const Remate: React.FC<{e: Escena; c: Colores; f: number; arriba: number}> = ({e, c, f, arriba}) => {
  const {fps} = useVideoConfig();
  if (!e.remate) return null;
  const en = Math.round(e.dur * 0.55);
  return (
    <div style={{position: 'absolute', right: W - DER_BAJO + 30, top: arriba - 20, zIndex: 4, ...entrar('sello', f - en, fps)}}>
      <div style={{fontFamily: 'Anton', fontSize: Math.min(84, 640 / Math.max(4, e.remate.length * 0.5)), lineHeight: 1, color: c.acento, border: `10px solid ${c.acento}`, borderRadius: 14, padding: '6px 26px 10px', transform: 'rotate(7deg)', transformOrigin: 'top right', background: `${c.papel}F2`, letterSpacing: 2}}>{e.remate}</div>
    </div>
  );
};

const EscenaVox: React.FC<{e: Escena; c: Colores; indice: number; f: number}> = ({e, c, indice, f}) => {
  const {fps} = useVideoConfig();
  const finTitular = medidas(e.keyword, React.useContext(FuenteCtx), e.kicker).fin;
  return (
    <div style={{position: 'absolute', width: W, height: H}}>
      {e.kicker && (
        <div style={{position: 'absolute', left: SEGURO.izq, top: SEGURO.arriba + 22, ...entrar('mordidas', f, fps)}}>
          <div style={{fontFamily: 'Anton', fontSize: 44, letterSpacing: 2, color: c.papel, background: c.tinta, padding: '6px 22px', transform: 'rotate(-2deg)', textTransform: 'uppercase'}}>{e.kicker}</div>
        </div>
      )}
      <Titular e={e} c={c} f={f} indice={indice} />
      <Sticker e={e} c={c} f={f} indice={indice} arriba={finTitular + 62} />
      <Remate e={e} c={c} f={f} arriba={finTitular + 62} />
      <div style={{position: 'absolute', inset: 0, zIndex: 3}}><Nota e={e} c={c} f={f} indice={indice} /></div>
      {e.fuente && <div style={{position: 'absolute', right: W - SEGURO.der, top: SEGURO.arriba + 30, maxWidth: 520, textAlign: 'right', fontFamily: 'Caveat', fontSize: 42, lineHeight: 1, color: c.tinta}}>Fuente: {e.fuente}</div>}
    </div>
  );
};

/** Subtítulos por palabra con los tiempos reales de la narración (nunca repartidos a mano). */
const Subtitulos: React.FC<{palabras: Palabra[]; c: Colores; fuente: string}> = ({palabras, c, fuente}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const grupos = React.useMemo(() => {
    const g: Palabra[][] = [];
    let actual: Palabra[] = [];
    for (const p of palabras) {
      const letras = actual.reduce((n, x) => n + x.t.length + 1, 0) + p.t.length;
      const pausa = actual.length > 0 && p.a - actual[actual.length - 1].b > 0.35;
      if (actual.length > 0 && (actual.length >= 3 || letras > (fuente === 'Anton' ? 18 : 15) || pausa)) {
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
  }, [palabras, fuente]);
  const i = grupos.findIndex((g, k) => t >= g[0].a - 0.04 && t < (grupos[k + 1] ? grupos[k + 1][0].a - 0.04 : g[g.length - 1].b + 0.12));
  if (i < 0) return null;
  const grupo = grupos[i];
  return (
    <div style={{position: 'absolute', left: SEGURO.izq, width: SEGURO.der - SEGURO.izq, top: 1320, display: 'flex', justifyContent: 'center'}}>
      <div style={{display: 'flex', gap: 16, background: c.papel, padding: '10px 22px 14px', boxShadow: `9px 9px 0 ${c.tinta}`, border: `5px solid ${c.tinta}`, transform: `rotate(${i % 2 ? 1 : -1}deg)`}}>
        {grupo.map((p, k) => {
          const dicha = t >= p.a - 0.04;
          const activa = dicha && t < p.b + 0.06;
          const golpe = spring({frame: frame - Math.round((p.a - 0.04) * fps), fps, config: {damping: 17, stiffness: 240, mass: 0.6}});
          return (
            <span key={k} style={{fontFamily: fuente, fontWeight: fuente === 'Anton' ? 400 : 700, fontSize: fuente === 'Anton' ? 74 : 62, lineHeight: fuente === 'Anton' ? 1.05 : 1.2, textTransform: 'uppercase', color: activa ? c.papel : dicha ? c.tinta : `${c.tinta}38`, background: activa ? c.acento : 'transparent', padding: '0 10px', transform: `scale(${activa ? interpolate(golpe, [0, 1], [0.8, 1]) : 1})`, display: 'inline-block'}}>
              {p.t}
            </span>
          );
        })}
      </div>
    </div>
  );
};

/** Cierre: al terminar la voz, un sello invita a comentar y una flecha señala el botón de comentarios. */
const Cierre: React.FC<{texto: string; c: Colores; desde: number}> = ({texto, c, desde}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const f = frame - desde;
  if (f < 0) return null;
  const t = spring({frame: f - 6, fps, config: {damping: 200, stiffness: 120}});
  return (
    <div style={{position: 'absolute', left: SEGURO.izq, width: SEGURO.der - SEGURO.izq, top: 1300, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 26}}>
      <div style={entrar('sello', f, fps)}>
        <div style={{fontFamily: 'Anton', fontSize: 84, lineHeight: 1, color: c.papel, background: c.acento, padding: '10px 30px 14px', boxShadow: `10px 10px 0 ${c.tinta}`, transform: 'rotate(-2deg)', letterSpacing: 1}}>{texto}</div>
      </div>
      <svg width={150} height={120} viewBox="0 0 150 120">
        <path d="M8 30 C 60 10, 110 40, 128 100 M128 100 l -30 -10 M128 100 l 6 -32" fill="none" stroke={c.tinta} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />
      </svg>
    </div>
  );
};

const SONIDOS = ['papel', 'deslizar', 'golpe', 'pop'];
const VIAJE = 9; // la cámara sale 9 frames antes del cambio de escena
/** Adelanto del reloj interno de una escena: la primera arranca ya compuesta; las demás, al llegar la cámara. */
const desfase = (e: Escena, i: number) => (i === 0 ? 60 : (e.transicion || 'viaje') === 'viaje' ? VIAJE + 3 : 14);

export const Vox: React.FC<VideoVox> = (v) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const c = v.perfil.colores;
  let k = 0;
  for (let i = 0; i < v.escenas.length; i++) if (frame >= v.escenas[i].desde - VIAJE) k = i;
  const actual = v.escenas[k];
  const a = lugar(Math.max(0, k - 1));
  const b = lugar(k);
  const tr = actual.transicion || 'viaje';
  // 'viaje': la cámara recorre el lienzo. 'barrido' y 'rasgado': un panel cruza la pantalla y la cámara cambia tapada.
  const viaje = k === 0 ? 1 : tr === 'viaje'
    ? spring({frame: frame - (actual.desde - VIAJE), fps, config: {damping: 26, stiffness: 140, mass: 0.9}})
    : frame >= actual.desde ? 1 : 0;
  const cruce = k > 0 && tr !== 'viaje' ? interpolate(frame, [actual.desde - 8, actual.desde + 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : -1;
  const derivaDe = (e: Escena) => interpolate(frame, [e.desde, e.desde + e.dur], [1, 1.05], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const mezcla = Math.min(1, Math.max(0, viaje));
  const deriva = k === 0 ? derivaDe(actual) : derivaDe(v.escenas[k - 1]) * (1 - mezcla) + derivaDe(actual) * mezcla;
  const cam = {
    x: interpolate(viaje, [0, 1], [a.x, b.x]),
    y: interpolate(viaje, [0, 1], [a.y, b.y]),
    giro: interpolate(viaje, [0, 1], [a.giro, b.giro]),
    zoom: (1 - (tr === 'viaje' ? 0.14 : 0) * Math.sin(Math.PI * Math.min(1, Math.max(0, viaje)))) * deriva, // retrocede a mitad del viaje
  };
  const avance = frame / v.frames;
  return (
    <FuenteCtx.Provider value={v.perfil.titular && FUENTES[v.perfil.titular] ? v.perfil.titular : 'Anton'}>
    <AbsoluteFill style={{backgroundColor: c.papel, overflow: 'hidden'}}>
      <Papel c={c} cuadricula={v.perfil.cuadricula} />
      <div style={{position: 'absolute', left: W / 2, top: H / 2, transform: `scale(${cam.zoom}) rotate(${-cam.giro}deg) translate(${-cam.x}px, ${-cam.y}px)`}}>
        {v.escenas.map((e, i) => {
          if (Math.abs(i - k) > 1) return null;
          const p = lugar(i);
          // La primera escena arranca ya compuesta: el frame 0 debe detener el scroll.
          const f = frame - e.desde + desfase(e, i);
          return (
            <div key={e.id} style={{position: 'absolute', left: p.x - W / 2, top: p.y - H / 2, width: W, height: H, transform: `rotate(${p.giro}deg)`}}>
              <EscenaVox e={e} c={c} indice={i} f={f} />
            </div>
          );
        })}
      </div>
      {cruce >= 0 && cruce < 1 && tr === 'barrido' && (
        <>
          <div style={{position: 'absolute', top: 0, left: 0, width: '125%', height: '100%', background: c.acento, transform: `translateX(${interpolate(cruce, [0, 1], [-126, 100])}%) skewX(-8deg)`}} />
          <div style={{position: 'absolute', top: 0, left: 0, width: '70%', height: '100%', background: c.tinta, transform: `translateX(${interpolate(cruce, [0, 1], [-260, 190])}%) skewX(-8deg)`}} />
        </>
      )}
      {cruce >= 0 && cruce < 1 && tr === 'rasgado' && (
        <div style={{position: 'absolute', left: 0, top: 0, width: '100%', height: '130%', transform: `translateY(${interpolate(cruce, [0, 1], [-131, 100])}%)`, filter: `drop-shadow(0 14px 0 ${c.tinta})`}}>
          <div style={{width: '100%', height: '100%', background: c.apoyo, clipPath: `polygon(${Array.from({length: 25}).map((_, n) => `${n * 4.17}% ${n % 2 ? 0 : 2.2 + azar(n) * 1.6}%`).join(', ')}, 100% 100%, ${Array.from({length: 25}).map((_, n) => `${100 - n * 4.17}% ${n % 2 ? 100 : 97.8 - azar(n + 9) * 1.6}%`).join(', ')}, 0 100%)`}} />
        </div>
      )}
      {v.cierre && v.finVoz != null && <Cierre texto={v.cierre} c={c} desde={Math.round((v.finVoz + 0.15) * fps)} />}
      {v.cierre && v.finVoz != null && v.sfx && <Audio src={staticFile('sfx/pop.wav')} from={Math.round((v.finVoz + 0.15) * fps)} volume={0.35} />}
      {v.palabras.length > 0 && <Subtitulos palabras={v.palabras} c={c} fuente={v.perfil.subtitulos && FUENTES[v.perfil.subtitulos] ? v.perfil.subtitulos : 'Anton'} />}
      {/* barra de avance y firma, dentro de la zona segura */}
      <div style={{position: 'absolute', left: SEGURO.izq, top: SEGURO.arriba - 8, width: SEGURO.der - SEGURO.izq, height: 10, background: `${c.tinta}22`}}>
        <div style={{width: `${avance * 100}%`, height: '100%', background: c.acento}} />
      </div>
      {v.perfil.handle && <div style={{position: 'absolute', right: W - SEGURO.der, top: SEGURO.arriba - 52, fontFamily: 'Anton', fontSize: 34, color: c.tinta, opacity: 0.7}}>{v.perfil.handle}</div>}
      {v.voz && <Audio src={staticFile(v.voz)} />}
      {v.musica && <Audio src={staticFile(v.musica)} volume={(fr) => interpolate(fr / fps, [0, 0.5, (v.finVoz ?? 9999), (v.finVoz ?? 9999) + 0.5], [(v.volMusica ?? 0.09) * 2.6, v.volMusica ?? 0.09, v.volMusica ?? 0.09, (v.volMusica ?? 0.09) * 3], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />}
      {v.sfx && v.escenas.map((e, i) => (
        <React.Fragment key={e.id}>
          {i > 0 && <Audio src={staticFile(`sfx/${e.transicion === 'rasgado' ? 'rasgar' : e.transicion === 'barrido' ? 'deslizar' : SONIDOS[i % SONIDOS.length]}.wav`)} from={Math.max(0, e.desde - VIAJE)} volume={0.3} />}
          {e.sonido && <Audio src={staticFile(`sfx/${e.sonido}.wav`)} from={Math.max(0, e.desde + (e.remate ? Math.round(e.dur * 0.55) - desfase(e, i) - 1 : i === 0 ? 2 : 12))} volume={v.volEfecto ?? 0.42} />}
          {e.resaltar && i > 0 && !e.sonido && <Audio src={staticFile('sfx/marcador.wav')} from={e.desde + 10} volume={0.22} />}
        </React.Fragment>
      ))}
      
    </AbsoluteFill>
    </FuenteCtx.Provider>
  );
};

/** Portada: un solo cuadro con el titular y el mejor recorte, centrado para la rejilla del perfil. */
export const Portada: React.FC<VideoVox> = (v) => {
  const c = v.perfil.colores;
  const fuente = v.perfil.titular && FUENTES[v.perfil.titular] ? v.perfil.titular : 'Anton';
  const p = v.portada ?? {texto: v.escenas[0].keyword, resaltar: v.escenas[0].resaltar, imagen: v.escenas.find((e) => e.imagen)?.imagen ?? ''};
  const e: Escena = {...v.escenas[0], keyword: p.texto, resaltar: p.resaltar, entrada: 'sello'};
  const BAJA = 150; // el titular reutiliza el mismo componente del video, desplazado hacia el centro
  const arriba = medidas(p.texto, fuente).fin + BAJA + 50;
  const alto = 1620 - arriba;
  return (
    <FuenteCtx.Provider value={fuente}>
      <AbsoluteFill style={{backgroundColor: c.papel}}>
        <Papel c={c} cuadricula={v.perfil.cuadricula} />
        <div style={{position: 'absolute', left: 0, top: BAJA, width: W, height: H}}>
          <Titular e={e} c={c} f={999} indice={0} />
        </div>
        {p.imagen && (
          <div style={{position: 'absolute', left: SEGURO.izq, width: SEGURO.der - SEGURO.izq, top: arriba, height: alto, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
            <div style={{position: 'absolute', width: alto * 0.9, height: alto * 0.9, borderRadius: '50%', backgroundColor: c.apoyo, backgroundImage: `radial-gradient(${c.tinta} 22%, transparent 24%)`, backgroundSize: '26px 26px'}} />
            <Img src={staticFile(p.imagen)} style={{position: 'relative', height: alto * 0.98, maxWidth: 880, objectFit: 'contain', transform: 'rotate(-3deg)', filter: `${borde(8, '#fff')} drop-shadow(16px 16px 0 ${c.tinta})`}} />
          </div>
        )}
        {v.perfil.handle && <div style={{position: 'absolute', left: SEGURO.izq, top: SEGURO.arriba + 40, fontFamily: 'Anton', fontSize: 44, color: c.papel, background: c.tinta, padding: '6px 22px'}}>{v.perfil.handle}</div>}
      </AbsoluteFill>
    </FuenteCtx.Provider>
  );
};
