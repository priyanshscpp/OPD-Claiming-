import { useEffect, useState } from 'react';

interface ToastProps {
    type: 'success' | 'error' | 'info';
    message: string;
    onClose: () => void;
    duration?: number;
}

const Toast = ({ type, message, onClose, duration = 5000 }: ToastProps) => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // Trigger slide-in animation
        setTimeout(() => setIsVisible(true), 10);

        // Auto-dismiss
        const timer = setTimeout(() => {
            setIsVisible(false);
            setTimeout(onClose, 300);
        }, duration);

        return () => clearTimeout(timer);
    }, [duration, onClose]);

    const getConfig = () => {
        switch (type) {
            case 'success':
                return {
                    bg: 'linear-gradient(135deg, #10B981, #059669)',
                    icon: '✓',
                };
            case 'error':
                return {
                    bg: 'linear-gradient(135deg, #DC2626, #B91C1C)',
                    icon: '✕',
                };
            case 'info':
                return {
                    bg: 'linear-gradient(135deg, #3B82F6, #2563EB)',
                    icon: 'ℹ',
                };
        }
    };

    const config = getConfig();

    return (
        <div
            style={{
                position: 'fixed',
                bottom: 'var(--spacing-lg)',
                right: isVisible ? 'var(--spacing-lg)' : '-400px',
                background: config.bg,
                color: 'white',
                padding: 'var(--spacing-md) var(--spacing-lg)',
                borderRadius: 'var(--radius-lg)',
                boxShadow: 'var(--shadow-xl)',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-md)',
                minWidth: '300px',
                maxWidth: '400px',
                zIndex: 1000,
                transition: 'right var(--transition-normal)',
            }}
        >
            <div
                style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: 'var(--radius-full)',
                    background: 'rgba(255, 255, 255, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 'var(--font-size-lg)',
                    fontWeight: 'bold',
                }}
            >
                {config.icon}
            </div>
            <p style={{ margin: 0, flex: 1, color: 'white', fontSize: 'var(--font-size-sm)' }}>
                {message}
            </p>
            <button
                onClick={() => {
                    setIsVisible(false);
                    setTimeout(onClose, 300);
                }}
                style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: 'none',
                    color: 'white',
                    width: '24px',
                    height: '24px',
                    borderRadius: 'var(--radius-full)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 'var(--font-size-sm)',
                    transition: 'background var(--transition-fast)',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'}
            >
                ✕
            </button>
        </div>
    );
};

export default Toast;
