import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getClaim, getDecision, getClaimDocuments } from '../services/api';
import type { Claim, Decision, Document } from '../types';
import StatusBadge from './StatusBadge';

const ClaimDetails = () => {
    const { claimId } = useParams<{ claimId: string }>();
    const [claim, setClaim] = useState<Claim | null>(null);
    const [decision, setDecision] = useState<Decision | null>(null);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (claimId) {
            loadClaimData();
        }
    }, [claimId]);

    const loadClaimData = async () => {
        try {
            setLoading(true);
            const [claimData, documentsData] = await Promise.all([
                getClaim(claimId!),
                getClaimDocuments(claimId!),
            ]);

            setClaim(claimData);
            setDocuments(documentsData);

            // Try to load decision if claim is processed
            if (claimData.status !== 'PENDING' && claimData.status !== 'PROCESSING') {
                try {
                    const decisionData = await getDecision(claimId!);
                    setDecision(decisionData);
                } catch (err) {
                    console.log('Decision not available yet');
                }
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load claim details');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const formatAmount = (amount: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
        }).format(amount);
    };

    if (loading) {
        return (
            <div className="container">
                <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
                    <div className="spinner" style={{ margin: '0 auto var(--spacing-md)' }} />
                    <p style={{ color: 'var(--color-gray)' }}>Loading claim details...</p>
                </div>
            </div>
        );
    }

    if (error || !claim) {
        return (
            <div className="container">
                <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
                    <div style={{ fontSize: 'var(--font-size-4xl)', marginBottom: 'var(--spacing-md)' }}>
                        ⚠️
                    </div>
                    <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>Error Loading Claim</h3>
                    <p style={{ color: 'var(--color-gray)', marginBottom: 'var(--spacing-lg)' }}>
                        {error || 'Claim not found'}
                    </p>
                    <Link to="/claims" className="btn btn-primary">
                        Back to Claims
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="container">
            <div className="animate-fade-in">
                <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                    <Link to="/claims" style={{ color: 'var(--color-red-primary)', textDecoration: 'none', fontWeight: 500 }}>
                        ← Back to Claims
                    </Link>
                </div>

                {/* Header */}
                <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h2 style={{ marginBottom: 'var(--spacing-sm)' }}>Claim {claim.id}</h2>
                            <p style={{ color: 'var(--color-gray)', margin: 0 }}>
                                Submitted on {formatDate(claim.submission_date)}
                            </p>
                        </div>
                        <StatusBadge status={claim.status} size="lg" />
                    </div>
                </div>

                <div className="grid grid-cols-2" style={{ marginBottom: 'var(--spacing-lg)' }}>
                    {/* Claim Information */}
                    <div className="card">
                        <h3 style={{ marginBottom: 'var(--spacing-lg)', display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                            <span>📋</span> Claim Information
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                            <div>
                                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', margin: 0 }}>
                                    Member ID
                                </p>
                                <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, margin: 0, color: 'var(--color-black)' }}>
                                    {claim.member_id}
                                </p>
                            </div>
                            <div>
                                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', margin: 0 }}>
                                    Treatment Date
                                </p>
                                <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, margin: 0, color: 'var(--color-black)' }}>
                                    {formatDate(claim.treatment_date)}
                                </p>
                            </div>
                            {claim.hospital_name && (
                                <div>
                                    <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', margin: 0 }}>
                                        Hospital
                                    </p>
                                    <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, margin: 0, color: 'var(--color-black)' }}>
                                        {claim.hospital_name}
                                    </p>
                                </div>
                            )}
                            {claim.category && (
                                <div>
                                    <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', margin: 0 }}>
                                        Category
                                    </p>
                                    <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, margin: 0, color: 'var(--color-black)' }}>
                                        {claim.category}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Amount Information */}
                    <div className="card">
                        <h3 style={{ marginBottom: 'var(--spacing-lg)', display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                            <span>💰</span> Amount Details
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                            <div>
                                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', margin: 0 }}>
                                    Claimed Amount
                                </p>
                                <p style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', margin: 0, color: 'var(--color-black)' }}>
                                    {formatAmount(claim.total_amount)}
                                </p>
                            </div>
                            {claim.approved_amount !== null && (
                                <div>
                                    <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', margin: 0 }}>
                                        Approved Amount
                                    </p>
                                    <p style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', margin: 0, color: 'var(--color-success)' }}>
                                        {formatAmount(claim.approved_amount)}
                                    </p>
                                </div>
                            )}
                            {decision && decision.rejected_amount && decision.rejected_amount > 0 && (
                                <div>
                                    <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', margin: 0 }}>
                                        Rejected Amount
                                    </p>
                                    <p style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'bold', margin: 0, color: 'var(--color-red-primary)' }}>
                                        {formatAmount(decision.rejected_amount)}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Decision Details */}
                {decision && (
                    <>
                        <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                            <h3 style={{ marginBottom: 'var(--spacing-lg)', display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                                <span>🎯</span> Decision Details
                            </h3>

                            <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', marginBottom: 'var(--spacing-xs)' }}>
                                    Confidence Score
                                </p>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                                    <div style={{
                                        flex: 1,
                                        height: '24px',
                                        background: 'var(--color-gray-lighter)',
                                        borderRadius: 'var(--radius-full)',
                                        overflow: 'hidden',
                                        position: 'relative',
                                    }}>
                                        <div style={{
                                            height: '100%',
                                            width: `${decision.confidence_score * 100}%`,
                                            background: 'linear-gradient(90deg, var(--color-red-primary), var(--color-red-light))',
                                            borderRadius: 'var(--radius-full)',
                                            boxShadow: 'inset 0 -2px 6px rgba(255, 255, 255, 0.3)',
                                            transition: 'width 1s ease-out',
                                        }} />
                                    </div>
                                    <span style={{ fontWeight: 'bold', color: 'var(--color-black)', fontSize: 'var(--font-size-lg)' }}>
                                        {(decision.confidence_score * 100).toFixed(0)}%
                                    </span>
                                </div>
                            </div>

                            {decision.reasoning && decision.reasoning.length > 0 && (
                                <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                                    <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', marginBottom: 'var(--spacing-sm)', fontWeight: 600 }}>
                                        Reasoning
                                    </p>
                                    <ul style={{ margin: 0, paddingLeft: 'var(--spacing-lg)' }}>
                                        {decision.reasoning.map((reason, index) => (
                                            <li key={index} style={{ color: 'var(--color-gray)', marginBottom: 'var(--spacing-xs)' }}>
                                                {reason}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {decision.rejection_reasons && decision.rejection_reasons.length > 0 && (
                                <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                                    <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-red-primary)', marginBottom: 'var(--spacing-sm)', fontWeight: 600 }}>
                                        Rejection Reasons
                                    </p>
                                    <ul style={{ margin: 0, paddingLeft: 'var(--spacing-lg)' }}>
                                        {decision.rejection_reasons.map((reason, index) => (
                                            <li key={index} style={{ color: 'var(--color-red-dark)', marginBottom: 'var(--spacing-xs)' }}>
                                                {reason}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {decision.deductions && Object.keys(decision.deductions).length > 0 && (
                                <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                                    <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray)', marginBottom: 'var(--spacing-sm)', fontWeight: 600 }}>
                                        Deductions
                                    </p>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                                        {Object.entries(decision.deductions).map(([key, value]) => (
                                            <div key={key} style={{ display: 'flex', justifyContent: 'space-between', padding: 'var(--spacing-sm)', background: 'var(--color-cream-dark)', borderRadius: 'var(--radius-md)' }}>
                                                <span style={{ color: 'var(--color-gray)' }}>{key}</span>
                                                <span style={{ fontWeight: 600, color: 'var(--color-black)' }}>{formatAmount(value)}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {decision.next_steps && (
                                <div style={{
                                    padding: 'var(--spacing-md)',
                                    background: 'var(--color-cream-dark)',
                                    borderRadius: 'var(--radius-md)',
                                    borderLeft: '4px solid var(--color-red-primary)',
                                }}>
                                    <p style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, marginBottom: 'var(--spacing-xs)', color: 'var(--color-black)' }}>
                                        Next Steps
                                    </p>
                                    <p style={{ margin: 0, color: 'var(--color-gray)' }}>
                                        {decision.next_steps}
                                    </p>
                                </div>
                            )}
                        </div>
                    </>
                )}

                {/* Documents */}
                {documents.length > 0 && (
                    <div className="card">
                        <h3 style={{ marginBottom: 'var(--spacing-lg)', display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                            <span>📄</span> Documents ({documents.length})
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                            {documents.map(doc => (
                                <div
                                    key={doc.id}
                                    style={{
                                        padding: 'var(--spacing-md)',
                                        background: 'var(--color-cream-dark)',
                                        borderRadius: 'var(--radius-md)',
                                        border: '1px solid var(--color-gray-light)',
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-sm)' }}>
                                        <div>
                                            <p style={{ fontWeight: 600, margin: 0, color: 'var(--color-black)' }}>
                                                {doc.filename}
                                            </p>
                                            <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray)', margin: 0 }}>
                                                {doc.document_type.toUpperCase()}
                                            </p>
                                        </div>
                                        {doc.ocr_confidence && (
                                            <span style={{
                                                padding: 'var(--spacing-xs) var(--spacing-sm)',
                                                background: 'var(--color-white)',
                                                borderRadius: 'var(--radius-full)',
                                                fontSize: 'var(--font-size-xs)',
                                                fontWeight: 600,
                                                color: 'var(--color-gray)',
                                            }}>
                                                OCR: {(doc.ocr_confidence * 100).toFixed(0)}%
                                            </span>
                                        )}
                                    </div>
                                    {doc.extracted_data && (
                                        <div style={{
                                            marginTop: 'var(--spacing-sm)',
                                            padding: 'var(--spacing-sm)',
                                            background: 'var(--color-white)',
                                            borderRadius: 'var(--radius-sm)',
                                            fontSize: 'var(--font-size-xs)',
                                        }}>
                                            <pre style={{ margin: 0, overflow: 'auto', color: 'var(--color-gray)' }}>
                                                {JSON.stringify(doc.extracted_data, null, 2)}
                                            </pre>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ClaimDetails;
