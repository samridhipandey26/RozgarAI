'use client';

export default function NavBar() {
  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 50,
      backgroundColor: '#111111',
      borderBottom: '1px solid #2A2A2A',
      height: '64px',
      display: 'flex',
      alignItems: 'center',
    }}>
      <div style={{ maxWidth: '1152px', margin: '0 auto', padding: '0 1.5rem', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <a href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '8px',
            backgroundColor: '#F77A02', display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontWeight: 800, fontSize: '18px', color: '#fff',
          }}>R</div>
          <span style={{ fontWeight: 800, fontSize: '1.25rem', color: '#fff', letterSpacing: '-0.02em' }}>
            Rozgar<span style={{ color: '#F77A02' }}>AI</span>
          </span>
        </a>
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <a
            href="/worker/login"
            style={{ color: '#D1D5DB', textDecoration: 'none', fontWeight: 500, fontSize: '0.9rem' }}
            onMouseEnter={e => (e.currentTarget.style.color = '#fff')}
            onMouseLeave={e => (e.currentTarget.style.color = '#D1D5DB')}
          >
            Worker
          </a>
          <a
            href="/employer/login"
            style={{
              backgroundColor: '#F77A02', color: '#fff', textDecoration: 'none',
              fontWeight: 600, fontSize: '0.875rem', padding: '8px 18px', borderRadius: '8px',
            }}
            onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#E06A00')}
            onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#F77A02')}
          >
            Employer
          </a>
        </div>
      </div>
    </nav>
  );
}
