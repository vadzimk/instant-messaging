import {GetUserSchema} from './userTypes.ts';

export interface GetMessageSchema {
    id: string;
    content: string;
    created_at: string; // // ISO 8601 datetime format
    user_from_id: string; // uuid
    user_to_id: string; // uuid
}
export interface MessageReceivedPayloadType {
    appUser: GetUserSchema
    message: GetMessageSchema
}

export interface GetMessagesSchema {
    messages: GetMessageSchema[]
}

export type ServerValidationError = {
    field: string,
    message: string []
}

export interface SioResponseSchema {
    success: boolean
    data: any
    errors: ServerValidationError[]
}

export type ErrorSchema = {
    errors: ServerValidationError[] | string[]
}

export interface CreateMessageSchema {
    contact_id: string; // uuid
    content: string;
}

export interface Chat {
    contactId: string; // uuid
    messages: GetMessageSchema[]
}

export type ChatState = {
    chatList: Chat[]
}
