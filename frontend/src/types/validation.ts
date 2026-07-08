export interface ValidationError {
    code: string;
    message: string;
}

export interface ValidationResult {
    valid: boolean;
    message: string;
    errors: ValidationError[];
}