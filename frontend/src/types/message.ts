export type MessageType =
    | "INFO"
    | "SUCCESS"
    | "WARNING"
    | "ERROR";

export interface AppMessage {
    id: string;
    type: MessageType;
    title?: string;
    message: string;
    timestamp: Date;
}