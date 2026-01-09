import { ClaimStatus } from '../types';

interface StatusBadgeProps {
    status: ClaimStatus;
    size?: 'sm' | 'md' | 'lg';
}

const StatusBadge = ({ status, size = 'md' }: StatusBadgeProps) => {
    const getStatusConfig = () => {
        switch (status) {
            case ClaimStatus.APPROVED:
                return {
                    bg: 'linear-gradient(135deg, #10B981, #059669)',
                    color: '#FFFFFF',
                    label: 'Approved',
                    glow: 'rgba(16, 185, 129, 0.3)',
                };
            case ClaimStatus.REJECTED:
                return {
                    bg: 'linear-gradient(135deg, #DC2626, #B91C1C)',
                    color: '#FFFFFF',
                    label: 'Rejected',
                    glow: 'rgba(220, 38, 38, 0.3)',
                };
            case ClaimStatus.PARTIAL:
                return {
                    bg: 'linear-gradient(135deg, #F59E0B, #D97706)',
                    color: '#FFFFFF',
                    label: 'Partial',
                    glow: 'rgba(245, 158, 11, 0.3)',
                };
            case ClaimStatus.MANUAL_REVIEW:
                return {
                    bg: 'linear-gradient(135deg, #3B82F6, #2563EB)',
                    color: '#FFFFFF',
                    label: 'Manual Review',
                    glow: 'rgba(59, 130, 246, 0.3)',
                };
            case ClaimStatus.PROCESSING:
                return {
                    bg: 'linear-gradient(135deg, #8B5CF6, #7C3AED)',
                    color: '#FFFFFF',
                    label: 'Processing',
                    glow: 'rgba(139, 92, 246, 0.3)',
                };
            default:
                return {
                    bg: 'linear-gradient(135deg, #6B7280, #4B5563)',
                    color: '#FFFFFF',
                    label: 'Pending',
                    glow: 'rgba(107, 114, 128, 0.3)',
                };
        }
    };

    const config = getStatusConfig();

    const sizeStyles = {
        sm: {
            padding: '0.25rem 0.5rem',
            fontSize: '0.75rem',
        },
        md: {
            padding: '0.375rem 0.75rem',
            fontSize: '0.875rem',
        },
        lg: {
            padding: '0.5rem 1rem',
            fontSize: '1rem',
        },
    };

    return (
        <span
            style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.375rem',
                background: config.bg,
                color: config.color,
                borderRadius: 'var(--radius-full)',
                fontWeight: 600,
                boxShadow: `0 4px 12px ${config.glow}, inset 0 -2px 6px rgba(255, 255, 255, 0.3)`,
                position: 'relative',
                overflow: 'hidden',
                ...sizeStyles[size],
            }}
        >
            <span
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '50%',
                    background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.2) 0%, transparent 100%)',
                }}
            />
            <span style={{ position: 'relative', zIndex: 1 }}>
                {config.label}
            </span>
        </span>
    );
};

export default StatusBadge;
