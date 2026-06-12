// frontend/src/components/VoiceRecorder.tsx
'use client';

import { useState, useRef } from 'react';
import { STRINGS_HI } from '../lib/strings_hi';

interface RecorderProps {
  onRecordingComplete: (file: File) => void;
}

export default function VoiceRecorder({ onRecordingComplete }: RecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const file = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
        onRecordingComplete(file);
        
        // Cleanup
        stream.getTracks().forEach(track => track.stop());
        if (timerRef.current) clearInterval(timerRef.current);
        setRecordingTime(0);
      };

      mediaRecorder.start();
      setIsRecording(true);
      
      // Timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Microphone access is required to record voice.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col items-center">
      {isRecording ? (
        <div className="flex flex-col items-center animate-pulse">
          <div className="text-red-500 font-bold mb-2">Recording: {formatTime(recordingTime)}</div>
          <button 
            onClick={stopRecording}
            className="bg-red-600 hover:bg-red-700 text-white rounded-full w-24 h-24 flex items-center justify-center shadow-[0_0_20px_rgba(220,38,38,0.5)] transition-all"
          >
            <span className="text-3xl">⏹</span>
          </button>
          <div className="mt-4 text-gray-400 text-sm">Click to stop and submit</div>
        </div>
      ) : (
        <div className="flex flex-col items-center">
          <button 
            onClick={startRecording}
            className="bg-[#F77A02] hover:bg-[#E06A00] text-white rounded-full w-24 h-24 flex items-center justify-center shadow-[0_0_20px_rgba(247,122,2,0.4)] transition-all transform hover:scale-105"
          >
            <span className="text-3xl">🎤</span>
          </button>
          <div className="mt-4 text-white font-bold">{STRINGS_HI.onboarding.voiceButton}</div>
        </div>
      )}
    </div>
  );
}
