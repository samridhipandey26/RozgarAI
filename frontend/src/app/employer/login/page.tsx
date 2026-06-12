'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchApi, saveSession } from '@/lib/api';

const S = {
  wrap: { minHeight: 'calc(100vh - 64px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem', background: 'radial-gradient(ellipse at top, #0a1a2e 0%, #0D0D0D 60%)' } as React.CSSProperties,
  card: { width: '100%', maxWidth: '420px', backgroundColor: '#1C1C1E', border: '1px solid #2A2A2A', borderRadius: '1.25rem', overflow: 'hidden', boxShadow: '0 25px 60px rgba(0,0,0,0.5)' } as React.CSSProperties,
  topBar: { height: '4px', backgroundColor: '#3B82F6', width: '100%' } as React.CSSProperties,
  body: { padding: '2.25rem 2rem' } as React.CSSProperties,
  label: { display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#9CA3AF', marginBottom: '6px', letterSpacing: '0.03em', textTransform: 'uppercase' } as React.CSSProperties,
  input: { width: '100%', backgroundColor: '#111', color: '#fff', border: '1px solid #333', borderRadius: '10px', padding: '12px 14px', fontSize: '1rem', outline: 'none', transition: 'border-color 0.2s, box-shadow 0.2s', marginBottom: '1.25rem', display: 'block', boxSizing: 'border-box' } as React.CSSProperties,
  error: { backgroundColor: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.4)', borderRadius: '8px', padding: '10px 14px', color: '#FCA5A5', fontSize: '0.875rem', marginBottom: '1.25rem' } as React.CSSProperties,
  btn: { width: '100%', backgroundColor: '#3B82F6', color: '#fff', fontWeight: 700, fontSize: '1rem', padding: '13px', borderRadius: '10px', border: 'none', cursor: 'pointer', transition: 'background-color 0.2s', marginTop: '0.5rem' } as React.CSSProperties,
};

export default function EmployerLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignup, setIsSignup] = useState(false);
  const [name, setName] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const iFocus = (e: React.FocusEvent<HTMLInputElement>) => { e.target.style.borderColor = '#3B82F6'; e.target.style.boxShadow = '0 0 0 2px rgba(59,130,246,0.2)'; };
  const iBlur = (e: React.FocusEvent<HTMLInputElement>) => { e.target.style.borderColor = '#333'; e.target.style.boxShadow = 'none'; };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) { setError('Email/phone and password are required.'); return; }
    if (isSignup && password !== confirm) { setError('Passwords do not match.'); return; }
    if (isSignup && password.length < 6) { setError('Password must be at least 6 characters.'); return; }

    setLoading(true); setError('');
    try {
      const endpoint = isSignup ? '/api/auth/signup' : '/api/auth/login';
      const body: any = { email: email.trim(), password, role: 'employer' };
      if (isSignup) body.name = name.trim();

      const res = await fetchApi(endpoint, { method: 'POST', body: JSON.stringify(body) });
      saveSession({ access_token: res.access_token, user_id: res.user_id, role: 'employer', name: res.name || name });
      router.push('/employer/dashboard');
    } catch (err: any) {
      setError(err.message || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={S.wrap}>
      <div style={S.card}>
        <div style={S.topBar} />
        <div style={S.body}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🏢</div>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff', marginBottom: '0.25rem' }}>Employer Portal</h1>
            <p style={{ color: '#6B7280', fontSize: '0.9rem' }}>Post jobs and find skilled workers</p>
          </div>

          {/* Toggle login/signup */}
          <div style={{ display: 'flex', backgroundColor: '#111', borderRadius: '10px', border: '1px solid #333', padding: '4px', marginBottom: '1.5rem' }}>
            {[['Login', false], ['Sign Up', true]].map(([label, val]) => (
              <button key={String(val)} type="button" onClick={() => { setIsSignup(val as boolean); setError(''); }}
                style={{ flex: 1, padding: '9px', borderRadius: '7px', border: 'none', backgroundColor: isSignup === val ? '#3B82F6' : 'transparent', color: isSignup === val ? '#fff' : '#6B7280', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', transition: 'all 0.2s' }}>
                {label as string}
              </button>
            ))}
          </div>

          {error && <div style={S.error}>{error}</div>}

          <form onSubmit={handleSubmit}>
            {isSignup && (
              <>
                <label style={S.label}>Company / Your Name</label>
                <input style={S.input} type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Sharma Construction Pvt Ltd" required={isSignup} onFocus={iFocus} onBlur={iBlur} />
              </>
            )}
            <label style={S.label}>Email or Phone</label>
            <input style={S.input} type="text" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@company.com" required onFocus={iFocus} onBlur={iBlur} />
            <label style={S.label}>Password</label>
            <input style={S.input} type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Min. 6 characters" required onFocus={iFocus} onBlur={iBlur} />
            {isSignup && (
              <>
                <label style={S.label}>Confirm Password</label>
                <input style={S.input} type="password" value={confirm} onChange={e => setConfirm(e.target.value)} placeholder="Repeat password" required={isSignup} onFocus={iFocus} onBlur={iBlur} />
              </>
            )}
            <button type="submit" disabled={loading}
              style={{ ...S.btn, opacity: loading ? 0.6 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}
              onMouseEnter={e => !loading && (e.currentTarget.style.backgroundColor = '#2563EB')}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#3B82F6')}>
              {loading ? 'Please wait…' : isSignup ? 'Create Employer Account →' : 'Log In →'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.8rem', color: '#555' }}>
            <a href="/worker/login" style={{ color: '#6B7280', textDecoration: 'none' }}>← Back to Worker login</a>
          </p>
        </div>
      </div>
    </div>
  );
}
