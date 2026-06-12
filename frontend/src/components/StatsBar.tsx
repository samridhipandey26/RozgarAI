'use client';

import { useEffect, useState } from 'react';
import { fetchApi } from '@/lib/api';

interface Stats {
  workers_registered: number;
  jobs_filled: number;
  avg_daily_wage: number;
  active_cities: number;
}

const FALLBACK: Stats = {
  workers_registered: 1240,
  jobs_filled: 834,
  avg_daily_wage: 562,
  active_cities: 8,
};

function AnimatedNumber({ value, prefix = '', suffix = '' }: { value: number; prefix?: string; suffix?: string }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (value === 0) return;
    let start = 0;
    const step = Math.ceil(value / 40);
    const timer = setInterval(() => {
      start += step;
      if (start >= value) {
        setDisplay(value);
        clearInterval(timer);
      } else {
        setDisplay(start);
      }
    }, 30);
    return () => clearInterval(timer);
  }, [value]);

  return <span>{prefix}{display.toLocaleString()}{suffix}</span>;
}

export default function StatsBar() {
  const [stats, setStats] = useState<Stats>(FALLBACK);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetchApi('/api/stats/')
      .then((data: Stats) => {
        setStats(data);
        setLoaded(true);
      })
      .catch((err) => {
        console.warn('[StatsBar] Backend not reachable, showing fallback stats.', err.message);
        setLoaded(true);
      });
  }, []);

  const items = [
    { label: 'मज़दूर जुड़े', value: stats.workers_registered, prefix: '', suffix: '+' },
    { label: 'नौकरियां मिलीं', value: stats.jobs_filled, prefix: '', suffix: '+' },
    { label: 'औसत मज़दूरी / दिन', value: stats.avg_daily_wage, prefix: '₹', suffix: '' },
    { label: 'सक्रिय शहर', value: stats.active_cities, prefix: '', suffix: '' },
  ];

  return (
    <div style={{ backgroundColor: '#1C1C1E', borderTop: '1px solid #333', borderBottom: '1px solid #333' }}
      className="py-10">
      <div className="max-w-5xl mx-auto px-4">
        <div className="grid grid-cols-2 gap-6"
          style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
          {items.map((item) => (
            <div
              key={item.label}
              className="text-center"
              style={{
                textAlign: 'center',
                padding: '1.5rem 1rem',
                backgroundColor: '#222225',
                borderRadius: '1rem',
                border: '1px solid #333',
              }}
            >
              <div style={{ fontSize: '2.25rem', fontWeight: 800, color: item.label.includes('मज़दूरी') ? '#F77A02' : '#ffffff', marginBottom: '0.5rem' }}>
                {loaded ? <AnimatedNumber value={item.value} prefix={item.prefix} suffix={item.suffix} /> : '—'}
              </div>
              <div style={{ fontSize: '0.875rem', color: '#9CA3AF' }}>{item.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
