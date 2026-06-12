'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchApi, saveSession } from '@/lib/api';

const S = {
  wrap: {
    minHeight: 'calc(100vh - 64px)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    padding: '2rem 1rem',
    background: 'radial-gradient(ellipse at top, #1a0e00 0%, #0D0D0D 60%)',
  } as React.CSSProperties,
  card: {
    width: '100%', maxWidth: '420px',
    backgroundColor: '#1C1C1E', border: '1px solid #2A2A2A',
    borderRadius: '1.25rem', overflow: 'hidden',
    boxShadow: '0 25px 60px rgba(0,0,0,0.5)',
  } as React.CSSProperties,
  topBar: { height: '4px', backgroundColor: '#F77A02', width: '100%' } as React.CSSProperties,
  body: { padding: '2.25rem 2rem' } as React.CSSProperties,
  label: { display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#9CA3AF', marginBottom: '6px', letterSpacing: '0.03em', textTransform: 'uppercase' } as React.CSSProperties,
  input: {
    width: '100%', backgroundColor: '#111', color: '#fff', border: '1px solid #333',
    borderRadius: '10px', padding: '12px 14px', fontSize: '1rem', outline: 'none',
    transition: 'border-color 0.2s, box-shadow 0.2s', marginBottom: '1.25rem',
    display: 'block', boxSizing: 'border-box',
  } as React.CSSProperties,
  error: { backgroundColor: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.4)', borderRadius: '8px', padding: '10px 14px', color: '#FCA5A5', fontSize: '0.875rem', marginBottom: '1.25rem' } as React.CSSProperties,
  btn: {
    width: '100%', backgroundColor: '#F77A02', color: '#fff', fontWeight: 700,
    fontSize: '1rem', padding: '13px', borderRadius: '10px', border: 'none',
    cursor: 'pointer', transition: 'background-color 0.2s', marginTop: '0.5rem',
  } as React.CSSProperties,
};

export default function WorkerLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) { setError('Please enter your email/phone and password.'); return; }

    setLoading(true);
    setError('');

    try {
      const res = await fetchApi('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: email.trim(), password }),
      });

      saveSession({ access_token: res.access_token, user_id: res.user_id, role: res.role, name: res.name });

      if (res.role === 'employer') {
        router.push('/employer/dashboard');
      } else if (res.onboarding_done) {
        router.push('/worker/dashboard');
      } else {
        router.push('/worker/onboarding');
      }
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const iFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.style.borderColor = '#F77A02';
    e.target.style.boxShadow = '0 0 0 2px rgba(247,122,2,0.2)';
  };
  const iBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.style.borderColor = '#333';
    e.target.style.boxShadow = 'none';
  };

  return (
    <div style={S.wrap}>
      <div style={S.card}>
        <div style={S.topBar} />
        <div style={S.body}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{ width: '52px', height: '52px', backgroundColor: '#F77A02', borderRadius: '14px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', fontWeight: 800, marginBottom: '1rem' }}>R</div>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff', marginBottom: '0.25rem' }}>Welcome back</h1>
            <p style={{ color: '#6B7280', fontSize: '0.9rem' }}>Log in to your RozgarAI account</p>
          </div>

          {error && <div style={S.error}>{error}</div>}

          <form onSubmit={handleSubmit}>
            <label style={S.label}>Email or Phone Number</label>
            <input
              style={S.input}
              type="text"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@email.com  or  +91XXXXXXXXXX"
              autoComplete="username"
              required
              onFocus={iFocus} onBlur={iBlur}
            />

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <label style={{ ...S.label, marginBottom: 0 }}>Password</label>
            </div>
            <input
              style={S.input}
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Your password"
              autoComplete="current-password"
              required
              onFocus={iFocus} onBlur={iBlur}
            />

            <button
              type="submit"
              disabled={loading}
              style={{ ...S.btn, opacity: loading ? 0.6 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}
              onMouseEnter={e => !loading && (e.currentTarget.style.backgroundColor = '#E06A00')}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#F77A02')}
            >
              {loading ? 'Logging in…' : 'Log In →'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.875rem', color: '#6B7280' }}>
            New to RozgarAI?{' '}
            <a href="/worker/signup" style={{ color: '#F77A02', textDecoration: 'none', fontWeight: 600 }}>
              Create account
            </a>
          </p>

          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            <a href="/employer/login" style={{ color: '#555', textDecoration: 'none', fontSize: '0.8rem' }}>
              Are you an employer? →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
