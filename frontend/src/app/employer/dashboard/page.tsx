// frontend/src/app/employer/dashboard/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';

export default function EmployerDashboard() {
  const [profile, setProfile] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [showNewJobModal, setShowNewJobModal] = useState(false);
  const router = useRouter();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const me = await fetchApi('/api/auth/me');
      if (!me || me.role !== 'employer') {
        router.push('/employer/login');
        return;
      }
      setProfile(me);
      // For now, list all jobs (in a real app, pass employer_id to filter)
      const allJobs = await fetchApi('/api/jobs/');
      setJobs(allJobs); // We'd filter by me.user_id if backend supported it on this endpoint
    } catch (e) {
      router.push('/employer/login');
    }
  };

  const handleCreateJob = async (e: any) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const jobData = {
      title: fd.get('title'),
      title_hindi: fd.get('title_hindi'),
      role_tag: fd.get('role_tag'),
      wage_per_day: parseInt(fd.get('wage_per_day') as string),
      city: fd.get('city'),
      address: fd.get('address'),
      openings: parseInt(fd.get('openings') as string),
    };

    try {
      await fetchApi('/api/jobs/', {
        method: 'POST',
        body: JSON.stringify(jobData),
      });
      setShowNewJobModal(false);
      loadDashboard();
    } catch (err) {
      alert("Failed to post job");
    }
  };

  if (!profile) return <div className="p-8 text-center">Loading...</div>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Employer Dashboard</h1>
          <p className="text-gray-400">Manage your job postings and applicants</p>
        </div>
        <button 
          onClick={() => setShowNewJobModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition-colors"
        >
          + Post New Job
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {jobs.map(job => (
          <div key={job.id} className="bg-[#1C1C1E] border border-[#333] rounded-xl p-6 relative overflow-hidden">
            <div className={`absolute top-0 left-0 w-full h-1 ${job.status === 'open' ? 'bg-green-500' : 'bg-gray-500'}`}></div>
            <h3 className="text-xl font-bold text-white mb-1">{job.title}</h3>
            <p className="text-gray-400 text-sm mb-4">{job.city} • ₹{job.wage_per_day}/day</p>
            
            <div className="flex justify-between items-center mb-4">
              <span className={`text-xs px-2 py-1 rounded ${job.status === 'open' ? 'bg-green-900/50 text-green-400' : 'bg-gray-800 text-gray-400'}`}>
                {job.status.toUpperCase()}
              </span>
              <span className="text-sm text-gray-300">Openings: {job.openings}</span>
            </div>
            
            <button className="w-full bg-[#222225] hover:bg-[#333] border border-[#444] text-white py-2 rounded transition-colors text-sm">
              View Applicants (Demo)
            </button>
          </div>
        ))}
      </div>

      {/* New Job Modal */}
      {showNewJobModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-[#1C1C1E] max-w-lg w-full rounded-2xl border border-[#333] overflow-hidden">
            <div className="bg-blue-600 h-2 w-full"></div>
            <form onSubmit={handleCreateJob} className="p-6">
              <h3 className="text-xl font-bold text-white mb-6">Post a New Job</h3>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Title (English)</label>
                    <input name="title" required className="w-full bg-[#0D0D0D] border border-[#333] rounded p-2 text-white" />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Title (Hindi)</label>
                    <input name="title_hindi" required className="w-full bg-[#0D0D0D] border border-[#333] rounded p-2 text-white" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Role Tag (e.g. electrician)</label>
                    <input name="role_tag" required className="w-full bg-[#0D0D0D] border border-[#333] rounded p-2 text-white" />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Wage (₹/day)</label>
                    <input type="number" name="wage_per_day" required className="w-full bg-[#0D0D0D] border border-[#333] rounded p-2 text-white" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">City</label>
                    <select name="city" className="w-full bg-[#0D0D0D] border border-[#333] rounded p-2 text-white">
                      <option>Lucknow</option><option>Kanpur</option><option>Varanasi</option>
                      <option>Agra</option><option>Gorakhpur</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Openings</label>
                    <input type="number" name="openings" defaultValue={1} min={1} required className="w-full bg-[#0D0D0D] border border-[#333] rounded p-2 text-white" />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-1">Full Address (for auto-geocoding)</label>
                  <textarea name="address" required className="w-full bg-[#0D0D0D] border border-[#333] rounded p-2 text-white h-20 resize-none"></textarea>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button type="button" onClick={() => setShowNewJobModal(false)} className="flex-1 bg-[#222225] py-2 rounded text-white border border-[#444]">Cancel</button>
                <button type="submit" className="flex-1 bg-blue-600 hover:bg-blue-700 py-2 rounded text-white font-bold">Post Job</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
