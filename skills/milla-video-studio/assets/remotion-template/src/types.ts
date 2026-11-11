export type TransitionFamily = 'wipe' | 'push' | 'mask' | 'depth' | 'pan' | 'zoom' | 'fade';

export type Asset = {
  id: string;
  path: string;
  kind: 'image' | 'audio' | 'video' | 'font' | 'graphic';
  provider?: string;
  model?: string;
  sha256?: string;
  discovery_provider?: string;
  source: {type: 'generated' | 'licensed' | 'owned' | 'code'; url?: string; license?: string; rights_confirmed?: boolean};
  qa: {watermark: false; third_party_logo: false; particles: false; approved?: boolean};
};
export type Diagram = {
  nodes: Array<{id: string; label: string; x: number; y: number}>;
  edges: Array<{from: string; to: string; label?: string}>;
};
/** Plano: lo que se ve dentro de una escena desde el segundo `at` (tomado de la voz real). */
export type Beat = {
  at: number; anchor?: string; note?: {text: string; at?: number};
} & (
  | {kind: 'quote'; text: string; highlight?: string; source: string}
  | {kind: 'list'; items: Array<{text: string; mark?: 'yes' | 'no'; at?: number}>}
  | {kind: 'calendar'; days?: number; cells?: Array<{label: string; state?: 'crossed' | 'marked'}>; caption?: string}
  | {kind: 'figure'; value: string; caption?: string; strike?: boolean}
  | {kind: 'timeline'; milestones: Array<{date: string; text: string; at?: number}>}
  | {kind: 'bars'; bars: Array<{label: string; value: number; text?: string; at?: number}>; source: string}
  | {kind: 'image'; asset_id: string}
);
export type Scene = {
  beats?: Beat[];
  id: string;
  start: number;
  end: number;
  asset_ids: [] | [string] | [string, string] | [string, string, string];
  title: string;
  kicker?: string;
  body?: string;
  theme?: 'ivory' | 'navy';
  kind?: never;
  transition: {family: TransitionFamily; durationSeconds: number};
  diagram?: Diagram;
};
export type Manifest = {
  schema_version: 1;
  project: {id: string; title: string};
  output: {width: 1080; height: 1920; fps: 30; durationSeconds: number};
  quality: {
    particles_allowed: false;
    watermarks_allowed: false;
    allowed_image_providers: ['kie'];
    minimum_transition_families: number;
    transition_variety_rationale?: string;
  };
  assets: Asset[];
  scenes: Scene[];
  subtitleCues?: Array<{start: number; end: number; text: string; words?: Array<{start: number; end: number; text: string}>}>;
  subtitlesVerified?: boolean;
  wordTimestampsVerified?: boolean;
  voice?: {provider?: string; reference_id?: string; approval?: {status: string}};
  audio?: {
    voice?: string;
    music?: string;
    voiceVolume?: number;
    musicVolume?: number;
    sfx?: Array<{asset_id: string; start: number; volume?: number; duration?: number}>;
  };
  branding?: {name?: string; footer?: string};
};
