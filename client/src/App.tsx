import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import SubmitClaim from './components/SubmitClaim';
import ClaimsList from './components/ClaimsList';
import ClaimDetails from './components/ClaimDetails';
import Toast from './components/Toast';

function Navigation() {
    const location = useLocation();
    const isActive = (path: string) => location.pathname === path;

    return (
        <nav style={{
            background: 'var(--color-bg-glass)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.3)',
            position: 'sticky',
            top: 0,
            zIndex: 100,
            padding: '0.75rem 0',
            boxShadow: 'var(--shadow-glass)',
        }}>
            <div className="container">
                <div className="flex items-center justify-between">
                    {/* Logo Section */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{
                            width: '48px',
                            height: '48px',
                            borderRadius: '12px',
                            overflow: 'hidden',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: 'white',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                        }}>
                             <img src="/logo.png" alt="Plum Logo" style={{ width: '40px', height: '40px', objectFit: 'contain' }} />
                        </div>
                        <div>
                            <h2 style={{ 
                                margin: 0, 
                                fontSize: '1.5rem', 
                                background: 'linear-gradient(135deg, var(--color-plum-primary), var(--color-accent))',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                letterSpacing: '-0.03em'
                            }}>
                                Plum
                            </h2>
                            <span style={{ 
                                fontSize: '0.75rem', 
                                color: 'var(--color-gray)', 
                                fontWeight: 500, 
                                lineHeight: 1, 
                                display: 'block',
                                letterSpacing: '0.05em',
                                textTransform: 'uppercase'
                            }}>
                                OPD Claims
                            </span>
                        </div>
                    </div>

                    {/* Navigation Links */}
                    <div style={{ 
                        display: 'flex', 
                        gap: '0.5rem', 
                        background: 'rgba(255,255,255,0.5)', 
                        padding: '0.25rem', 
                        borderRadius: 'var(--radius-lg)',
                        border: '1px solid rgba(255,255,255,0.5)'
                    }}>
                        <Link
                            to="/"
                            style={{
                                padding: '0.5rem 1.25rem',
                                borderRadius: 'var(--radius-md)',
                                textDecoration: 'none',
                                fontWeight: 600,
                                fontSize: '0.9rem',
                                transition: 'all 0.2s ease',
                                ...(isActive('/') ? {
                                    background: 'var(--color-white)',
                                    color: 'var(--color-plum-primary)',
                                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                                    transform: 'scale(1.02)'
                                } : {
                                    color: 'var(--color-gray)',
                                    background: 'transparent',
                                }),
                            }}
                        >
                            Submit Claim
                        </Link>
                        <Link
                            to="/claims"
                            style={{
                                padding: '0.5rem 1.25rem',
                                borderRadius: 'var(--radius-md)',
                                textDecoration: 'none',
                                fontWeight: 600,
                                fontSize: '0.9rem',
                                transition: 'all 0.2s ease',
                                ...(isActive('/claims') ? {
                                    background: 'var(--color-white)',
                                    color: 'var(--color-plum-primary)',
                                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                                    transform: 'scale(1.02)'
                                } : {
                                    color: 'var(--color-gray)',
                                    background: 'transparent',
                                }),
                            }}
                        >
                            View Claims
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
}

export interface ToastMessage {
    id: number;
    type: 'success' | 'error' | 'info';
    message: string;
}

function App() {
    const [toasts, setToasts] = useState<ToastMessage[]>([]);

    const showToast = (type: 'success' | 'error' | 'info', message: string) => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, type, message }]);
    };

    const removeToast = (id: number) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    };

    return (
        <Router>
            <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
                <Navigation />

                <main style={{ flex: 1, padding: 'var(--spacing-xl) 0' }}>
                    <div className="animate-fade-in">
                        <Routes>
                            <Route path="/" element={<SubmitClaim showToast={showToast} />} />
                            <Route path="/claims" element={<ClaimsList />} />
                            <Route path="/claims/:claimId" element={<ClaimDetails />} />
                        </Routes>
                    </div>
                </main>

                <footer style={{
                    background: 'var(--color-white)',
                    borderTop: '1px solid var(--color-gray-light)',
                    padding: 'var(--spacing-lg)',
                    textAlign: 'center',
                    color: 'var(--color-gray)',
                    fontSize: 'var(--font-size-sm)',
                    marginTop: 'auto'
                }}>
                    <div className="container">
                        <p style={{ margin: 0 }}>&copy; 2024 Plum Benefits. AI-Powered OPD Adjudication Engine.</p>
                    </div>
                </footer>

                {toasts.map(toast => (
                    <Toast
                        key={toast.id}
                        type={toast.type}
                        message={toast.message}
                        onClose={() => removeToast(toast.id)}
                    />
                ))}
            </div>
        </Router>
    );
}

export default App;
