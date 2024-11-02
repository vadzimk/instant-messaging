export type UserState = {
    id?: string // uuid
    email?: string
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    first_name?: string
    last_name?: string
    access_token?: string
    token_type?: string
}

export interface GetUserSchema {
    id: string // uuid
    email: string
    first_name: string
    last_name: string
}

export interface LoginUserSchema {
    id: string // uuid
    email: string
    first_name: string
    last_name?: string
    access_token: string
    token_type: string
}
