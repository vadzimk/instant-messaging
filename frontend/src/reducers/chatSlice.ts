import {createAsyncThunk, createSlice} from '@reduxjs/toolkit';

interface GetMessageSchema {
    id: string
    content: string
    created_at: string // // ISO 8601 datetime format
    user_from_id: string // uuid
    user_to_id: string // uuid
}

export interface Chat {
    id: string; // uuid
    contactId: string; // uuid
    messages: GetMessageSchema[]
}

type ChatState = {
    chatList: Chat[]
}
const initialState: ChatState = {
    chatList: [],
}

const chatSlice = createSlice(({
    name: 'chat',
    initialState,
    reducers: {},
    // extraReducers: {}
}))

export const sendMessage = createAsyncThunk(
    '/chat/sendMessage',
    async (messageFields,
           {dispatch, rejectWithValue, getState}) => {
        try {

        } catch (e){

        }
    }
)

// eslint-disable-next-line no-empty-pattern
export const {} = chatSlice.actions

export default chatSlice
