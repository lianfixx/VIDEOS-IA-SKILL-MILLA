import React from 'react';
import {Composition, Still} from 'remotion';
import {Portada, Vox, type VideoVox} from './Vox';
import demo from './data/demo.json';

// `npm run render -- --props=src/data/video.json` sustituye el demo por la producción real.
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
  </>
);
