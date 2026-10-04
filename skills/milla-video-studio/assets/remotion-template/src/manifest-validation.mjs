// Rendering guards, independent from React. The Python project validator adds
// file hashes, provenance and human approval; this module cannot replace it.
export const supportedFamilies = ['wipe', 'push', 'mask', 'depth', 'pan', 'zoom', 'fade'];
export const frameOf = (seconds, fps = 30) => Math.round(seconds * fps);
const fail = (message) => { throw new Error(`MILLA render: ${message}`); };
const finite = (n) => typeof n === 'number' && Number.isFinite(n);
const requiredText = (text, limit, label) => {
  if (typeof text !== 'string' || !text.trim() || text.length > limit) fail(`${label}: texto vacío o más de ${limit} caracteres.`);
};
export const isSafeAssetPath = (path) => typeof path === 'string' && path.length > 0 &&
  !/^(?:[a-z][a-z0-9+.-]*:|\/|\\)/i.test(path) && !path.includes('\\') &&
  !path.split('/').some((part) => part === '..' || part === '.' || !part) &&
  !/[?#%\x00-\x1f]/.test(path);

export function validateManifest(m) {
  if (!m || m.schema_version !== 1) fail('schema_version debe ser 1.');
  if (m.output?.width !== 1080 || m.output?.height !== 1920 || m.output?.fps !== 30) fail('La plantilla usa 1080×1920 a 30 fps.');
  if (!finite(m.output.durationSeconds) || m.output.durationSeconds <= 0) fail('Duración total inválida.');
  const fps = m.output.fps;
  const total = frameOf(m.output.durationSeconds, fps);
  if (!Number.isSafeInteger(total) || total < 1) fail('La duración debe producir una cantidad positiva y segura de frames.');
  if (m.quality?.particles_allowed !== false || m.quality?.watermarks_allowed !== false) fail('Prohibir partículas y marcas de agua explícitamente.');
  const transitionMinimum = m.quality?.minimum_transition_families;
  if (!Number.isInteger(transitionMinimum) || transitionMinimum < 1 || transitionMinimum > supportedFamilies.length) fail('minimum_transition_families debe ser entero entre 1 y las familias implementadas; el perfil usa 4.');
  if (transitionMinimum < 4 && (typeof m.quality?.transition_variety_rationale !== 'string' || !m.quality.transition_variety_rationale.trim())) fail('Reducir el valor predeterminado de 4 requiere transition_variety_rationale.');
  if (JSON.stringify(m.quality?.allowed_image_providers) !== JSON.stringify(['kie'])) fail('allowed_image_providers debe conservar solo Kie para recursos generados.');
  if (!Array.isArray(m.assets) || !Array.isArray(m.scenes) || !m.scenes.length) fail('Faltan assets o escenas.');
  const assets = new Map();
  for (const asset of m.assets) {
    requiredText(asset.id, 100, 'asset.id');
    if (assets.has(asset.id)) fail(`Asset duplicado: ${asset.id}.`);
    if (!isSafeAssetPath(asset.path)) fail(`Ruta local insegura: ${asset.id}. Usar rutas relativas a public/.`);
    if (asset.qa?.watermark !== false || asset.qa?.third_party_logo !== false || asset.qa?.particles !== false) fail(`Asset ${asset.id}: QA debe descartar marca de agua, logo de tercero y partículas.`);
    if (asset.kind === 'image') {
      const generated = asset.provider === 'kie' && asset.source?.type === 'generated';
      const realPhoto = asset.provider === 'real-photo' && ['licensed', 'owned'].includes(asset.source?.type) && asset.source?.rights_confirmed === true;
      if (!generated && !realPhoto) fail(`Imagen ${asset.id}: usar Kie generado o real-photo con derechos licenciados/propios.`);
    }
    assets.set(asset.id, asset);
  }
  const ids = new Set();
  const usedImages = new Set();
  const usedImagePaths = new Set();
  const usedImageHashes = new Set();
  const families = new Set();
  const scenes = m.scenes.map((scene, i) => {
    requiredText(scene.id, 100, 'scene.id');
    requiredText(scene.title, 74, `${scene.id}.title`);
    if (scene.kicker != null) requiredText(scene.kicker, 48, `${scene.id}.kicker`);
    if (scene.body != null) requiredText(scene.body, 145, `${scene.id}.body`);
    if (Object.prototype.hasOwnProperty.call(scene, 'theme') && !['ivory', 'navy'].includes(scene.theme)) fail(`${scene.id}.theme: usar ivory o navy.`);
    if (Object.prototype.hasOwnProperty.call(scene, 'kind')) fail(`${scene.id}.kind no está implementado; usar asset_ids/body/diagram.`);
    if (ids.has(scene.id)) fail(`Escena duplicada: ${scene.id}.`);
    ids.add(scene.id);
    if (!finite(scene.start) || !finite(scene.end) || scene.start < 0 || scene.end <= scene.start) fail(`Tiempo inválido: ${scene.id}.`);
    const start = frameOf(scene.start, fps);
    const end = frameOf(scene.end, fps);
    if (end <= start || end > total) fail(`Escena fuera de composición: ${scene.id}.`);
    if (i === 0 && start !== 0) fail('La primera escena debe comenzar en frame 0.');
    if (!finite(scene.transition?.durationSeconds) || scene.transition.durationSeconds < 0) fail(`Solapamiento inválido: ${scene.id}.`);
    const overlap = frameOf(scene.transition.durationSeconds, fps);
    if (!supportedFamilies.includes(scene.transition?.family)) fail(`Transición no implementada: ${scene.transition?.family}. No sustituir silenciosamente.`);
    if (!finite(overlap) || overlap < 0 || overlap >= end - start) fail(`Solapamiento inválido: ${scene.id}.`);
    if (i === 0 && overlap !== 0) fail('Primera escena: durationSeconds debe ser 0.');
    if (i > 0) {
      if (overlap < 2) fail(`Transición ${scene.id}: se requieren al menos 2 frames solapados.`);
      const previous = m.scenes[i - 1];
      const previousStart = frameOf(previous.start, fps);
      const previousEnd = frameOf(previous.end, fps);
      if (start <= previousStart || end <= previousEnd) fail('Las escenas deben avanzar en inicio y final.');
      // Incoming must be fully opaque before the outgoing layer disappears.
      if (previousEnd < start + overlap) fail(`Hueco/destello potencial antes de ${scene.id}: extender escena anterior hasta start + transición.`);
      if (i > 1 && scene.transition.family === previous.transition.family) fail('No repetir familia en transiciones consecutivas.');
      families.add(scene.transition.family);
    }
    if (!Array.isArray(scene.asset_ids) || scene.asset_ids.length > 3) fail(`${scene.id}: usar 0..3 imágenes; diagramas son nativos.`);
    for (const id of scene.asset_ids) {
      const asset = assets.get(id);
      if (!asset || asset.kind !== 'image') fail(`${scene.id}: ${id} debe ser una imagen registrada.`);
      if (usedImages.has(id)) fail(`Imagen repetida entre escenas: ${id}.`);
      if (usedImagePaths.has(asset.path) || (asset.sha256 && usedImageHashes.has(asset.sha256))) fail(`Imagen repetida bajo otro ID: ${id}.`);
      usedImages.add(id);
      usedImagePaths.add(asset.path);
      if (asset.sha256) usedImageHashes.add(asset.sha256);
    }
    if (scene.diagram && scene.asset_ids.length && scene.body) fail(`${scene.id}: imagen + diagrama + body exceden las zonas seguras. Separar el body en otra escena o quitarlo.`);
    if (scene.diagram) validateDiagram(scene.diagram, scene.id);
    return {start, end, overlap};
  });
  if (scenes.at(-1).end !== total) fail('La última escena debe cubrir hasta el último frame; no desvanecerla al vacío.');
  const changes = Math.max(0, scenes.length - 1);
  if (changes >= 5 && families.size < transitionMinimum) fail(`Se requieren ${transitionMinimum} familias diferentes para 5 o más cambios.`);
  let cueEnd = -1;
  for (const cue of m.subtitleCues ?? []) {
    if (m.subtitlesVerified !== true) fail('Los cues requieren verificación con el audio real; no inferir tiempos por palabras.');
    requiredText(cue.text, 85, 'subtitleCues.text');
    if (!finite(cue.start) || !finite(cue.end) || cue.start < 0 || cue.end <= cue.start || cue.end > m.output.durationSeconds) fail('Cue fuera de tiempo.');
    const a = frameOf(cue.start, fps);
    const b = frameOf(cue.end, fps);
    if (b <= a || a < cueEnd) fail('Cues solapados, desordenados o menores de un frame.');
    cueEnd = b;
    if (cue.words != null) {
      if (!Array.isArray(cue.words) || !cue.words.length) fail('words debe contener tiempos reales de palabras o estar ausente.');
      if (m.wordTimestampsVerified !== true) fail('El resaltado requiere tiempos de palabra verificados sobre el audio real.');
      const normalized = (text) => text.trim().replace(/\s+/g, ' ');
      if (normalized(cue.words.map((word) => word.text).join(' ')) !== normalized(cue.text)) fail('Las palabras deben reproducir exactamente el texto del cue.');
      let wordEnd = a;
      for (const word of cue.words) {
        requiredText(word.text, 40, 'subtitleCues.words.text');
        if (!finite(word.start) || !finite(word.end) || word.start < cue.start || word.end > cue.end || word.end <= word.start) fail('Palabra fuera del intervalo del cue.');
        const wa = frameOf(word.start, fps); const wb = frameOf(word.end, fps);
        if (wa < wordEnd || wb <= wa) fail('Palabras solapadas, desordenadas o menores de un frame.');
        wordEnd = wb;
      }
    }
  }
  const audioAsset = (id) => { if (id && assets.get(id)?.kind !== 'audio') fail(`Audio inexistente: ${id}.`); };
  audioAsset(m.audio?.voice);
  audioAsset(m.audio?.music);
  for (const value of [m.audio?.voiceVolume, m.audio?.musicVolume]) {
    if (value != null && (!finite(value) || value < 0 || value > 1)) fail('Volumen debe estar entre 0 y 1.');
  }
  for (const effect of m.audio?.sfx ?? []) {
    requiredText(effect.asset_id, 100, 'sfx.asset_id');
    audioAsset(effect.asset_id);
    if (!finite(effect.start) || effect.start < 0 || frameOf(effect.start, fps) >= total) fail('SFX fuera de composición.');
    if (effect.volume != null && (!finite(effect.volume) || effect.volume < 0 || effect.volume > 1)) fail('Volumen SFX inválido.');
    if (effect.duration != null && (!finite(effect.duration) || effect.duration <= 0 || frameOf(effect.duration, fps) < 1)) fail('Duración SFX inválida.');
  }
  if (m.fontAssetId) fail('Esta plantilla base usa fuentes del sistema. Integrar carga bloqueante y verificar métricas antes de habilitar fontAssetId.');
  return {total, scenes};
}

function validateDiagram(diagram, sceneId) {
  if (!Array.isArray(diagram.nodes) || !Array.isArray(diagram.edges) || !diagram.nodes.length || diagram.nodes.length > 6) fail(`${sceneId}: diagrama requiere 1..6 nodos.`);
  const nodes = new Map();
  for (const node of diagram.nodes) {
    requiredText(node.id, 64, 'diagram.node.id');
    requiredText(node.label, 28, 'diagram.node.label');
    if (nodes.has(node.id) || !finite(node.x) || !finite(node.y) || node.x < 15 || node.x > 85 || node.y < 15 || node.y > 85) fail(`${sceneId}: nodo duplicado o fuera del margen 15..85.`);
    for (const other of nodes.values()) {
      if (Math.abs(node.x - other.x) * 8.4 < 214 && Math.abs(node.y - other.y) * 4.8 < 102) fail(`${sceneId}: nodos de diagrama se superponen.`);
    }
    nodes.set(node.id, node);
  }
  for (const edge of diagram.edges) {
    if (!nodes.has(edge.from) || !nodes.has(edge.to) || edge.from === edge.to) fail(`${sceneId}: arista con nodo desconocido o bucle.`);
    if (edge.label != null) requiredText(edge.label, 24, 'diagram.edge.label');
  }
}
