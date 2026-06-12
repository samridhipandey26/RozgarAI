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
      console.log("Requesting microphone...");
      
      // 1. Check if API is available (fixes "not secure" / HTTP issues)
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error("navigator.mediaDevices is undefined. Usually means page is not served over HTTPS or localhost.");
        throw new Error("unavailable");
      }

      // 2. Log current permission state if supported
      try {
        const permStatus = await navigator.permissions.query({ name: 'microphone' as any });
        console.log("Permission state:", permStatus.state);
      } catch (e) {
        console.log("Permissions API not supported by browser", e);
      }

      // 3. Request microphone (triggers browser popup if 'prompt')
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log("Microphone granted");
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        console.log("Recording stopped");
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
      console.log("Recording started");
      
      // Timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err: any) {
      console.error("Error accessing microphone:", err);
      
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        console.log("Microphone denied");
        alert("Microphone access denied. Please allow microphone access in browser settings.\n\nमाइक्रोफोन अनुमति अस्वीकृत है। कृपया ब्राउज़र सेटिंग्स में माइक्रोफोन की अनुमति दें।");
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        alert("No microphone found on this device.\n\nइस डिवाइस पर कोई माइक्रोफ़ोन नहीं मिला।");
      } else if (err.message === "unavailable") {
        alert("Microphone API unavailable. This usually happens if you are connecting over HTTP instead of HTTPS/localhost.\n\nमाइक्रोफ़ोन API अनुपलब्ध है। सुरक्षित कनेक्शन (HTTPS) आवश्यक है।");
      } else {
        alert("Microphone access is required to record voice. Error: " + err.message);
      }
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
