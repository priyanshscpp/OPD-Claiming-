import axios from 'axios';
import type {
    Member,
    Claim,
    Decision,
    Document,
    ClaimSubmitResponse,
    ClaimFilters
} from '../types';

const api = axios.create({
    baseURL: `https://ai-powered-opd-claim-adjudication-engine-production.up.railway.app/api/v1`,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const fetchMembers = async (): Promise<Member[]> => {
    const response = await api.get<Member[]>('/members');
    return response.data;
};

export const getMember = async (memberId: string): Promise<Member> => {
    const response = await api.get<Member>(`/members/${memberId}`);
    return response.data;
};

export const submitClaim = async (formData: FormData): Promise<ClaimSubmitResponse> => {
    const response = await api.post<ClaimSubmitResponse>('/claims', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getClaim = async (claimId: string): Promise<Claim> => {
    const response = await api.get<Claim>(`/claims/${claimId}`);
    return response.data;
};

export const listClaims = async (filters?: ClaimFilters): Promise<Claim[]> => {
    const response = await api.get<Claim[]>('/claims', { params: filters });
    return response.data;
};

export const getClaimDocuments = async (claimId: string): Promise<Document[]> => {
    const response = await api.get<Document[]>(`/claims/${claimId}/documents`);
    return response.data;
};

export const getDecision = async (claimId: string): Promise<Decision> => {
    const response = await api.get<Decision>(`/decisions/${claimId}`);
    return response.data;
};

export default api;
