'use client';

import StatsBar from '@/components/StatsBar';

export default function Home() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 'calc(100vh - 64px)' }}>

      {/* ── Hero ────────────────────────────────────────────────────── */}
      <section style={{
        flex: 1,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        textAlign: 'center',
        padding: '5rem 1.5rem',
        background: 'radial-gradient(ellipse at top, #2A1200 0%, #0D0D0D 55%)',
        position: 'relative', overflow: 'hidden',
      }}>
        {/* Decorative glow */}
        <div style={{
          position: 'absolute', top: '-80px', left: '50%', transform: 'translateX(-50%)',
          width: '600px', height: '300px', borderRadius: '50%',
          background: 'radial-gradient(ellipse, rgba(247,122,2,0.15) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        {/* Badge */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '8px',
          backgroundColor: 'rgba(247,122,2,0.1)', border: '1px solid rgba(247,122,2,0.3)',
          borderRadius: '100px', padding: '6px 16px', marginBottom: '2rem',
          fontSize: '0.8rem', fontWeight: 600, color: '#F77A02', letterSpacing: '0.05em',
        }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#F77A02', display: 'inline-block' }}></span>
          INDIA'S FIRST VOICE-FIRST JOB PLATFORM
        </div>

        {/* Main heading */}
        <h1 style={{ fontSize: 'clamp(2.5rem, 7vw, 5rem)', fontWeight: 900, lineHeight: 1.05, marginBottom: '1.5rem', letterSpacing: '-0.03em', maxWidth: '900px' }}>
          <span style={{ color: '#ffffff' }}>काम खोजो।</span>{' '}
          <span style={{ color: '#ffffff' }}>काम दो।</span>{' '}
          <span style={{ color: '#F77A02' }}>आज।</span>
        </h1>
        <p style={{ fontSize: 'clamp(1rem, 2.5vw, 1.25rem)', color: '#9CA3AF', marginBottom: '3rem', maxWidth: '580px', lineHeight: 1.7 }}>
          RozgarAI — 30 second voice note से professional resume, real job matches,
          और interview tips तक। Hindi में। आपके शहर में।
        </p>

        {/* CTA Buttons */}
        <div style={{ display: 'flex', flexDirection: 'row', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          <a href="/worker/signup"
            style={{
              backgroundColor: '#F77A02', color: '#fff', fontWeight: 700,
              fontSize: '1.1rem', padding: '14px 36px', borderRadius: '100px',
              textDecoration: 'none', display: 'inline-block',
              boxShadow: '0 0 30px rgba(247,122,2,0.35)',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.backgroundColor = '#E06A00'; e.currentTarget.style.transform = 'scale(1.03)'; }}
            onMouseLeave={e => { e.currentTarget.style.backgroundColor = '#F77A02'; e.currentTarget.style.transform = 'scale(1)'; }}>
            मज़दूर Login / Signup
          </a>
          <a href="/employer/login"
            style={{
              backgroundColor: '#222225', color: '#fff', fontWeight: 600,
              fontSize: '1.1rem', padding: '14px 36px', borderRadius: '100px',
              textDecoration: 'none', border: '1px solid #444', display: 'inline-block',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = '#888'; e.currentTarget.style.backgroundColor = '#2A2A2E'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = '#444'; e.currentTarget.style.backgroundColor = '#222225'; }}>
            Employer Portal →
          </a>
        </div>

        {/* Feature pills */}
        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '3rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          {['🎤 Hindi Voice Onboarding', '📄 AI Resume Builder', '🔍 Smart Job Matching', '💬 Interview Coach'].map(f => (
            <span key={f} style={{
              backgroundColor: '#1C1C1E', border: '1px solid #333', borderRadius: '100px',
              padding: '6px 14px', fontSize: '0.8rem', color: '#9CA3AF',
            }}>{f}</span>
          ))}
        </div>
      </section>

      {/* ── Stats ────────────────────────────────────────────────────── */}
      <StatsBar />

      {/* ── How it works ─────────────────────────────────────────────── */}
      <section style={{ padding: '5rem 1.5rem', backgroundColor: '#0D0D0D' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <h2 style={{ textAlign: 'center', fontSize: '2rem', fontWeight: 800, marginBottom: '0.75rem', color: '#fff' }}>
            3 Steps. 3 Minutes. Job Ready.
          </h2>
          <p style={{ textAlign: 'center', color: '#6B7280', marginBottom: '3.5rem', fontSize: '1rem' }}>
            बोलिए, देखिए, अप्लाई करिए।
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
            {[
              { step: '01', icon: '🎙️', title: 'बोलिए', subtitle: 'Speak in Hindi', desc: 'Record a 30-second voice note about your work. Our AI understands Hindi, UP dialects, and colloquial speech.' },
              { step: '02', icon: '🤖', title: 'AI काम करता है', subtitle: 'AI Does the Work', desc: '7 AI agents extract your skills, build a professional resume, and find the top matching jobs near you.' },
              { step: '03', icon: '✅', title: 'अप्लाई करिए', subtitle: 'Apply & Get Hired', desc: 'Review your matches, get interview tips, then confirm with one tap. Employer gets notified instantly.' },
            ].map(item => (
              <div key={item.step} style={{
                backgroundColor: '#1C1C1E', border: '1px solid #2A2A2A', borderRadius: '1rem',
                padding: '2rem', position: 'relative', overflow: 'hidden',
              }}>
                <div style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', fontSize: '2rem', fontWeight: 900, color: '#222', letterSpacing: '-0.05em' }}>
                  {item.step}
                </div>
                <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{item.icon}</div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff', marginBottom: '0.25rem' }}>{item.title}</h3>
                <p style={{ fontSize: '0.8rem', color: '#F77A02', fontWeight: 600, marginBottom: '0.75rem', letterSpacing: '0.05em', textTransform: 'uppercase' }}>{item.subtitle}</p>
                <p style={{ color: '#9CA3AF', lineHeight: 1.65, fontSize: '0.9rem' }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <footer style={{ borderTop: '1px solid #222', padding: '2.5rem 1.5rem', textAlign: 'center' }}>
        <p style={{ color: '#F77A02', fontWeight: 600, marginBottom: '0.5rem' }}>
          हर हाथ को काम, हर काम को सम्मान।
        </p>
        <p style={{ color: '#4B5563', fontSize: '0.875rem' }}>© 2026 RozgarAI Platform. Built for Bharat.</p>
      </footer>

    </div>
  );
}
