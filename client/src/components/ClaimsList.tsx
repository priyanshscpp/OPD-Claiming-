import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { listClaims } from '../services/api';
import type { Claim, ClaimStatus } from '../types';
import StatusBadge from './StatusBadge';

const ClaimsList = () => {
    const [claims, setClaims] = useState<Claim[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<ClaimStatus | 'ALL'>('ALL');

    useEffect(() => {
        loadClaims();
    }, []);

    const loadClaims = async () => {
        try {
            setLoading(true);
            const data = await listClaims();
            setClaims(data);
        } catch (error) {
            console.error('Error loading claims:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredClaims = filter === 'ALL'
        ? claims
        : claims.filter(claim => claim.status === filter);

    const getStats = () => {
        const total = claims.length;
        const approved = claims.filter(c => c.status === 'APPROVED').length;
        const rejected = claims.filter(c => c.status === 'REJECTED').length;
        const pending = claims.filter(c => c.status === 'PROCESSING' || c.status === 'PENDING').length;
        const totalApproved = claims
            .filter(c => c.status === 'APPROVED')
            .reduce((sum, c) => sum + (c.approved_amount || 0), 0);

        return { total, approved, rejected, pending, totalApproved };
    };

    const stats = getStats();

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    };

    const formatAmount = (amount: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
        }).format(amount);
    };

    return (
        <div className="container">
            <div className="animate-fade-in">
                <h2 style={{ marginBottom: 'var(--spacing-xl)' }}>Claims Dashboard</h2>

                {/* Stats Cards */}
                <div className="grid grid-cols-4" style={{ marginBottom: 'var(--spacing-2xl)' }}>
                    <div className="card" style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 'var(--font-size-3xl)', marginBottom: 'var(--spacing-sm)' }}>
                            📊
                        </div>
                        <p style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', margin: 0, color: 'var(--color-black)' }}>
                            {stats.total}
                        </p>
                        <p style={{ color: 'var(--color-gray)', fontSize: 'var(--font-size-sm)', margin: 0 }}>
                            Total Claims
                        </p>
                    </div>

                    <div className="card" style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 'var(--font-size-3xl)', marginBottom: 'var(--spacing-sm)' }}>
                            ✅
                        </div>
                        <p style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', margin: 0, color: 'var(--color-success)' }}>
                            {stats.approved}
                        </p>
                        <p style={{ color: 'var(--color-gray)', fontSize: 'var(--font-size-sm)', margin: 0 }}>
                            Approved
                        </p>
                    </div>

                    <div className="card" style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 'var(--font-size-3xl)', marginBottom: 'var(--spacing-sm)' }}>
                            ⏳
                        </div>
                        <p style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', margin: 0, color: 'var(--color-warning)' }}>
                            {stats.pending}
                        </p>
                        <p style={{ color: 'var(--color-gray)', fontSize: 'var(--font-size-sm)', margin: 0 }}>
                            Pending
                        </p>
                    </div>

                    <div className="card" style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 'var(--font-size-3xl)', marginBottom: 'var(--spacing-sm)' }}>
                            💰
                        </div>
                        <p style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'bold', margin: 0, color: 'var(--color-plum-primary)' }}>
                            {formatAmount(stats.totalApproved)}
                        </p>
                        <p style={{ color: 'var(--color-gray)', fontSize: 'var(--font-size-sm)', margin: 0 }}>
                            Total Approved
                        </p>
                    </div>
                </div>

                {/* Filters */}
                <div className="card" style={{ marginBottom: 'var(--spacing-lg)', padding: 'var(--spacing-lg)' }}>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap', alignItems: 'center' }}>
                        <span style={{ fontWeight: 600, color: 'var(--color-black)' }}>Filter:</span>
                        {['ALL', 'PROCESSING', 'APPROVED', 'REJECTED', 'PARTIAL', 'MANUAL_REVIEW'].map(status => (
                            <button
                                key={status}
                                onClick={() => setFilter(status as any)}
                                style={{
                                    padding: 'var(--spacing-sm) var(--spacing-md)',
                                    borderRadius: 'var(--radius-full)',
                                    border: 'none',
                                    cursor: 'pointer',
                                    fontWeight: 500,
                                    fontSize: 'var(--font-size-sm)',
                                    transition: 'all var(--transition-fast)',
                                    ...(filter === status ? {
                                        background: 'linear-gradient(135deg, var(--color-plum-primary), var(--color-plum-dark))',
                                        color: 'white',
                                        boxShadow: 'var(--shadow-md)',
                                    } : {
                                        background: 'white',
                                        color: 'var(--color-gray)',
                                        border: '1px solid var(--color-gray-light)',
                                    }),
                                }}
                                onMouseEnter={(e) => {
                                    if (filter !== status) {
                                        e.currentTarget.style.background = 'var(--color-gray-light)';
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (filter !== status) {
                                        e.currentTarget.style.background = 'white';
                                    }
                                }}
                            >
                                {status === 'ALL' ? 'All' : status.replace('_', ' ')}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Claims List */}
                {loading ? (
                    <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
                        <div className="spinner" style={{ margin: '0 auto var(--spacing-md)' }} />
                        <p style={{ color: 'var(--color-gray)' }}>Loading claims...</p>
                    </div>
                ) : filteredClaims.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
                        <div style={{ fontSize: 'var(--font-size-4xl)', marginBottom: 'var(--spacing-md)' }}>
                            📭
                        </div>
                        <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>No claims found</h3>
                        <p style={{ color: 'var(--color-gray)', marginBottom: 'var(--spacing-lg)' }}>
                            {filter === 'ALL' ? 'Start by submitting your first claim' : `No ${filter} claims`}
                        </p>
                        {filter === 'ALL' && (
                            <Link to="/" className="btn btn-primary">
                                Submit New Claim
                            </Link>
                        )}
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                        {filteredClaims.map(claim => (
                            <Link
                                key={claim.id}
                                to={`/claims/${claim.id}`}
                                style={{ textDecoration: 'none' }}
                            >
                                <div className="card" style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: 'var(--spacing-lg)',
                                }}>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-sm)' }}>
                                            <h4 style={{ margin: 0, color: 'var(--color-black)' }}>
                                                {claim.id}
                                            </h4>
                                            <StatusBadge status={claim.status} size="sm" />
                                        </div>
                                        <p style={{ margin: 0, color: 'var(--color-gray)', fontSize: 'var(--font-size-sm)' }}>
                                            Member: <strong>{claim.member_id}</strong> •
                                            Treatment: {formatDate(claim.treatment_date)} •
                                            Submitted: {formatDate(claim.submission_date)}
                                        </p>
                                        {claim.hospital_name && (
                                            <p style={{ margin: 'var(--spacing-xs) 0 0', color: 'var(--color-gray)', fontSize: 'var(--font-size-sm)' }}>
                                                🏥 {claim.hospital_name}
                                            </p>
                                        )}
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <p style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'bold', margin: 0, color: 'var(--color-plum-primary)' }}>
                                            {formatAmount(claim.total_amount)}
                                        </p>
                                        {claim.approved_amount !== null && (
                                            <p style={{ fontSize: 'var(--font-size-sm)', margin: 'var(--spacing-xs) 0 0', color: 'var(--color-success)' }}>
                                                Approved: {formatAmount(claim.approved_amount)}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ClaimsList;
