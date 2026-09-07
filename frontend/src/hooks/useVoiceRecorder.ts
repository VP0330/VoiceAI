import { useState, useRef, useCallback } from 'react';

export const useVoiceRecorder = () => {
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);

      audioChunks.current = [];

      recorder.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      recorder.onerror = (event) => {
        console.error('[MediaRecorder] Error:', event.error);
        setError(event.error.toString());
      };

      mediaRecorder.current = recorder;
      recorder.start();
      setIsRecording(true);
      setError(null);
      console.log('[VoiceRecorder] Started');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to start recording';
      console.error('[VoiceRecorder] Error:', errorMsg);
      setError(errorMsg);
      setIsRecording(false);
    }
  }, []);

  const stopRecording = useCallback(
    async (): Promise<Blob | null> => {
      return new Promise((resolve) => {
        if (!mediaRecorder.current) {
          setError('No recording in progress');
          resolve(null);
          return;
        }

        const recorder = mediaRecorder.current;

        recorder.onstop = () => {
          const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
          console.log('[VoiceRecorder] Stopped, audio size:', audioBlob.size);
          setIsRecording(false);

          // Stop all tracks
          recorder.stream.getTracks().forEach((track) => track.stop());
          mediaRecorder.current = null;

          resolve(audioBlob);
        };

        recorder.stop();
      });
    },
    []
  );

  const uploadAudio = useCallback(async (sessionId: string, audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('audio_file', audioBlob, 'audio.wav');

      console.log('[VoiceRecorder] Uploading', audioBlob.size, 'bytes');

      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
      const response = await fetch(`${apiBaseUrl}/api/voice/process`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('[VoiceRecorder] Upload success:', data);
      return data;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Upload failed';
      console.error('[VoiceRecorder] Upload error:', errorMsg);
      setError(errorMsg);
      throw err;
    }
  }, []);

  return {
    isRecording,
    error,
    setError,
    startRecording,
    stopRecording,
    uploadAudio,
  };
};
