import {createAsyncThunk, createSlice} from '@reduxjs/toolkit';
import {SocketClient} from '../services/socketClient.ts';
import {NotificationType, notify} from './notificationSlice.ts';
import {v4 as uuidv4} from 'uuid'
import {RootState} from '../store.ts';

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

type ServerValidationError = {
    field: string,
    message: string []
}

export interface SioResponseSchema {
    success: boolean
    data: any
    errors: ServerValidationError[]
}

type ErrorSchema = {
    errors: ServerValidationError[] | string[]
}

interface CreateMessageSchema {
    contact_id: string; // uuid
    content: string;
}

export interface Chat {
    id: string; // uuid ! generated on client !
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
            const currentChat = state.chatList.find(ch => (
                ch.contactId === action.payload.data.user_from_id || ch.contactId === action.payload.data.user_to_id))
            if (currentChat) {
                currentChat.messages.push(action.payload.data) // mutation is allowed in redux toolkit, bc toolkit uses immer library
            } else {
                const newChat: Chat = {
                    id: uuidv4(),
                    contactId: action.payload.data.user_from_id == action.payload.userId ? action.payload.data.user_to_id : action.payload.data.user_from_id,
                    messages: [action.payload.data]
                }
                state.chatList.push(newChat)
            }
        })
    }
}))

export const sendMessage = createAsyncThunk<{ data: GetMessageSchema, userId: string }, CreateMessageSchema, { rejectValue: ErrorSchema }>(
    '/chat/sendMessage',
    async (messageFields: CreateMessageSchema,
           thunkAPI) => {
        try {
            const socketClient = SocketClient.getInstance()
            const res: SioResponseSchema = await socketClient.emitWithAck('message', {
                contact_id: messageFields.contact_id,
                content: messageFields.content
            })
            if (!res.success) {
                console.dir(res)
                thunkAPI.dispatch(notify({message: "Could not send message", type: NotificationType.ERROR}))
                console.error('Could not send message')
                return thunkAPI.rejectWithValue({errors: res.errors})
            }
            const state = thunkAPI.getState() as RootState
            const userId = state.user.id
            return {data: res.data, userId}

        } catch (e) {
            thunkAPI.dispatch(notify({message: "Could not send message", type: NotificationType.ERROR}))
            console.error(e)
            return thunkAPI.rejectWithValue({errors: ["Could not send message"]})

        }
    }
)

// eslint-disable-next-line no-empty-pattern
export const {} = chatSlice.actions

export default chatSlice
