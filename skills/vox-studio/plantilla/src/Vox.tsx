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
/** Plano: lo que se ve dentro de una escena desde que la voz dice su palabra ancla. */
export type Plano = {
  tipo: string; desde: number; dur: number; imagen?: string; texto?: string; resaltar?: string; origen?: string;
  items?: {texto: string; marca: string; desde: number}[]; celdas?: {t: string; estado: string}[]; etiqueta?: string;
  dato?: string; tachar?: boolean; imagenes?: string[]; entre?: string; foto?: boolean; credito?: string;
  pasos?: {texto: string; nota?: string; desde: number}[]; hitos?: {fecha: string; texto: string; desde: number}[];
  barras?: {etiqueta: string; valor: number; texto?: string; desde: number}[];
  etiquetas?: {texto: string; x: number; y: number; desde: number}[]; apunte?: {texto: string; desde: number};
  junto?: Plano; // pieza de código que entra al lado de la imagen, sin sustituirla
};
export type Escena = {
  planos?: Plano[]; remateEn?: number | null;
  id: string; desde: number; dur: number; keyword: string; resaltar: string; kicker: string;
  nota: string; dato: string; fuente: string; imagen: string; foto: boolean; entrada: string; transicion?: string; sonido?: string; remate?: string;
};
export type Palabra = {t: string; a: number; b: number; c?: boolean}; // c: la dice la voz de comentario
export type VideoVox = {
  fps: number; ancho: number; alto: number; frames: number; titulo: string;
  perfil: {nombre: string; handle: string; colores: Colores; cuadricula: boolean; titular?: string; subtitulos?: string};
  finVoz?: number; cierre?: string; etiquetaComentario?: string; volMusica?: number; volEfecto?: number; portada?: {texto: string; resaltar: string; imagen: string};
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
  // Anton es casi uniforme (0.47 em) salvo M y W, anchas, e I, estrecha: con la media, «MÍNIMO» o «WHATSAPP» se salían.
  Anton: {A: 0.49, B: 0.48, C: 0.47, D: 0.49, E: 0.41, F: 0.4, G: 0.48, H: 0.5, I: 0.23, J: 0.47, K: 0.47, L: 0.4, M: 0.75, N: 0.5, Ñ: 0.5, O: 0.49, P: 0.47, Q: 0.49, R: 0.48, S: 0.46, T: 0.4, U: 0.47, V: 0.47, W: 0.71, X: 0.48, Y: 0.45, Z: 0.41, Á: 0.49, É: 0.41, Í: 0.23, Ó: 0.49, Ú: 0.47, Ü: 0.47, '¿': 0.49, '?': 0.49, '¡': 0.23, '!': 0.23, '0': 0.49, '1': 0.33, '2': 0.49, '3': 0.49, '4': 0.49, '5': 0.49, '6': 0.49, '7': 0.49, '8': 0.49, '9': 0.49, $: 0.46, '%': 1.06, '.': 0.23, ',': 0.24, ':': 0.24},
  Gelasio: {A: 0.76, B: 0.76, C: 0.72, D: 0.83, E: 0.72, F: 0.67, G: 0.81, H: 0.91, I: 0.45, J: 0.6, K: 0.82, L: 0.69, M: 1.02, N: 0.84, Ñ: 0.84, O: 0.82, P: 0.7, Q: 0.82, R: 0.8, S: 0.65, T: 0.68, U: 0.83, V: 0.76, W: 1.13, X: 0.81, Y: 0.73, Z: 0.69, Á: 0.76, É: 0.72, Í: 0.45, Ó: 0.82, Ú: 0.83, Ü: 0.83, '¿': 0.55, '?': 0.55, '¡': 0.38, '!': 0.38, '0': 0.7, '1': 0.49, '2': 0.63, '3': 0.62, '4': 0.65, '5': 0.6, '6': 0.65, '7': 0.55, '8': 0.68, '9': 0.65, $: 0.64, '%': 0.88, '.': 0.33, ',': 0.33, ':': 0.37},
};
const SEPARA = 0.22; // espacio entre palabras del titular, en em
/** Ancho de una línea del titular en em: con la tabla de la fuente si existe; si no, con su media por letra. */
const anchoLinea = (linea: string, fuente: string, media: number): number => {
  const tabla = ANCHOS[fuente];
  if (!tabla) return Math.max(linea.length, 3) * media;
  const palabras = linea.toUpperCase().split(' ');
  const letras = palabras.reduce((a, p) => a + [...p].reduce((b, ch) => b + (tabla[ch] ?? (fuente === 'Anton' ? 0.5 : 0.84)), 0), 0);
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

const SALIDA = 7; // frames que tarda un plano en irse cuando entra el siguiente
const recorteCss = (c: Colores) => `${borde(7, '#fff')} drop-shadow(14px 14px 0 ${c.tinta})`;
const Cinta: React.FC<{c: Colores}> = ({c}) => <div style={{position: 'absolute', top: -26, left: '38%', width: 190, height: 52, background: c.acento, opacity: 0.82, transform: 'rotate(-5deg)'}} />;

/** Recorte de un documento con la frase clave subrayada a mano: la fuente a la vista. */
const CitaDoc: React.FC<{p: Plano; c: Colores; t: number; ancho: number}> = ({p, c, t, ancho}) => {
  const texto = p.texto ?? '';
  const marca = p.resaltar ?? '';
  const corte = marca ? texto.indexOf(marca) : -1;
  const tam = texto.length <= 80 ? 50 : texto.length <= 120 ? 44 : 40;
  const trazo = interpolate(t, [12, 12 + Math.max(14, marca.length * 0.7)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'relative', width: Math.min(ancho - 30, 770), background: '#FFFDF7', padding: '34px 40px 40px 52px', boxShadow: `14px 14px 0 ${c.tinta}`, transform: `rotate(${Math.sin(t / 40) * 0.5 - 1.5}deg)`}}>
      <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 14, background: c.acento}} />
      <Cinta c={c} />
      <div style={{display: 'inline-block', fontFamily: 'Anton', fontSize: 34, letterSpacing: 1.5, textTransform: 'uppercase', color: c.papel, background: c.tinta, padding: '4px 16px 6px', marginBottom: 18}}>{p.origen}</div>
      <div style={{fontFamily: 'Gelasio', fontWeight: 700, fontSize: tam, lineHeight: 1.34, color: c.tinta}}>
        «{corte < 0 ? texto : texto.slice(0, corte)}
        {corte >= 0 && <span style={{backgroundImage: `linear-gradient(${c.apoyo}, ${c.apoyo})`, backgroundRepeat: 'no-repeat', backgroundSize: `${trazo * 100}% 86%`, backgroundPosition: '0 62%', padding: '0 4px', margin: '0 -4px'}}>{marca}</span>}
        {corte >= 0 && texto.slice(corte + marca.length)}»
      </div>
    </div>
  );
};

/** Lista que se va palomeando o tachando al ritmo de la voz. */
const Lista: React.FC<{p: Plano; c: Colores; real: number; alto: number; ancho: number}> = ({p, c, real, alto, ancho}) => {
  const {fps} = useVideoConfig();
  const items = p.items ?? [];
  const fila = Math.min(124, (alto - 10) / Math.max(1, items.length));
  const largo = Math.max(...items.map((x) => x.texto.length), 4);
  const tam = Math.min(fila * 0.66, (ancho - fila - 90) / (largo * 0.5));
  return (
    <div style={{width: ancho - 40, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      {items.map((it, m) => {
        const t = real - it.desde;
        const dib = interpolate(t, [5, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const no = it.marca === 'no';
        return (
          <div key={m} style={{height: fila, display: 'flex', alignItems: 'center', gap: 26, ...entrar(m % 2 ? 'desliza-der' : 'desliza-izq', t, fps)}}>
            <div style={{flex: 'none', width: fila * 0.72, height: fila * 0.72, border: `7px solid ${c.tinta}`, background: no ? c.papel : it.marca ? c.acento : c.papel, transform: `rotate(${m % 2 ? 3 : -3}deg)`, boxShadow: `6px 6px 0 ${c.tinta}`}}>
              <svg viewBox="0 0 40 40" width="100%" height="100%">
                {it.marca === 'si' && dib > 0 && <path d="M8 21 l9 9 l16 -20" fill="none" stroke={c.papel} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - dib} />}
                {no && dib > 0 && <path d="M9 9 L31 31 M31 9 L9 31" fill="none" stroke={c.tinta} strokeWidth={6} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - dib} />}
              </svg>
            </div>
            <div style={{position: 'relative', fontFamily: 'Anton', fontSize: tam, lineHeight: 1, letterSpacing: 1, color: c.tinta, whiteSpace: 'nowrap'}}>
              {it.texto}
              {no && <div style={{position: 'absolute', left: -8, top: '48%', height: Math.max(8, tam * 0.13), width: `calc(${dib * 100}% + ${16 * dib}px)`, background: c.acento, transform: 'rotate(-2deg)'}} />}
            </div>
          </div>
        );
      })}
    </div>
  );
};

/** Calendario: los días se tachan uno a uno; los marcados saltan en color. */
const Calendario: React.FC<{p: Plano; c: Colores; t: number; alto: number; ancho: number}> = ({p, c, t, alto, ancho}) => {
  const {fps} = useVideoConfig();
  const celdas = p.celdas ?? [];
  const cols = celdas.length <= 7 ? celdas.length : 5;
  const filas = Math.ceil(celdas.length / cols);
  const pie = p.etiqueta ? 84 : 0;
  const lado = Math.min((ancho - 70) / cols - 14, (alto - pie - 30) / filas - 14, 170);
  const paso = Math.min(6, Math.max(0.6, (p.dur - 34) / Math.max(1, celdas.length))); // 31 días caben aunque el plano sea corto
  return (
    <div style={{position: 'relative', background: '#FFFDF7', padding: '22px 22px 16px', boxShadow: `14px 14px 0 ${c.tinta}`, borderTop: `26px solid ${c.tinta}`, transform: 'rotate(1.5deg)'}}>
      <Cinta c={c} />
      <div style={{display: 'grid', gridTemplateColumns: `repeat(${cols}, ${lado}px)`, gap: 14}}>
        {celdas.map((x, n) => {
          const tt = t - 10 - n * paso;
          const dib = interpolate(tt, [0, 5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const salto = x.estado === 'marcado' ? spring({frame: tt, fps, config: {damping: 11, stiffness: 190, mass: 0.7}}) : 0;
          const activo = x.estado === 'marcado' && tt >= 0;
          return (
            <div key={n} style={{position: 'relative', width: lado, height: lado, border: `5px solid ${c.tinta}`, background: activo ? c.acento : c.papel, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${1 + 0.16 * Math.sin(Math.PI * Math.min(1, salto))})`}}>
              <span style={{position: 'relative', zIndex: 1, fontFamily: 'Anton', fontSize: lado * 0.5, lineHeight: 1, color: activo ? c.papel : c.tinta}}>{x.t}</span>
              {x.estado === 'tachado' && dib > 0 && (
                <svg viewBox="0 0 40 40" width="100%" height="100%" style={{position: 'absolute', inset: 0}}>
                  <path d="M6 7 L34 33 M34 7 L6 33" fill="none" stroke={c.acento} strokeWidth={4.5} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - dib} />
                </svg>
              )}
            </div>
          );
        })}
      </div>
      {p.etiqueta && <div style={{fontFamily: 'Caveat', fontSize: 58, lineHeight: 1, color: c.tinta, textAlign: 'center', marginTop: 12}}>{p.etiqueta}</div>}
    </div>
  );
};

/** Cifra grande: cuenta hasta su valor y, si se pide, queda tachada. */
const DatoGrande: React.FC<{p: Plano; c: Colores; t: number; alto: number; texto?: number}> = ({p, c, t, alto, texto = 860}) => {
  const dato = p.dato ?? '';
  const m = /^(\D*)(\d+)(\D*)$/.exec(dato);
  const sube = interpolate(t, [3, 17], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const visto = m ? `${m[1]}${String(Math.round(Number(m[2]) * sube)).padStart(sube < 1 ? 1 : m[2].length, '0')}${m[3]}` : dato;
  const raya = interpolate(t, [20, 27], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tam = Math.min((alto - (p.etiqueta ? 110 : 20)) * 0.6, texto / Math.max(2, dato.length));
  return (
    <div style={{position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', transform: `translateY(${Math.sin(t / 24) * 5}px) rotate(-2deg)`}}>
      <div style={{position: 'relative', fontFamily: 'Anton', fontSize: tam, lineHeight: 1.08, color: c.papel, background: c.tinta, padding: '6px 46px 12px', boxShadow: `14px 14px 0 ${c.acento}`, border: `8px solid ${c.papel}`, outline: `6px solid ${c.tinta}`, fontVariantNumeric: 'tabular-nums'}}>
        {visto}
        {p.tachar && raya > 0 && (
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" width="116%" height="100%" style={{position: 'absolute', left: '-8%', top: 0, overflow: 'visible'}}>
            <path d="M2 78 L98 24" stroke={c.papel} strokeWidth={15} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - raya} vectorEffect="non-scaling-stroke" style={{strokeWidth: 34}} />
            <path d="M2 78 L98 24" stroke={c.acento} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - raya} vectorEffect="non-scaling-stroke" style={{strokeWidth: 20}} />
          </svg>
        )}
        <Cinta c={c} />
      </div>
      {p.etiqueta && <div style={{marginTop: 26, fontFamily: 'Anton', fontSize: Math.min(50, (texto * 1.5) / Math.max(8, p.etiqueta.length)), lineHeight: 1, letterSpacing: 1, textTransform: 'uppercase', color: c.papel, background: c.acento, padding: '8px 24px 10px', transform: 'rotate(3deg)', boxShadow: `8px 8px 0 ${c.tinta}`}}>{p.etiqueta}</div>}
    </div>
  );
};

/** Dos recortes frente a frente, con una ficha en medio (O, VS, +). */
const Duo: React.FC<{p: Plano; c: Colores; t: number; alto: number; ancho: number}> = ({p, c, t, alto, ancho}) => {
  const {fps} = useVideoConfig();
  const [a, b] = p.imagenes ?? [];
  const img = (src: string, giro: number, fase: number) => (
    <Img src={staticFile(src)} style={{display: 'block', maxWidth: ancho * 0.45, maxHeight: alto * 0.82, objectFit: 'contain', filter: recorteCss(c), transform: `translateY(${Math.sin(t / 24 + fase) * 6}px) rotate(${giro}deg)`}} />
  );
  return (
    <div style={{position: 'relative', width: ancho, height: alto, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
      <div style={entrar('desliza-izq', t, fps)}>{a && img(a, -5, 0)}</div>
      <div style={entrar('desliza-der', t - 5, fps)}>{b && img(b, 5, 2)}</div>
      {p.entre && (
        <div style={{position: 'absolute', left: '50%', top: '50%', marginLeft: -70, marginTop: -70, ...entrar('sello', t - 11, fps)}}>
          <div style={{width: 140, height: 140, borderRadius: '50%', background: c.tinta, border: `8px solid ${c.papel}`, outline: `6px solid ${c.tinta}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Anton', fontSize: p.entre.length > 1 ? 58 : 80, color: c.papel}}>{p.entre}</div>
        </div>
      )}
    </div>
  );
};

/** Diagrama de flujo: cada caja cae con su palabra y la flecha se dibuja hacia la siguiente. */
const Flujo: React.FC<{p: Plano; c: Colores; real: number; alto: number; ancho: number}> = ({p, c, real, alto, ancho}) => {
  const {fps} = useVideoConfig();
  const pasos = p.pasos ?? [];
  const n = pasos.length;
  const flecha = 54;
  const caja = Math.min(132, (alto - 10 - (n - 1) * flecha) / n);
  const largo = Math.max(...pasos.map((x) => x.texto.length), 4);
  const tam = Math.min(caja * 0.66, (ancho * 0.62) / (largo * 0.5));
  return (
    <div style={{width: ancho - 40, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', paddingLeft: 40}}>
      {pasos.map((x, m) => {
        const t = real - x.desde;
        const ultimo = m === n - 1;
        const dib = m > 0 ? interpolate(real - (x.desde - 7), [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
        return (
          <React.Fragment key={m}>
            {m > 0 && (
              <svg width={80} height={flecha} viewBox="0 0 80 54" style={{marginLeft: 70}}>
                {dib > 0 && <path d="M40 2 L40 44 M40 48 l-15 -17 M40 48 l15 -17" fill="none" stroke={c.tinta} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - dib} />}
              </svg>
            )}
            <div style={{position: 'relative', height: caja, display: 'flex', alignItems: 'center', ...entrar(m % 2 ? 'desliza-der' : 'sello', t, fps)}}>
              <div style={{fontFamily: 'Anton', fontSize: tam, lineHeight: 1, letterSpacing: 1, whiteSpace: 'nowrap', padding: `${caja * 0.13}px 34px ${caja * 0.17}px`, color: ultimo ? c.papel : m % 2 ? c.tinta : c.papel, background: ultimo ? c.acento : m % 2 ? '#FFFDF7' : c.tinta, border: `7px solid ${c.tinta}`, boxShadow: `9px 9px 0 ${ultimo ? c.tinta : c.acento}`, transform: `rotate(${m % 2 ? 1.5 : -1.5}deg)`}}>{x.texto}</div>
              {x.nota && <div style={{marginLeft: 26, width: 300, fontFamily: 'Caveat', fontSize: 50, lineHeight: 0.95, color: c.tinta, transform: 'rotate(-3deg)', clipPath: `inset(-10% ${(1 - interpolate(t, [8, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})) * 100}% -10% 0)`}}>{x.nota}</div>}
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};

/** Barras que crecen hasta su valor; la mayor va en el color de acento. */
const Barras: React.FC<{p: Plano; c: Colores; real: number; alto: number; ancho: number}> = ({p, c, real, alto, ancho}) => {
  const {fps} = useVideoConfig();
  const barras = p.barras ?? [];
  const max = Math.max(...barras.map((x) => x.valor), 1e-9);
  const fila = Math.min(215, (alto - 70) / Math.max(1, barras.length));
  const cifra = Math.min(fila * 0.4, ancho * 0.11);
  // Cifra tal como se escribió (sin redondear decimales); mientras crece se muestra con sus mismos decimales.
  const decimales = (v: number) => (String(v).split('.')[1] ?? '').length;
  const escrito = (x: {valor: number; texto?: string}) => x.texto || String(x.valor);
  // La pista deja sitio fijo al texto más largo: así ninguna barra se encoge y la proporción dibujada es la de los datos.
  const sitio = Math.max(...barras.map((x) => escrito(x).length), 1) * cifra * 0.5 + 30;
  const pista = Math.max(120, ancho - 40 - sitio);
  return (
    <div style={{width: ancho - 40}}>
      {barras.map((x, m) => {
        const t = real - x.desde;
        const sube = spring({frame: t, fps, config: {damping: 200, stiffness: 70}});
        const largo = Math.max(6, (x.valor / max) * pista * Math.min(1, sube));
        const visto = x.texto || (sube > 0.985 ? String(x.valor) : (x.valor * sube).toFixed(decimales(x.valor)));
        return (
          <div key={m} style={{height: fila, ...entrar('desliza-izq', t, fps)}}>
            <div style={{fontFamily: 'Anton', fontSize: Math.min(56, fila * 0.28), lineHeight: 1.1, letterSpacing: 1, color: c.tinta}}>{x.etiqueta}</div>
            <div style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 6}}>
              <div style={{flex: 'none', width: largo, height: cifra, background: x.valor === max ? c.acento : c.tinta, boxShadow: `7px 7px 0 ${x.valor === max ? c.tinta : c.apoyo}`}} />
              <div style={{flex: 'none', fontFamily: 'Anton', fontSize: cifra, lineHeight: 1, color: c.tinta, whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums'}}>{sube > 0.6 || !x.texto ? visto : ''}</div>
            </div>
          </div>
        );
      })}
      <div style={{fontFamily: 'Caveat', fontSize: 42, lineHeight: 1, color: c.tinta, marginTop: 4}}>Fuente: {p.origen}</div>
    </div>
  );
};

/** Línea de tiempo: la línea baja hasta cada hito cuando la voz llega a él. */
const LineaTiempo: React.FC<{p: Plano; c: Colores; real: number; alto: number; ancho: number}> = ({p, c, real, alto, ancho}) => {
  const {fps} = useVideoConfig();
  const hitos = p.hitos ?? [];
  const fila = Math.min(192, (alto - 10) / Math.max(1, hitos.length));
  // La línea avanza de hito en hito: llega a cada uno justo cuando aparece.
  let avance = 0;
  hitos.forEach((h, m) => {
    if (m > 0) avance += interpolate(real, [h.desde - 9, h.desde], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  });
  return (
    <div style={{position: 'relative', width: ancho - 40, height: fila * hitos.length}}>
      <div style={{position: 'absolute', left: 31, top: fila * 0.5, width: 10, height: fila * (hitos.length - 1), background: `${c.tinta}22`}} />
      <div style={{position: 'absolute', left: 31, top: fila * 0.5, width: 10, height: fila * avance, background: c.tinta}} />
      {hitos.map((h, m) => {
        const t = real - h.desde;
        const salta = spring({frame: t, fps, config: {damping: 11, stiffness: 200, mass: 0.6}});
        if (t < 0) return null;
        return (
          <div key={m} style={{position: 'absolute', left: 0, top: fila * m, height: fila, width: '100%', display: 'flex', alignItems: 'center', gap: 28}}>
            <div style={{flex: 'none', width: 72, height: 72, borderRadius: '50%', background: m === hitos.length - 1 ? c.acento : c.papel, border: `9px solid ${c.tinta}`, transform: `scale(${salta})`}} />
            <div style={entrar('desliza-der', t, fps)}>
              <div style={{display: 'inline-block', fontFamily: 'Anton', fontSize: Math.min(50, fila * 0.3), lineHeight: 1, letterSpacing: 1.5, color: c.papel, background: c.tinta, padding: '5px 16px 7px', transform: 'rotate(-1.5deg)'}}>{h.fecha}</div>
              <div style={{fontFamily: 'Gelasio', fontWeight: 700, fontSize: Math.min(48, fila * 0.29), lineHeight: 1.12, color: c.tinta, marginTop: 8, maxWidth: ancho - 190}}>{h.texto}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

/** Etiquetas que señalan partes de una imagen: explican a la par, no después. */
const Etiquetas: React.FC<{p: Plano; c: Colores; real: number}> = ({p, c, real}) => {
  const {fps} = useVideoConfig();
  return (
    <>
      {(p.etiquetas ?? []).map((x, m) => {
        const t = real - x.desde;
        if (t < 0) return null;
        // Punto a los lados: la etiqueta se abre hacia el centro. Punto al centro: la etiqueta va encima, centrada.
        // Así una etiqueta de 16 letras no sale de la zona segura. En fotos reales, x e y se miden sobre el marco.
        const centro = x.x > 0.35 && x.x < 0.65;
        const izq = x.x >= 0.65;
        const linea = interpolate(t, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return (
          <div key={m} style={{position: 'absolute', left: `${x.x * 100}%`, top: `${x.y * 100}%`, zIndex: 2}}>
            <div style={{position: 'absolute', left: -13, top: -13, width: 26, height: 26, borderRadius: '50%', background: c.acento, border: `5px solid ${c.papel}`, outline: `4px solid ${c.tinta}`}} />
            {centro
              ? <div style={{position: 'absolute', left: -3, bottom: 16, width: 6, height: 44 * linea, background: c.tinta}} />
              : <div style={{position: 'absolute', top: -3, [izq ? 'right' : 'left']: 16, width: 70 * linea, height: 6, background: c.tinta}} />}
            <div style={centro
              ? {position: 'absolute', bottom: 58, left: 0, width: 0, display: 'flex', justifyContent: 'center', ...entrar('sello', t - 5, fps)}
              : {position: 'absolute', top: -34, [izq ? 'right' : 'left']: 84, ...entrar('sello', t - 5, fps)}}>
              <div style={{fontFamily: 'Anton', fontSize: 42, lineHeight: 1, letterSpacing: 1, whiteSpace: 'nowrap', color: c.papel, background: c.tinta, padding: '8px 18px 10px', border: `5px solid ${c.papel}`, transform: `rotate(${izq ? 2 : -2}deg)`}}>{x.texto}</div>
            </div>
          </div>
        );
      })}
    </>
  );
};

/** Apunte a mano junto al plano: la aclaración que acompaña, con su flecha. */
const Apunte: React.FC<{p: Plano; c: Colores; real: number; der: boolean; arriba: number}> = ({p, c, real, der, arriba}) => {
  const {fps} = useVideoConfig();
  if (!p.apunte) return null;
  const t = spring({frame: real - p.apunte.desde, fps, config: {damping: 200, stiffness: 110}});
  if (real < p.apunte.desde) return null;
  return (
    <div style={{position: 'absolute', top: arriba, [der ? 'right' : 'left']: 20, width: 560, transform: `rotate(${der ? -4 : 4}deg)`, zIndex: 3}}>
      <svg width={150} height={110} viewBox="0 0 150 110" style={{position: 'absolute', top: -105, [der ? 'left' : 'right']: 40, transform: der ? undefined : 'scaleX(-1)'}}>
        {t > 0.001 && <path d="M130 100 C 110 40, 70 20, 22 18 M22 18 l 26 -14 M22 18 l 20 22" fill="none" stroke={c.tinta} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />}
      </svg>
      <div style={{fontFamily: 'Caveat', fontSize: 60, lineHeight: 1, color: c.tinta, textAlign: der ? 'right' : 'left', clipPath: `inset(-10% ${(1 - t) * 100}% -10% 0)`}}>{p.apunte.texto}</div>
    </div>
  );
};

/** Los planos de una escena: cada uno entra con su palabra y el anterior sale de cuadro. Nunca por opacidad. */
const Planos: React.FC<{e: Escena; c: Colores; f: number; real: number; indice: number; arriba: number}> = ({e, c, f, real, indice, arriba}) => {
  const {fps} = useVideoConfig();
  const planos = e.planos ?? [];
  const alto = (e.nota || planos.some((x) => x.apunte) ? 1150 : 1265) - arriba;
  const ancho = DER_BAJO - SEGURO.izq;
  const verbos = ['cae', 'desliza-der', 'sello', 'desliza-izq', 'desdobla'];
  return (
    <div style={{position: 'absolute', left: SEGURO.izq, width: ancho, top: arriba, height: alto}}>
      {planos.map((p, j) => {
        // El primer plano usa el reloj adelantado de la escena: llega ya compuesto con la cámara.
        const t = j === 0 ? f - 8 : real - p.desde;
        const s = j + 1 < planos.length ? real - planos[j + 1].desde : -1;
        if (t < 0 || s > SALIDA) return null;
        const lado = (indice + j) % 2 ? 1 : -1;
        const sale = s > 0 ? {transform: `translateX(${lado * Math.pow(s / SALIDA, 2) * 1500}px) rotate(${lado * s * 1.6}deg)`} : {};
        const propio = ['lista', 'duo', 'flujo', 'barras', 'linea'].includes(p.tipo); // sus piezas entran una por una
        const fondo = p.tipo === 'imagen' || p.tipo === 'dato' || p.tipo === 'duo';
        // Con una pieza `junto`, la imagen no se va: se hace a un lado y la pieza entra a su derecha.
        const tj = p.junto ? real - p.junto.desde : -1;
        const cede = p.junto ? spring({frame: tj, fps, config: {damping: 200, stiffness: 130}}) : 0;
        const crece = spring({frame: j === 0 ? t + 4 : t - SALIDA, fps, config: {damping: 200, stiffness: 120}}); // el fondo nuevo espera a que salga el plano anterior
        return (
          <div key={j} style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', ...sale}}>
            {fondo && <div style={{position: 'absolute', width: alto * 0.95, height: alto * 0.95, borderRadius: '50%', transform: `scale(${crece}) rotate(${t * 0.06}deg)`, backgroundColor: c.apoyo, backgroundImage: `radial-gradient(${c.tinta} 22%, transparent 24%)`, backgroundSize: '26px 26px', opacity: 0.9}} />}
            {fondo && <svg width={alto * 1.3} height={alto * 1.3} viewBox="-100 -100 200 200" style={{position: 'absolute'}}>
              {Array.from({length: 12}).map((_, n) => {
                const ang = (n / 12) * Math.PI * 2 + indice + j;
                const r = spring({frame: t - 4 - (n % 3), fps, config: {damping: 200, stiffness: 160}});
                return <line key={n} x1={Math.cos(ang) * 72} y1={Math.sin(ang) * 72} x2={Math.cos(ang) * (72 + 20 * r)} y2={Math.sin(ang) * (72 + 20 * r)} stroke={c.tinta} strokeWidth={2.6} strokeLinecap="round" />;
              })}
            </svg>}
            <div style={{position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', ...(propio ? {} : entrar(verbos[(indice + j) % verbos.length], t, fps))}}>
              {p.tipo === 'imagen' && p.imagen && (
                <div style={{position: 'relative', transformOrigin: 'center', transform: `translateX(${-ancho * 0.25 * cede}px) scale(${1 - 0.4 * cede}) translateY(${Math.sin(t / 24) * 5}px) rotate(${((indice + j) % 2 ? 2 : -2) + Math.sin(t / 37 + j) * 0.7}deg)`}}>
                  {p.foto ? (
                    // Foto real: copia en papel, en blanco y negro, con su crédito. Nunca se recorta como si fuera un objeto.
                    <div style={{background: '#fff', padding: '18px 18px 14px', boxShadow: `16px 16px 0 ${c.tinta}`}}>
                      <Img src={staticFile(p.imagen)} style={{display: 'block', maxWidth: ancho - 130, maxHeight: alto - 150, filter: 'grayscale(1) contrast(1.2)'}} />
                      <div style={{fontFamily: 'Caveat', fontSize: 34, lineHeight: 1, color: '#333', marginTop: 10, maxWidth: ancho - 130}}>{p.credito || ' '}</div>
                    </div>
                  ) : (
                    <Img src={staticFile(p.imagen)} style={{display: 'block', width: 'auto', height: alto * 0.98, maxWidth: ancho - 60, objectFit: 'contain', filter: recorteCss(c)}} />
                  )}
                  <Cinta c={c} />
                  <Etiquetas p={p} c={c} real={real} />
                </div>
              )}
              {p.tipo === 'cita' && <CitaDoc p={p} c={c} t={t} ancho={ancho} />}
              {p.tipo === 'lista' && <Lista p={p} c={c} real={real} alto={alto} ancho={ancho} />}
              {p.tipo === 'calendario' && <Calendario p={p} c={c} t={t} alto={alto} ancho={ancho} />}
              {p.tipo === 'dato' && <DatoGrande p={p} c={c} t={t} alto={alto} />}
              {p.tipo === 'duo' && <Duo p={p} c={c} t={t} alto={alto} ancho={ancho} />}
              {p.tipo === 'flujo' && <Flujo p={p} c={c} real={real} alto={alto} ancho={ancho} />}
              {p.tipo === 'barras' && <Barras p={p} c={c} real={real} alto={alto} ancho={ancho} />}
              {p.tipo === 'linea' && <LineaTiempo p={p} c={c} real={real} alto={alto} ancho={ancho} />}
            </div>
            {p.junto && tj >= 0 && (
              <div style={{position: 'absolute', left: ancho * 0.5, width: ancho * 0.5, top: 0, height: alto, display: 'flex', alignItems: 'center', justifyContent: 'center', ...(['lista', 'flujo', 'barras', 'linea'].includes(p.junto.tipo) ? {} : entrar('sello', tj, fps))}}>
                {p.junto.tipo === 'dato' && <DatoGrande p={p.junto} c={c} t={tj} alto={alto * 0.62} texto={(ancho * 0.5 - 120) * 2} />}
                {p.junto.tipo === 'lista' && <div style={{background: '#FFFDF7', padding: '18px 16px 14px 20px', boxShadow: `10px 10px 0 ${c.tinta}`, transform: 'rotate(1.5deg)'}}><Lista p={p.junto} c={c} real={real} alto={alto * 0.72} ancho={ancho * 0.5 - 10} /></div>}
                {p.junto.tipo === 'calendario' && <Calendario p={p.junto} c={c} t={tj} alto={alto * 0.8} ancho={ancho * 0.5 + 20} />}
                {p.junto.tipo === 'flujo' && <Flujo p={p.junto} c={c} real={real} alto={alto * 0.8} ancho={ancho * 0.5} />}
                {p.junto.tipo === 'barras' && <div style={{background: '#FFFDF7', padding: '18px 16px 14px 20px', boxShadow: `10px 10px 0 ${c.tinta}`, transform: 'rotate(1.5deg)'}}><Barras p={p.junto} c={c} real={real} alto={alto * 0.62} ancho={ancho * 0.5 - 10} /></div>}
                {p.junto.tipo === 'linea' && <div style={{background: '#FFFDF7', padding: '18px 16px 14px 20px', boxShadow: `10px 10px 0 ${c.tinta}`, transform: 'rotate(1.5deg)'}}><LineaTiempo p={p.junto} c={c} real={real} alto={alto * 0.8} ancho={ancho * 0.5 - 10} /></div>}
              </div>
            )}
            <Apunte p={p} c={c} real={real} der={(indice + j) % 2 === 0} arriba={alto + 38} />
          </div>
        );
      })}
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
        {t > 0.001 && <path d="M130 100 C 110 40, 70 20, 22 18 M22 18 l 26 -14 M22 18 l 20 22" fill="none" stroke={c.tinta} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />}
      </svg>
      <div style={{fontFamily: 'Caveat', fontSize: 60, lineHeight: 1, color: c.tinta, textAlign: der ? 'right' : 'left', clipPath: `inset(0 ${(1 - t) * 100}% 0 0)`}}>{e.nota}</div>
    </div>
  );
};

/** Remate visual tipo meme: un sello de goma que cae a media escena, junto con su sonido. */
const Remate: React.FC<{e: Escena; c: Colores; f: number; real: number; arriba: number}> = ({e, c, f, real, arriba}) => {
  const {fps} = useVideoConfig();
  if (!e.remate) return null;
  // Con `remate_en` el sello cae con la palabra; si no, a poco más de media escena.
  const t = e.remateEn != null ? real - e.remateEn : f - Math.round(e.dur * 0.55);
  return (
    <div style={{position: 'absolute', right: W - DER_BAJO + 30, top: arriba - 20, zIndex: 4, ...entrar('sello', t, fps)}}>
      <div style={{fontFamily: 'Anton', fontSize: Math.min(84, 640 / Math.max(4, e.remate.length * 0.5)), lineHeight: 1, color: c.acento, border: `10px solid ${c.acento}`, borderRadius: 14, padding: '6px 26px 10px', transform: 'rotate(7deg)', transformOrigin: 'top right', background: `${c.papel}F2`, letterSpacing: 2}}>{e.remate}</div>
    </div>
  );
};

const EscenaVox: React.FC<{e: Escena; c: Colores; indice: number; f: number; real: number}> = ({e, c, indice, f, real}) => {
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
      {e.planos && e.planos.length > 0
        ? <Planos e={e} c={c} f={f} real={real} indice={indice} arriba={finTitular + 62} />
        : <Sticker e={e} c={c} f={f} indice={indice} arriba={finTitular + 62} />}
      <Remate e={e} c={c} f={f} real={real} arriba={finTitular + 62} />
      <div style={{position: 'absolute', inset: 0, zIndex: 3}}><Nota e={e} c={c} f={f} indice={indice} /></div>
      {e.fuente && <div style={{position: 'absolute', right: W - SEGURO.der, top: SEGURO.arriba + 30, maxWidth: 520, textAlign: 'right', fontFamily: 'Caveat', fontSize: 42, lineHeight: 1, color: c.tinta}}>Fuente: {e.fuente}</div>}
    </div>
  );
};

/** Subtítulos por palabra con los tiempos reales de la narración (nunca repartidos a mano). */
const Subtitulos: React.FC<{palabras: Palabra[]; c: Colores; fuente: string; etiqueta?: string}> = ({palabras, c, fuente, etiqueta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const grupos = React.useMemo(() => {
    const g: Palabra[][] = [];
    let actual: Palabra[] = [];
    for (const p of palabras) {
      const letras = actual.reduce((n, x) => n + x.t.length + 1, 0) + p.t.length;
      const pausa = actual.length > 0 && p.a - actual[actual.length - 1].b > 0.35;
      const otraVoz = actual.length > 0 && !!p.c !== !!actual[actual.length - 1].c;
      if (actual.length > 0 && (actual.length >= 3 || letras > (fuente === 'Anton' ? 18 : 15) || pausa || otraVoz)) {
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
  // La voz de comentario se distingue a la vista: caja invertida y etiqueta. Opinión y dato no se confunden.
  const opina = !!grupo[0].c;
  return (
    <div style={{position: 'absolute', left: SEGURO.izq, width: SEGURO.der - SEGURO.izq, top: 1320, display: 'flex', justifyContent: 'center'}}>
      <div style={{position: 'relative', display: 'flex', gap: 16, background: opina ? c.tinta : c.papel, padding: '10px 22px 14px', boxShadow: `9px 9px 0 ${opina ? c.acento : c.tinta}`, border: `5px solid ${c.tinta}`, transform: `rotate(${i % 2 ? 1 : -1}deg)`}}>
        {opina && etiqueta && <div style={{position: 'absolute', left: -14, top: -40, fontFamily: 'Anton', fontSize: 32, lineHeight: 1, letterSpacing: 2, color: c.papel, background: c.acento, padding: '5px 14px 7px', transform: 'rotate(-3deg)'}}>{etiqueta}</div>}
        {grupo.map((p, k) => {
          const dicha = t >= p.a - 0.04;
          const activa = dicha && t < p.b + 0.06;
          const golpe = spring({frame: frame - Math.round((p.a - 0.04) * fps), fps, config: {damping: 17, stiffness: 240, mass: 0.6}});
          return (
            <span key={k} style={{fontFamily: fuente, fontWeight: fuente === 'Anton' ? 400 : 700, fontSize: fuente === 'Anton' ? 74 : 62, lineHeight: fuente === 'Anton' ? 1.05 : 1.2, textTransform: 'uppercase', color: activa ? c.papel : dicha ? (opina ? c.papel : c.tinta) : `${opina ? c.papel : c.tinta}${opina ? '66' : '38'}`, background: activa ? c.acento : 'transparent', padding: '0 10px', transform: `scale(${activa ? interpolate(golpe, [0, 1], [0.8, 1]) : 1})`, display: 'inline-block'}}>
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
        {t > 0.001 && <path d="M8 30 C 60 10, 110 40, 128 100 M128 100 l -30 -10 M128 100 l 6 -32" fill="none" stroke={c.tinta} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />}
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
              <EscenaVox e={e} c={c} indice={i} f={f} real={frame - e.desde} />
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
      {v.palabras.length > 0 && <Subtitulos palabras={v.palabras} c={c} fuente={v.perfil.subtitulos && FUENTES[v.perfil.subtitulos] ? v.perfil.subtitulos : 'Anton'} etiqueta={v.etiquetaComentario} />}
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
          {e.sonido && <Audio src={staticFile(`sfx/${e.sonido}.wav`)} from={Math.max(0, e.desde + (e.remate ? (e.remateEn != null ? e.remateEn : Math.round(e.dur * 0.55) - desfase(e, i) - 1) : i === 0 ? 2 : 12))} volume={v.volEfecto ?? 0.42} />}
          {e.resaltar && i > 0 && !e.sonido && <Audio src={staticFile('sfx/marcador.wav')} from={e.desde + 10} volume={0.22} />}
          {(e.planos ?? []).map((p, j) => (
            <React.Fragment key={j}>
              {j > 0 && <Audio src={staticFile(`sfx/${['papel', 'pop', 'deslizar'][j % 3]}.wav`)} from={e.desde + p.desde} volume={0.2} />}
              {p.tipo === 'cita' && p.resaltar && !(i === 0 && j === 0) && <Audio src={staticFile('sfx/marcador.wav')} from={e.desde + p.desde + (j === 0 ? 4 : 12)} volume={0.2} />}
              {p.tipo === 'lista' && (p.items ?? []).map((it, m) => m > 0 && <Audio key={m} src={staticFile('sfx/pop.wav')} from={e.desde + it.desde} volume={0.14} />)}
              {[...(p.pasos ?? []), ...(p.hitos ?? []), ...(p.barras ?? [])].map((it, m) => m > 0 && <Audio key={`m${m}`} src={staticFile('sfx/pop.wav')} from={e.desde + it.desde} volume={0.14} />)}
              {(p.etiquetas ?? []).map((it, m) => <Audio key={`e${m}`} src={staticFile('sfx/pop.wav')} from={e.desde + it.desde} volume={0.14} />)}
              {p.apunte && <Audio src={staticFile('sfx/marcador.wav')} from={e.desde + p.apunte.desde} volume={0.16} />}
              {p.junto && <Audio src={staticFile('sfx/pop.wav')} from={e.desde + p.junto.desde} volume={0.18} />}
            </React.Fragment>
          ))}
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
