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
    width: '100%', maxWidth: '440px',
    backgroundColor: '#1C1C1E', border: '1px solid #2A2A2A',
    borderRadius: '1.25rem', overflow: 'hidden',
    boxShadow: '0 25px 60px rgba(0,0,0,0.5)',
  } as React.CSSProperties,
  topBar: { height: '4px', backgroundColor: '#F77A02', width: '100%' } as React.CSSProperties,
  body: { padding: '2.25rem 2rem' } as React.CSSProperties,
  title: { fontSize: '1.75rem', fontWeight: 800, color: '#fff', marginBottom: '0.35rem', textAlign: 'center' } as React.CSSProperties,
  subtitle: { fontSize: '0.9rem', color: '#6B7280', textAlign: 'center', marginBottom: '2rem' } as React.CSSProperties,
  label: { display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#9CA3AF', marginBottom: '6px', letterSpacing: '0.03em', textTransform: 'uppercase' } as React.CSSProperties,
  input: {
    width: '100%', backgroundColor: '#111', color: '#fff', border: '1px solid #333',
    borderRadius: '10px', padding: '12px 14px', fontSize: '1rem', outline: 'none',
    transition: 'border-color 0.2s', marginBottom: '1.25rem', display: 'block', boxSizing: 'border-box',
  } as React.CSSProperties,
  error: { backgroundColor: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.4)', borderRadius: '8px', padding: '10px 14px', color: '#FCA5A5', fontSize: '0.875rem', marginBottom: '1.25rem' } as React.CSSProperties,
  btn: {
    width: '100%', backgroundColor: '#F77A02', color: '#fff', fontWeight: 700,
    fontSize: '1rem', padding: '13px', borderRadius: '10px', border: 'none',
    cursor: 'pointer', transition: 'background-color 0.2s', marginTop: '0.5rem',
  } as React.CSSProperties,
  segmented: { display: 'flex', backgroundColor: '#111', borderRadius: '10px', border: '1px solid #333', padding: '4px', marginBottom: '1.5rem' } as React.CSSProperties,
};

export default function WorkerSignup() {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '', role: 'worker' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm(prev => ({ ...prev, [k]: e.target.value }));

  const validate = () => {
    if (!form.name.trim()) return 'Name is required';
    if (!form.email.trim()) return 'Email or phone is required';
    if (form.password.length < 6) return 'Password must be at least 6 characters';
    if (form.password !== form.confirm) return 'Passwords do not match';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const err = validate();
    if (err) { setError(err); return; }

    setLoading(true);
    setError('');

    try {
      const res = await fetchApi('/api/auth/signup', {
        method: 'POST',
        body: JSON.stringify({
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password,
          role: form.role,
        }),
      });

      saveSession({ access_token: res.access_token, user_id: res.user_id, role: res.role, name: form.name.trim() });
      router.push(form.role === 'employer' ? '/employer/dashboard' : '/worker/onboarding');
    } catch (err: any) {
      setError(err.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const inputFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.style.borderColor = '#F77A02';
    e.target.style.boxShadow = '0 0 0 2px rgba(247,122,2,0.2)';
  };
  const inputBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.style.borderColor = '#333';
    e.target.style.boxShadow = 'none';
  };

  return (
    <div style={S.wrap}>
      <div style={S.card}>
        <div style={S.topBar} />
        <div style={S.body}>
          <h1 style={S.title}>Create Account</h1>
          <p style={S.subtitle}>Join RozgarAI — नौकरी खोजें या दें।</p>

          {/* Role selector */}
          <div style={S.segmented}>
            {(['worker', 'employer'] as const).map(r => (
              <button
                key={r}
                type="button"
                onClick={() => setForm(prev => ({ ...prev, role: r }))}
                style={{
                  flex: 1, padding: '9px', borderRadius: '7px', border: 'none',
                  backgroundColor: form.role === r ? '#F77A02' : 'transparent',
                  color: form.role === r ? '#fff' : '#6B7280',
                  fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', transition: 'all 0.2s',
                }}>
                {r === 'worker' ? '👷 Worker' : '🏢 Employer'}
              </button>
            ))}
          </div>

          {error && <div style={S.error}>{error}</div>}

          <form onSubmit={handleSubmit}>
            <label style={S.label}>Full Name</label>
            <input style={S.input} type="text" value={form.name} onChange={set('name')}
              placeholder="Ramesh Kumar" required onFocus={inputFocus} onBlur={inputBlur} />

            <label style={S.label}>Email or Phone</label>
            <input style={S.input} type="text" value={form.email} onChange={set('email')}
              placeholder="you@email.com  or  +91XXXXXXXXXX" required onFocus={inputFocus} onBlur={inputBlur} />

            <label style={S.label}>Password</label>
            <input style={S.input} type="password" value={form.password} onChange={set('password')}
              placeholder="Min. 6 characters" required onFocus={inputFocus} onBlur={inputBlur} />

            <label style={S.label}>Confirm Password</label>
            <input style={S.input} type="password" value={form.confirm} onChange={set('confirm')}
              placeholder="Repeat password" required onFocus={inputFocus} onBlur={inputBlur} />

            <button type="submit" disabled={loading} style={{ ...S.btn, opacity: loading ? 0.6 : 1 }}
              onMouseEnter={e => !loading && (e.currentTarget.style.backgroundColor = '#E06A00')}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#F77A02')}>
              {loading ? 'Creating account…' : 'Create Account →'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: '#6B7280' }}>
            Already have an account?{' '}
            <a href="/worker/login" style={{ color: '#F77A02', textDecoration: 'none', fontWeight: 600 }}>Log in</a>
          </p>
        </div>
      </div>
    </div>
  );
}
