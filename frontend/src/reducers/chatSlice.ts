import {createAsyncThunk, createSlice} from '@reduxjs/toolkit';
import {SocketClient} from '../services/socketClient.ts';
import {NotificationType, notify} from './notificationSlice.ts';
import {AppDispatch, RootState} from '../store.ts';
import {
    Chat,
    ChatState,
    CreateMessageSchema,
    ErrorSchema,
    GetMessageSchema,
    GetMessagesSchema,
    SioResponseSchema
} from './types';
import {baseUrl, fetchWithAuthHandler} from '../services/api.ts';


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
                    contactId: action.payload.data.user_from_id == action.payload.userId ? action.payload.data.user_to_id : action.payload.data.user_from_id,
                    messages: [action.payload.data]
                }
                state.chatList.push(newChat)
            }
        }).addCase(getMessages.fulfilled, (state, action) => {
            const chat = state.chatList.find(
                ch => ch.contactId === action.payload.contactId)
            if (chat) {
                chat.messages = action.payload.data.messages
            } else {
                const newChat: Chat = {
                    contactId: action.payload.contactId,
                    messages: action.payload.data.messages
                }
                state.chatList.push(newChat)
            }
        })
    }
}))

export const sendMessage = createAsyncThunk<{
    data: GetMessageSchema,
    userId: string | undefined
}, CreateMessageSchema, { rejectValue: ErrorSchema }>(
    '/chat/sendMessage',
    async (messageFields: CreateMessageSchema,
           thunkAPI) => {
        try {
            const socketClient = SocketClient.getInstance()
            const res: SioResponseSchema = await socketClient.emitWithAck('message_send', {
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

export const getMessages = createAsyncThunk<{ data: GetMessagesSchema, contactId: string }, string>(
    '/chat/getMessages',
    async (contactId: string, thunkAPI) => {
        const data = await fetchWithAuthHandler<GetMessagesSchema>(
            `${baseUrl}/api/chats/${contactId}`,
            {
                method: "GET"
            },
            thunkAPI.getState as () => RootState,
            thunkAPI.dispatch as AppDispatch,
            thunkAPI.rejectWithValue,
            "Could not get messages"
        )
        return {data, contactId}
    }
)

export const selectChatByContactId = (state: RootState, contactId: string | null ) =>
    state.chat.chatList.find(
        ch => ch.contactId === contactId)

// eslint-disable-next-line no-empty-pattern
export const {} = chatSlice.actions

export default chatSlice
