import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchMembers, submitClaim } from '../services/api';
import type { Member } from '../types';
import FileUpload from './FileUpload';

interface SubmitClaimProps {
    showToast: (type: 'success' | 'error' | 'info', message: string) => void;
}

const SubmitClaim = ({ showToast }: SubmitClaimProps) => {
    const navigate = useNavigate();
    const [members, setMembers] = useState<Member[]>([]);
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const [formData, setFormData] = useState({
        memberId: '',
        treatmentDate: '',
    });
    const [files, setFiles] = useState<File[]>([]);

    useEffect(() => {
        loadMembers();
    }, []);

    const loadMembers = async () => {
        try {
            setLoading(true);
            const data = await fetchMembers();
            setMembers(data);
        } catch (error) {
            showToast('error', 'Failed to load members');
            console.error('Error loading members:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!formData.memberId || !formData.treatmentDate || files.length === 0) {
            showToast('error', 'Please fill all fields and upload at least one document');
            return;
        }

        try {
            setSubmitting(true);
            const submitFormData = new FormData();
            submitFormData.append('member_id', formData.memberId);
            submitFormData.append('treatment_date', formData.treatmentDate);
            files.forEach(file => {
                submitFormData.append('files', file);
            });

            const response = await submitClaim(submitFormData);
            showToast('success', `Claim submitted successfully! ID: ${response.claim_id}`);

            // Reset form
            setFormData({ memberId: '', treatmentDate: '' });
            setFiles([]);

            // Navigate to claim details after a short delay
            setTimeout(() => {
                navigate(`/claims/${response.claim_id}`);
            }, 1500);
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Failed to submit claim';
            showToast('error', message);
            console.error('Error submitting claim:', error);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="container">
            <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
                <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-2xl)' }}>
                    <h2 style={{ marginBottom: 'var(--spacing-sm)' }}>Submit New Claim</h2>
                    <p style={{ color: 'var(--color-gray)', fontSize: 'var(--font-size-lg)' }}>
                        Upload your medical documents and submit your OPD claim
                    </p>
                </div>

                <div className="card">
                    <form onSubmit={handleSubmit}>
                        <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                            <label className="label" htmlFor="memberId">
                                Select Member *
                            </label>
                            {loading ? (
                                <div style={{ padding: 'var(--spacing-md)', textAlign: 'center' }}>
                                    <div className="spinner" style={{ margin: '0 auto' }} />
                                </div>
                            ) : (
                                <select
                                    id="memberId"
                                    className="input select"
                                    value={formData.memberId}
                                    onChange={(e) => setFormData({ ...formData, memberId: e.target.value })}
                                    required
                                >
                                    <option value="">Choose a member...</option>
                                    {members.map(member => (
                                        <option key={member.id} value={member.id}>
                                            {member.name} ({member.id})
                                        </option>
                                    ))}
                                </select>
                            )}
                        </div>

                        <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                            <label className="label" htmlFor="treatmentDate">
                                Treatment Date *
                            </label>
                            <input
                                id="treatmentDate"
                                type="date"
                                className="input"
                                value={formData.treatmentDate}
                                onChange={(e) => setFormData({ ...formData, treatmentDate: e.target.value })}
                                max={new Date().toISOString().split('T')[0]}
                                required
                            />
                        </div>

                        <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                            <label className="label">
                                Upload Documents * (Prescription, Bill, Reports)
                            </label>
                            <FileUpload files={files} onFilesChange={setFiles} />
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={submitting}
                            style={{ width: '100%', padding: 'var(--spacing-md)' }}
                        >
                            {submitting ? (
                                <>
                                    <div className="spinner" />
                                    Processing Claim...
                                </>
                            ) : (
                                <>
                                    <span style={{ fontSize: 'var(--font-size-lg)' }}>📤</span>
                                    Submit Claim
                                </>
                            )}
                        </button>
                    </form>
                </div>

                <div style={{
                    marginTop: 'var(--spacing-xl)',
                    padding: 'var(--spacing-lg)',
                    background: 'var(--color-gray-lighter)',
                    borderRadius: 'var(--radius-lg)',
                    border: '1px solid var(--color-gray-light)',
                }}>
                    <h4 style={{ marginBottom: 'var(--spacing-md)', display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <span>💡</span> Quick Tips
                    </h4>
                    <ul style={{ margin: 0, paddingLeft: 'var(--spacing-lg)', color: 'var(--color-gray)' }}>
                        <li>Upload clear, readable images or PDFs of your documents</li>
                        <li>Include prescription from a registered doctor</li>
                        <li>Attach original bills and payment receipts</li>
                        <li>Processing typically takes 2-5 minutes with AI assistance</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default SubmitClaim;
