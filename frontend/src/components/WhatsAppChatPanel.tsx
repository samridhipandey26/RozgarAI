// frontend/src/components/WhatsAppChatPanel.tsx
'use client';

import { useEffect, useRef } from 'react';

interface ChatProps {
  messages: Array<{ role: string; text: string }>;
}

export default function WhatsAppChatPanel({ messages }: ChatProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col min-h-full h-full bg-[#111] rounded-xl border border-[#333] overflow-hidden">
      <div className="bg-[#222225] p-4 flex items-center border-b border-[#333]">
        <div className="w-10 h-10 rounded-full bg-[#F77A02] flex items-center justify-center text-white font-bold text-xl mr-3">
          R
        </div>
        <div>
          <div className="font-bold text-white">RozgarAI Agent</div>
          <div className="text-xs text-green-400">Online</div>
        </div>
      </div>
      
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4" style={{ backgroundImage: 'url("https://www.transparenttextures.com/patterns/cubes.png")', backgroundColor: '#0A0A0A' }}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'bot' ? 'justify-start' : 'justify-end'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              msg.role === 'bot' 
                ? 'bg-[#222225] text-white rounded-tl-none border border-[#333]' 
                : 'bg-[#F77A02] text-white rounded-tr-none'
            }`}>
              <div className="whitespace-pre-wrap">{msg.text}</div>
              <div className={`text-[10px] text-right mt-1 ${msg.role === 'bot' ? 'text-gray-500' : 'text-orange-200'}`}>
                {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
