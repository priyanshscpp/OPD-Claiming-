// Type definitions for the OPD Claim Adjudication System

export enum ClaimStatus {
    PENDING = 'PENDING',
    PROCESSING = 'PROCESSING',
    APPROVED = 'APPROVED',
    REJECTED = 'REJECTED',
    PARTIAL = 'PARTIAL',
    MANUAL_REVIEW = 'MANUAL_REVIEW',
}

export interface Member {
    id: string;
    name: string;
    policy_id: string;
    join_date: string;
    annual_limit_used: number;
    created_at: string;
    gender?: string;
}

export interface Claim {
    id: string;
    member_id: string;
    submission_date: string;
    treatment_date: string;
    total_amount: number;
    approved_amount: number | null;
    status: ClaimStatus;
    category: string | null;
    hospital_name: string | null;
    created_at: string;
}

export interface Document {
    id: string;
    claim_id: string;
    document_type: string;
    filename: string;
    file_url: string;
    extracted_data: Record<string, any> | null;
    ocr_confidence: number | null;
    created_at: string;
}

export interface Decision {
    id: string;
    claim_id: string;
    decision: ClaimStatus;
    approved_amount: number;
    rejected_amount: number | null;
    rejection_reasons: string[];
    confidence_score: number;
    reasoning: string[];
    notes: string | null;
    next_steps: string | null;
    flags: string[];
    deductions: Record<string, number>;
    created_at: string;
}

export interface ClaimSubmitResponse {
    success: boolean;
    claim_id: string;
    status: ClaimStatus;
    approved_amount: number;
    confidence_score: number;
    message: string;
}

export interface ApiError {
    detail: string;
}

export interface ClaimFilters {
    member_id?: string;
    status?: ClaimStatus;
    skip?: number;
    limit?: number;
}
