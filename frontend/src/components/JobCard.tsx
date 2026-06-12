// frontend/src/components/JobCard.tsx
'use client';

import { useEffect } from 'react';
import { STRINGS_HI } from '../lib/strings_hi';

export interface JobMatch {
  id?: string;
  title?: string;
  title_hindi?: string;
  employer?: string;
  employer_name?: string;
  wage_per_day?: number | string;
  location?: string;
  city?: string;
  distance_km?: number | string;
  match_score?: number;
  match_pct?: number;
  openings?: number | string;
  start_date?: string;
  role_tag?: string;
  role?: string;
}

interface JobProps {
  job: JobMatch;
  onApply: (job: JobMatch) => void;
}

export default function JobCard({ job, onApply }: JobProps) {
  useEffect(() => {
    console.log("[JobCard] Received job payload:", job);
  }, [job]);

  if (!job) return null;

  // Safe fallbacks
  const title = job?.title_hindi || job?.title || 'Unknown Role';
  const matchScore = job?.match_score || job?.match_pct;
  const employer = job?.employer || job?.employer_name || 'Contractor';
  const location = job?.location || job?.city || 'Unknown Location';
  const wage = job?.wage_per_day || 'Negotiable';
  const distance = job?.distance_km;
  const openings = job?.openings;
  
  // Tag formatting (fallback to title, replace underscores)
  const roleTagRaw = job?.role_tag || job?.role || job?.title || 'Unknown';
  const roleTag = typeof roleTagRaw === 'string' ? roleTagRaw.replace(/_/g, ' ') : String(roleTagRaw);

  return (
    <div className="bg-[#222225] rounded-xl overflow-hidden border border-[#333] hover:border-[#F77A02]/50 transition-colors flex flex-col h-full relative">
      <div className="w-1.5 h-full bg-[#F77A02] absolute left-0 top-0"></div>
      
      <div className="p-5 flex-1 relative pl-6">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-xl font-bold text-white">{title}</h3>
          {matchScore !== undefined && (
            <span className="bg-[#331E0C] text-[#F77A02] text-xs px-2 py-1 rounded-full font-bold">
              {matchScore}% {STRINGS_HI.dashboard.matchPct || 'Match'}
            </span>
          )}
        </div>
        
        <p className="text-gray-400 text-sm mb-4">{employer} • {location}</p>
        
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-[#1C1C1E] rounded-lg p-2 text-center border border-[#333]">
            <div className="text-sm text-gray-500">{STRINGS_HI.dashboard.wagePerDay || 'Wage/Day'}</div>
            <div className="text-lg font-bold text-[#F77A02]">
              {typeof wage === 'number' ? `₹${wage}` : wage}
            </div>
          </div>
          {distance !== undefined && distance !== null && distance !== '?' && (
            <div className="bg-[#1C1C1E] rounded-lg p-2 text-center border border-[#333]">
              <div className="text-sm text-gray-500">{STRINGS_HI.dashboard.distance || 'Distance'}</div>
              <div className="text-lg font-bold text-white">{distance} km</div>
            </div>
          )}
        </div>
        
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="bg-[#1C1C1E] text-gray-300 text-xs px-2 py-1 rounded border border-[#333] capitalize">
            {roleTag}
          </span>
          {openings !== undefined && openings !== null && (
            <span className="bg-[#1C1C1E] text-gray-300 text-xs px-2 py-1 rounded border border-[#333]">
              {openings} Openings
            </span>
          )}
        </div>
      </div>
      
      <div className="p-4 pt-0 pl-6 mt-auto">
        <button 
          onClick={() => onApply(job)}
          className="w-full bg-[#F77A02] hover:bg-[#E06A00] text-white font-bold py-3 rounded-lg transition-colors"
        >
          {STRINGS_HI.dashboard.applyButton || 'Apply Now'}
        </button>
      </div>
    </div>
  );
}
