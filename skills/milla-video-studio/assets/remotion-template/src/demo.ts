import type {Manifest} from './types';

// Synthetic editorial text, no legal advice, no invented voice or caption timing.
// This is a layout fixture, not a recovered or approved MILLA video.
export const demo: Manifest = {
  schema_version: 1,
  project: {id: 'technical-demo', title: 'Plantilla nueva: demostración técnica'},
  output: {width: 1080, height: 1920, fps: 30, durationSeconds: 10.4},
  quality: {particles_allowed: false, watermarks_allowed: false, allowed_image_providers: ['kie'], minimum_transition_families: 4},
  assets: [],
  branding: {name: 'MILLA ABOGADOS', footer: 'Demostración técnica · pendiente de aprobación'},
  subtitleCues: [],
  subtitlesVerified: false,
  scenes: [
    {id: 'brief', start: 0, end: 2.4, asset_ids: [], title: 'Cada video empieza con una idea clara.', kicker: '01 · ENFOQUE', body: 'Define a quién hablas y qué quieres explicar.', transition: {family: 'fade', durationSeconds: 0}, diagram: {nodes: [{id: 'a', label: 'Audiencia', x: 22, y: 30}, {id: 'b', label: 'Mensaje', x: 78, y: 70}], edges: [{from: 'a', to: 'b'}]}},
    {id: 'research', start: 2, end: 4.4, asset_ids: [], title: 'Investiga antes de afirmar.', kicker: '02 · FUENTES', transition: {family: 'wipe', durationSeconds: 0.4}, diagram: {nodes: [{id: 'a', label: 'Fuente', x: 22, y: 30}, {id: 'b', label: 'Verificación', x: 78, y: 70}], edges: [{from: 'a', to: 'b'}]}},
    {id: 'voice', start: 4, end: 6.4, asset_ids: [], title: 'Primero escucha. Después produce.', kicker: '03 · VOZ', body: 'La voz necesita una muestra escuchada y aprobada.', transition: {family: 'push', durationSeconds: 0.4}},
    {id: 'visuals', start: 6, end: 8.4, asset_ids: [], title: 'La imagen ayuda a entender.', kicker: '04 · COMPOSICIÓN', transition: {family: 'mask', durationSeconds: 0.4}, diagram: {nodes: [{id: 'a', label: 'Idea', x: 22, y: 30}, {id: 'b', label: 'Diagrama', x: 78, y: 70}], edges: [{from: 'a', to: 'b'}]}},
    {id: 'review', start: 8, end: 10.4, asset_ids: [], theme: 'navy', title: 'Revisa el archivo que vas a entregar.', kicker: '05 · CONTROL FINAL', body: 'La plantilla no sustituye la escucha ni la inspección del MP4.', transition: {family: 'depth', durationSeconds: 0.4}},
  ],
};
