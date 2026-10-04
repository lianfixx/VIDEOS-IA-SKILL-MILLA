import React from 'react';
import {Composition, type CalculateMetadataFunction} from 'remotion';
import {MillaVideo} from './MillaVideo';
import {demo} from './demo';
import type {Manifest} from './types';
import {validateManifest} from './manifest-validation.mjs';

const calculateMetadata: CalculateMetadataFunction<Manifest> = ({props}) => {
  const {total} = validateManifest(props);
  return {durationInFrames: total, width: 1080, height: 1920, fps: 30, defaultCodec: 'h264', defaultPixelFormat: 'yuv420p', props};
};
export const Root: React.FC = () => <Composition id="MillaVideo" component={MillaVideo} durationInFrames={312} width={1080} height={1920} fps={30} defaultProps={demo} calculateMetadata={calculateMetadata} />;
