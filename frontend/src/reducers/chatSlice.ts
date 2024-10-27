import {createAsyncThunk, createSlice} from '@reduxjs/toolkit';
import {SocketClient} from '../services/socketClient.ts';
import {NotificationType, notify} from './notificationSlice.ts';

interface GetMessageSchema {
    id: string;
    content: string;
    created_at: string; // // ISO 8601 datetime format
    user_from_id: string; // uuid
    user_to_id: string; // uuid
}

interface GetMessagesSchema {
    messages: GetMessageSchema[]
}

export interface SioErrorSchema {
    success: boolean
    data: any
    errors: { field: string, message: string }[] | string[]
}

interface CreateMessageSchema {
    contact_id: string; // uuid
    content: string;
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
    extraReducers: builder => {
        builder.addCase(sendMessage.fulfilled, (state, action) => {
            // TODO chat list is empty
            state.chatList.find(ch => (
                ch.contactId === action.payload.user_from_id || ch.contactId === action.payload.user_to_id))?.messages.push(action.payload) // mutation is allowed in redux toolkit, bc it uses immer library
        })
    }
}))

export const sendMessage = createAsyncThunk<GetMessageSchema, CreateMessageSchema, { rejectValue: SioErrorSchema }>(
    '/chat/sendMessage',
    async (messageFields: CreateMessageSchema,
           thunkAPI) => {
        try {
            const socketClient = SocketClient.getInstance()
            const data = await socketClient.emitWithAck('message', {
                contact_id: messageFields.contact_id,
                content: messageFields.content
            })
            if (!data.success) {
                thunkAPI.dispatch(notify({message: "Could not send message", type: NotificationType.ERROR}))
                console.error('Could not send message')
                return thunkAPI.rejectWithValue(data.errors)
            }
            return data

        } catch (e) {
            thunkAPI.dispatch(notify({message: "Could not send message", type: NotificationType.ERROR}))
            console.error(e)
            return thunkAPI.rejectWithValue({success: false, data: messageFields, errors: ["Could not send message"]})

        }
    }
)

// eslint-disable-next-line no-empty-pattern
export const {} = chatSlice.actions

export default chatSlice
