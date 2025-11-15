/**
 * WebRTC utility functions
 * Helper functions for managing WebRTC peer connections and audio
 */

/**
 * Creates and configures an audio element for playback
 *
 * @returns Configured HTML audio element
 */
export function createAudioElement(): HTMLAudioElement {
  const audio = document.createElement('audio');
  audio.autoplay = true;
  return audio;
}

/**
 * Handles incoming track from peer connection
 * Sets up audio playback when remote track is received
 *
 * @param event - The RTCTrackEvent from peer connection
 * @param audioElement - The audio element to play the track
 */
export function handleIncomingTrack(event: RTCTrackEvent, audioElement: HTMLAudioElement | null): void {
  console.log('Received remote track:', event.track.kind);

  if (event.track.kind === 'audio' && audioElement) {
    audioElement.srcObject = event.streams[0];
    audioElement.play().catch(console.error);
  }
}

/**
 * Gets user media with optimal audio settings for voice
 *
 * @returns Promise resolving to MediaStream with audio track
 */
export async function getUserAudioStream(): Promise<MediaStream> {
  return await navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
  });
}

/**
 * Adds audio tracks from stream to peer connection
 *
 * @param peerConnection - The RTCPeerConnection to add tracks to
 * @param stream - The MediaStream containing audio tracks
 */
export function addAudioTracks(peerConnection: RTCPeerConnection, stream: MediaStream): void {
  stream.getTracks().forEach((track) => {
    peerConnection.addTrack(track, stream);
  });
}

/**
 * Stops all tracks in a media stream
 *
 * @param stream - The MediaStream to stop
 */
export function stopMediaStream(stream: MediaStream | null): void {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }
}

/**
 * Stops audio playback and clears the audio element
 *
 * @param audioElement - The audio element to stop and clear
 */
export function stopAudioPlayback(audioElement: HTMLAudioElement | null): void {
  if (audioElement) {
    audioElement.pause();
    audioElement.srcObject = null;
  }
}
