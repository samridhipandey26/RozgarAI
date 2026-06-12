// frontend/src/components/AgentPipelineTrace.tsx
'use client';

import { useEffect, useState } from 'react';

const AGENTS = [
  { id: 'voice_intake', label: 'Voice Intake', icon: '🎙️' },
  { id: 'skill_extractor', label: 'Skill Extractor', icon: '🧠' },
  { id: 'resume_builder', label: 'Resume Builder', icon: '📄' },
  { id: 'job_matcher', label: 'Job Matcher', icon: '🔍' },
  { id: 'interview_coach', label: 'Interview Coach', icon: '💬' },
];

interface TraceProps {
  sessionId: string;
  onGateReached?: (data: any) => void;
  onComplete?: (data: any) => void;
}

export default function AgentPipelineTrace({ sessionId, onGateReached, onComplete }: TraceProps) {
  const [events, setEvents] = useState<any[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [completedAgents, setCompletedAgents] = useState(new Set<string>());
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const source = new EventSource(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/pipeline/stream/${sessionId}`);

    source.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);

      if (data.event === 'agent_started') {
        setActiveAgent(data.agent);
      } else if (data.event === 'agent_completed') {
        setCompletedAgents(prev => new Set(prev).add(data.agent));
        if (data.agent === 'interview_coach') setActiveAgent(null); // End of phase 1
      } else if (data.event === 'gate_reached') {
        setActiveAgent(null);
        if (onGateReached) onGateReached(data.data);
      } else if (data.event === 'pipeline_done') {
        source.close();
        if (onComplete) onComplete(data.data);
      } else if (data.event === 'pipeline_error') {
        setError(data.data?.error || 'Pipeline failed');
        source.close();
      }
    };

    source.onerror = (err) => {
      console.error('SSE Error', err);
      setError('Connection lost to pipeline');
      source.close();
    };

    return () => source.close();
  }, [sessionId, onGateReached, onComplete]);

  return (
    <div className="bg-[#1C1C1E] rounded-xl p-6 border border-[#333]">
      <h3 className="text-white font-bold text-lg mb-4">Pipeline Status</h3>
      
      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-200 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {AGENTS.map((agent) => {
          const isCompleted = completedAgents.has(agent.id);
          const isActive = activeAgent === agent.id;
          
          return (
            <div key={agent.id} className={`flex items-center p-3 rounded-lg border transition-all ${
              isActive ? 'bg-[#331E0C] border-[#F77A02]' : 
              isCompleted ? 'bg-[#222225] border-[#333] opacity-70' : 
              'bg-[#222225] border-transparent opacity-40'
            }`}>
              <div className="text-2xl mr-4">{agent.icon}</div>
              <div className="flex-1">
                <div className={`font-bold ${isActive ? 'text-[#F77A02]' : 'text-white'}`}>
                  {agent.label}
                </div>
                <div className="text-xs text-gray-500">
                  {isActive ? 'Processing...' : isCompleted ? 'Completed' : 'Waiting...'}
                </div>
              </div>
              {isCompleted && <div className="text-green-500">✓</div>}
              {isActive && (
                <div className="w-4 h-4 rounded-full border-2 border-[#F77A02] border-t-transparent animate-spin"></div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
