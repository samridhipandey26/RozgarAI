// frontend/src/app/worker/onboarding/page.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { STRINGS_HI } from '@/lib/strings_hi';
import { fetchApi } from '@/lib/api';
import VoiceRecorder from '@/components/VoiceRecorder';
import WhatsAppChatPanel from '@/components/WhatsAppChatPanel';
import AgentPipelineTrace from '@/components/AgentPipelineTrace';

export default function WorkerOnboarding() {
  const [messages, setMessages] = useState([{ role: 'bot', text: 'नमस्ते! कृपया अपना परिचय दें। आप क्या काम करते हैं, कहाँ रहते हैं और कितना अनुभव है?' }]);
  const [textInput, setTextInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [pipelineFinished, setPipelineFinished] = useState(false);
  const router = useRouter();

  // Authentication check would go here

  const startPipeline = async (formData: FormData) => {
    try {
      // Get token for auth header
      const tokenStr = localStorage.getItem('supabase.auth.token');
      const token = tokenStr ? JSON.parse(tokenStr).currentSession?.access_token : '';
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/pipeline/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });
      
      if (!res.ok) throw new Error('Failed to start pipeline');
      const data = await res.json();
      setSessionId(data.session_id);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'bot', text: 'Error starting pipeline.' }]);
    }
  };

  const handleVoiceComplete = (file: File) => {
    setMessages(prev => [...prev, { role: 'worker', text: '🎤 [Voice Message Sent]' }]);
    const formData = new FormData();
    formData.append('audio', file);
    startPipeline(formData);
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!textInput.trim()) return;
    
    setMessages(prev => [...prev, { role: 'worker', text: textInput }]);
    const formData = new FormData();
    formData.append('transcript', textInput);
    startPipeline(formData);
    setTextInput('');
  };

  const handlePipelineComplete = () => {
    setPipelineFinished(true);
    setMessages(prev => [...prev, { role: 'bot', text: '✅ आपकी प्रोफाइल पूरी हो गई है! अब आप नौकरियां देख सकते हैं।' }]);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-6 text-center">
        <h1 className="text-3xl font-bold">{STRINGS_HI.onboarding.title}</h1>
        <p className="text-gray-400 mt-2">{STRINGS_HI.onboarding.subtitle}</p>
      </div>

      <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6 min-h-0">
        
        {/* Chat Panel */}
        <div className="md:col-span-2 flex flex-col gap-4">
          <div className="flex-1 min-h-0">
            <WhatsAppChatPanel messages={messages} />
          </div>
          
          {/* Inputs */}
          {!sessionId && (
            <div className="bg-[#1C1C1E] p-6 rounded-xl border border-[#333] flex flex-col md:flex-row items-center gap-6">
              <div className="flex-1 w-full">
                <VoiceRecorder onRecordingComplete={handleVoiceComplete} />
              </div>
              
              <div className="w-px h-full bg-[#333] hidden md:block"></div>
              <div className="w-full h-px bg-[#333] block md:hidden"></div>
              
              <form onSubmit={handleTextSubmit} className="flex-1 w-full flex flex-col gap-3">
                <textarea
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder={STRINGS_HI.onboarding.textPlaceholder}
                  className="w-full bg-[#0D0D0D] border border-[#333] rounded-lg p-3 text-white focus:border-[#F77A02] focus:ring-1 focus:ring-[#F77A02] outline-none resize-none h-24"
                />
                <button type="submit" className="bg-[#222225] hover:bg-[#333] text-white font-bold py-2 px-4 rounded border border-[#444] transition-colors">
                  {STRINGS_HI.onboarding.submitText}
                </button>
              </form>
            </div>
          )}
          
          {pipelineFinished && (
            <button 
              onClick={() => router.push('/worker/dashboard')}
              className="w-full bg-[#F77A02] hover:bg-[#E06A00] text-white font-bold py-4 rounded-xl shadow-[0_0_20px_rgba(247,122,2,0.3)] transition-all"
            >
              डैशबोर्ड पर जाएँ (Go to Dashboard) ➔
            </button>
          )}
        </div>

        {/* Pipeline Trace */}
        <div className="overflow-y-auto">
          {sessionId ? (
            <AgentPipelineTrace 
              sessionId={sessionId} 
              onComplete={handlePipelineComplete} 
            />
          ) : (
            <div className="bg-[#1C1C1E] rounded-xl p-6 border border-[#333] h-full flex flex-col items-center justify-center text-gray-500 text-center">
              <span className="text-4xl mb-4">⚙️</span>
              <p>अपना परिचय दें। हमारा AI एजेंट आपकी प्रोफाइल तैयार करेगा।</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
