// frontend/src/components/JobCard.tsx
'use client';

import { STRINGS_HI } from '../lib/strings_hi';

interface JobProps {
  job: any;
  onApply: (job: any) => void;
}

export default function JobCard({ job, onApply }: JobProps) {
  return (
    <div className="bg-[#222225] rounded-xl overflow-hidden border border-[#333] hover:border-[#F77A02]/50 transition-colors flex flex-col h-full">
      <div className="w-1.5 h-full bg-[#F77A02] absolute left-0 top-0"></div>
      
      <div className="p-5 flex-1 relative pl-6">
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#F77A02]"></div>
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-xl font-bold text-white">{job.title_hindi || job.title}</h3>
          {job.match_pct && (
            <span className="bg-[#331E0C] text-[#F77A02] text-xs px-2 py-1 rounded-full font-bold">
              {job.match_pct}% {STRINGS_HI.dashboard.matchPct}
            </span>
          )}
        </div>
        
        <p className="text-gray-400 text-sm mb-4">{job.employer_name || 'Contractor'} • {job.city}</p>
        
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-[#1C1C1E] rounded-lg p-2 text-center border border-[#333]">
            <div className="text-sm text-gray-500">{STRINGS_HI.dashboard.wagePerDay}</div>
            <div className="text-lg font-bold text-[#F77A02]">₹{job.wage_per_day}</div>
          </div>
          {job.distance_km !== undefined && (
            <div className="bg-[#1C1C1E] rounded-lg p-2 text-center border border-[#333]">
              <div className="text-sm text-gray-500">{STRINGS_HI.dashboard.distance}</div>
              <div className="text-lg font-bold text-white">{job.distance_km}</div>
            </div>
          )}
        </div>
        
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="bg-[#1C1C1E] text-gray-300 text-xs px-2 py-1 rounded border border-[#333]">
            {job.role_tag.replace('_', ' ')}
          </span>
          {job.openings && (
            <span className="bg-[#1C1C1E] text-gray-300 text-xs px-2 py-1 rounded border border-[#333]">
              {job.openings} Openings
            </span>
          )}
        </div>
      </div>
      
      <div className="p-4 pt-0 pl-6">
        <button 
          onClick={() => onApply(job)}
          className="w-full bg-[#F77A02] hover:bg-[#E06A00] text-white font-bold py-3 rounded-lg transition-colors"
        >
          {STRINGS_HI.dashboard.applyButton}
        </button>
      </div>
    </div>
  );
}
