// frontend/src/app/worker/dashboard/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { STRINGS_HI } from '@/lib/strings_hi';
import { fetchApi } from '@/lib/api';
import JobCard from '@/components/JobCard';

export default function WorkerDashboard() {
  const [profile, setProfile] = useState<any>(null);
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState<any[]>([]);
  const [latestResume, setLatestResume] = useState<any>(null);
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [showModal, setShowModal] = useState(false);
  const [applying, setApplying] = useState(false);
  const router = useRouter();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load profile
      const me = await fetchApi('/api/auth/me');
      if (!me) {
        router.push('/worker/login');
        return;
      }
      setProfile(me);

      // Load matching jobs
      const jobsRes = await fetchApi('/api/jobs/match');
      setJobs(jobsRes);

      // Load applications
      const apps = await fetchApi('/api/applications/worker');
      setApplications(apps);

      // Load latest resume
      try {
        const resumes = await fetchApi('/api/resumes/list');
        if (resumes.latest) setLatestResume(resumes.latest);
      } catch (e) {
        console.error("No resume found");
      }

    } catch (err) {
      console.error(err);
      router.push('/worker/login');
    }
  };

  const handleApplyClick = (job: any) => {
    setSelectedJob(job);
    setShowModal(true);
  };

  const confirmApply = async () => {
    if (!selectedJob) return;
    setApplying(true);
    try {
      await fetchApi('/api/applications/', {
        method: 'POST',
        body: JSON.stringify({ job_id: selectedJob.id, confirmed: true }),
      });
      setShowModal(false);
      loadDashboardData(); // Reload to update status
    } catch (err) {
      console.error("Failed to apply:", err);
      alert("Application failed. Please try again.");
    } finally {
      setApplying(false);
      setSelectedJob(null);
    }
  };

  const handleDownloadResume = async () => {
    if (latestResume) {
      // If we have a URL, just open it
      if (latestResume.pdf_url) {
        window.open(latestResume.pdf_url, '_blank');
      } else {
        // Direct download from backend
        const { data } = await (await import('@/lib/supabase')).supabase.auth.getSession();
        const token = data?.session?.access_token || '';
        window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/resumes/download/${latestResume.id}?token=${token}`, '_blank');
      }
    }
  };

  if (!profile) return <div className="p-8 text-center text-white">Loading dashboard...</div>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Profile Header */}
      <div className="bg-[#1C1C1E] border border-[#333] rounded-2xl p-6 mb-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">
            {STRINGS_HI.dashboard.greeting}, {profile.name || 'Worker'}!
          </h1>
          <p className="text-gray-400">आपकी प्रोफाइल तैयार है और नौकरियां नीचे हैं।</p>
        </div>
        <button 
          onClick={handleDownloadResume}
          disabled={!latestResume}
          className="bg-[#331E0C] hover:bg-[#4A2B11] text-[#F77A02] border border-[#F77A02] font-bold py-2 px-6 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <span>📄</span> {STRINGS_HI.dashboard.resumeDownload}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Jobs Section */}
        <div className="lg:col-span-2">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span className="w-2 h-6 bg-[#F77A02] rounded-sm"></span>
            {STRINGS_HI.dashboard.jobMatchTitle}
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((job: any) => {
              const applied = applications.some(a => a.job_id === job.id);
              return (
                <div key={job.id}>
                  {applied ? (
                    <div className="bg-[#1C1C1E] rounded-xl overflow-hidden border border-[#333] opacity-60 relative h-full flex flex-col justify-center items-center p-6 text-center">
                      <div className="text-2xl mb-2">✅</div>
                      <div className="font-bold text-[#F77A02]">{STRINGS_HI.dashboard.applied}</div>
                      <div className="text-sm mt-2 text-white">{job.title_hindi || job.title}</div>
                      <div className="text-xs text-gray-500 mt-1">{applications.find(a=>a.job_id===job.id)?.status}</div>
                    </div>
                  ) : (
                    <JobCard job={job} onApply={handleApplyClick} />
                  )}
                </div>
              );
            })}
            
            {jobs.length === 0 && (
              <div className="col-span-2 bg-[#1C1C1E] rounded-xl p-8 text-center border border-[#333] text-gray-400">
                अभी कोई मैचिंग नौकरी नहीं मिली।
              </div>
            )}
          </div>
        </div>

        {/* Status Tracker Side Panel */}
        <div className="lg:col-span-1">
          <h2 className="text-xl font-bold mb-4">Application Status</h2>
          <div className="bg-[#1C1C1E] rounded-xl border border-[#333] p-4 space-y-4">
            {applications.length === 0 ? (
              <div className="text-sm text-gray-500 text-center py-4">No applications yet</div>
            ) : (
              applications.map((app: any) => {
                const job = jobs.find((j:any) => j.id === app.job_id) || { title_hindi: 'Job' };
                return (
                  <div key={app.id} className="border-b border-[#333] pb-4 last:border-0 last:pb-0">
                    <div className="font-bold text-white mb-1">{job.title_hindi}</div>
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${app.status === 'confirmed' ? 'bg-green-500' : 'bg-[#F77A02]'}`}></div>
                      <span className="text-sm capitalize text-gray-300">{app.status}</span>
                    </div>
                    {app.otp && (
                      <div className="mt-2 bg-[#0D0D0D] border border-[#333] p-2 rounded text-xs text-center">
                        <span className="text-gray-500">OTP: </span>
                        <span className="font-mono text-[#F77A02] font-bold text-lg tracking-widest">{app.otp}</span>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>

      </div>

      {/* Confirmation Modal */}
      {showModal && selectedJob && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-[#1C1C1E] max-w-md w-full rounded-2xl border border-[#333] overflow-hidden shadow-2xl transform transition-all">
            <div className="bg-[#F77A02] h-2 w-full"></div>
            <div className="p-6">
              <h3 className="text-xl font-bold text-white mb-4 text-center">
                {STRINGS_HI.application.confirmModalTitle}
              </h3>
              
              <div className="bg-[#0D0D0D] p-4 rounded-lg mb-6 border border-[#333]">
                <div className="font-bold text-lg text-[#F77A02] mb-1">{selectedJob.title_hindi || selectedJob.title}</div>
                <div className="text-gray-300">{selectedJob.employer_name} • {selectedJob.city}</div>
                <div className="text-white font-bold mt-2">₹{selectedJob.wage_per_day}/din</div>
              </div>
              
              <div className="flex gap-3">
                <button 
                  onClick={() => setShowModal(false)}
                  disabled={applying}
                  className="flex-1 bg-[#222225] hover:bg-[#333] text-white font-bold py-3 rounded-lg border border-[#444] transition-colors"
                >
                  {STRINGS_HI.application.noButton}
                </button>
                <button 
                  onClick={confirmApply}
                  disabled={applying}
                  className="flex-1 bg-[#F77A02] hover:bg-[#E06A00] text-white font-bold py-3 rounded-lg transition-colors flex justify-center items-center"
                >
                  {applying ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    STRINGS_HI.application.yesButton
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
