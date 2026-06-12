'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { STRINGS_HI } from '@/lib/strings_hi';
import { fetchApi } from '@/lib/api';
import VoiceRecorder from '@/components/VoiceRecorder';
import WhatsAppChatPanel from '@/components/WhatsAppChatPanel';
import AgentPipelineTrace from '@/components/AgentPipelineTrace';
import JobCard from '@/components/JobCard';

export default function WorkerOnboarding() {
  const [messages, setMessages] = useState([{ role: 'bot', text: 'नमस्ते! कृपया अपना परिचय दें। आप क्या काम करते हैं, कहाँ रहते हैं और कितना अनुभव है?' }]);
  const [textInput, setTextInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [pipelineFinished, setPipelineFinished] = useState(false);
  const router = useRouter();

  // POST-PIPELINE STATE
  const [workerProfile, setWorkerProfile] = useState<any>(null);
  const [jobMatches, setJobMatches] = useState<any[]>([]);
  const [resumePath, setResumePath] = useState<string | null>(null);
  const [interviewTips, setInterviewTips] = useState<string[]>([]);

  // LOGGING: UI State update
  useEffect(() => {
    console.log("[UI] State Updated:", { workerProfile, jobMatches, resumePath, interviewTips });
  }, [workerProfile, jobMatches, resumePath, interviewTips]);

  const startPipeline = async (formData: FormData) => {
    console.log("[Pipeline Start] Starting new onboarding pipeline...");
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
      console.log("[Pipeline Start] Session ID:", data.session_id);
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

  // LOGGING & STATE EXTRACT: Each stage completion
  const handleAgentCompleted = (agent: string, data: any) => {
    console.log(`[Stage Completion] ${agent}:`, data);
    if (agent === 'skill_extractor' && data) {
      // data = { name, city, skill, years_exp } from _agent_output
      setWorkerProfile(data);
      console.log(`[UI] Worker profile set: name=${data.name}, city=${data.city}, skill=${data.skill}`);
    } else if (agent === 'resume_builder' && data?.pdf_path) {
      // pdf_path is now a server-relative URL e.g. /resumes/abc_v1.pdf
      setResumePath(data.pdf_path);
      console.log(`[UI] Resume path set: ${data.pdf_path}`);
    }
  };

  // LOGGING & STATE EXTRACT: Final Payload (gate_reached)
  const handleGateReached = (data: any) => {
    console.log("[Final Payload Received] gate_reached:", JSON.stringify(data, null, 2));
    
    if (data.matched_jobs && Array.isArray(data.matched_jobs)) {
      console.log(`[UI] ${data.matched_jobs.length} job matches received:`, data.matched_jobs.map((j: any) => `${j.title} (${j.match_score}%)`));
      setJobMatches(data.matched_jobs);
    }
    if (data.interview_tips && Array.isArray(data.interview_tips)) {
      console.log(`[UI] ${data.interview_tips.length} interview tips received`);
      setInterviewTips(data.interview_tips);
    }
    // Prefer resume_pdf_path from gate_reached (it's the server-relative URL)
    if (data.resume_pdf_path) {
      setResumePath(data.resume_pdf_path);
      console.log(`[UI] Resume URL set from gate_reached: ${data.resume_pdf_path}`);
    }
    
    setPipelineFinished(true);
    setMessages(prev => [...prev, { role: 'bot', text: '✅ आपकी प्रोफाइल पूरी हो गई है! अब आप अपनी प्रोफाइल, रेज़्यूमे और नौकरियां देख सकते हैं।' }]);
  };

  const handlePipelineComplete = (data: any) => {
    console.log("[Pipeline Complete Payload]:", data);
  };

  const handleApply = (job: any) => {
    console.log("Applied to:", job);
    alert(`Applied to ${job.employer_name || 'Contractor'}! Check WhatsApp for status.`);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-6 text-center">
        <h1 className="text-3xl font-bold">{STRINGS_HI.onboarding.title}</h1>
        <p className="text-gray-400 mt-2">{STRINGS_HI.onboarding.subtitle}</p>
      </div>

      <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6 min-h-0">
        
        {/* Left/Center Column */}
        <div className="md:col-span-2 flex flex-col gap-4 overflow-y-auto pr-2 pb-10">
          
          {workerProfile && (
            <div className="bg-[#1C1C1E] p-4 rounded-xl border border-[#F77A02]/30 flex justify-between items-center shadow-[0_0_15px_rgba(247,122,2,0.1)]">
              <div>
                <h3 className="text-[#F77A02] font-bold text-lg">👷 {workerProfile.name || 'Worker'}</h3>
                <p className="text-gray-300 text-sm">
                  {workerProfile.skill?.replace(/_/g, ' ').toUpperCase()} • {workerProfile.years_exp} Yrs Exp • {workerProfile.city}
                  {workerProfile.wage ? ` • ₹${workerProfile.wage}/day` : ''}
                </p>
              </div>
              {resumePath && (
                <a 
                  href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${resumePath}`} 
                  target="_blank" 
                  className="bg-[#222225] border border-[#F77A02] text-[#F77A02] hover:bg-[#F77A02] hover:text-white px-4 py-2 rounded-lg font-bold transition-colors"
                >
                  📄 Download Resume
                </a>
              )}
            </div>
          )}

          <div className="flex-1 min-h-[350px]">
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
          
          {/* Post-Pipeline: Job Matches */}
          {jobMatches.length > 0 && (
            <div className="mt-4">
              <h2 className="text-xl font-bold text-white mb-4">💼 Matched Jobs</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {jobMatches.map((job, idx) => (
                  <JobCard key={idx} job={job} onApply={handleApply} />
                ))}
              </div>
            </div>
          )}

          {/* Post-Pipeline: Interview Tips */}
          {interviewTips.length > 0 && (
            <div className="mt-4 bg-[#1C1C1E] p-5 rounded-xl border border-[#331E0C] shadow-lg">
              <h2 className="text-xl font-bold text-[#F77A02] mb-3">💬 Interview Tips</h2>
              <ul className="space-y-2">
                {interviewTips.map((tip, idx) => (
                  <li key={idx} className="text-gray-200 flex items-start gap-2">
                    <span className="text-[#F77A02] mt-0.5">💡</span> {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {pipelineFinished && (
            <button 
              onClick={() => router.push('/worker/dashboard')}
              className="w-full mt-4 bg-[#F77A02] hover:bg-[#E06A00] text-white font-bold py-4 rounded-xl shadow-[0_0_20px_rgba(247,122,2,0.3)] transition-all"
            >
              डैशबोर्ड पर जाएँ (Go to Dashboard) ➔
            </button>
          )}
        </div>

        {/* Right Column: Pipeline Trace */}
        <div className="overflow-y-auto">
          {sessionId ? (
            <AgentPipelineTrace 
              sessionId={sessionId} 
              onGateReached={handleGateReached}
              onAgentCompleted={handleAgentCompleted}
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
