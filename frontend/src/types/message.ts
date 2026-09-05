/** Visual severity used to render an application message. */
export type MessageType =
    | "INFO"
    | "SUCCESS"
    | "WARNING"
    | "ERROR";

/** Message shown in the dialog panel. */
export interface AppMessage {
    id: string;
    type: MessageType;
    title?: string;
    message: string;
    timestamp: Date;
}