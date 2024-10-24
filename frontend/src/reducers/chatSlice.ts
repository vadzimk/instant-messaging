import {createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import {NotificationType, notify} from './notificationSlice.ts';
import {baseUrl, FastApiError} from './api.ts';
import {UserState} from './userSlice.ts';

type Message = [string, string, string] // Tuple: [message content, sender ID, recipient ID]

export interface CreateContactSchema {
    email: string
}

interface GetContactSchema extends CreateContactSchema {
    first_name: string;
    last_name: string;
}

interface GetContactsSchema {
    contacts: GetContactSchema[];
}

export interface Chat {
    id: number; // positive non-zero
    contact: GetContactSchema;
    messages: Message[]
}

type ChatState = {
    chatList: Chat[]
    currentChatId: number | null
}

const initialState: ChatState = {
    chatList: [],
    currentChatId: null,
}

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        setCurrentChat(state, action: PayloadAction<number | null>) {
            state.currentChatId = action.payload
        }
    },
    extraReducers: builder => {
        builder.addCase(addContact.fulfilled, (state, action) => {
            const newChat: Chat = {
                id: state.chatList.length + 1,
                contact: action.payload,
                messages: []
            }
            state.chatList = [...state.chatList, newChat]
            state.currentChatId = newChat.id
        }).addCase(getContacts.fulfilled, (state, action) => {
            if (!action.payload.contacts.length) {
                return state
            }
            state.chatList = action.payload.contacts.map((c, index) => {
                return {
                    id: index + 1,
                    contact: c,
                    messages: []
                }
            })
            if (state.chatList.length > 0) {
                state.currentChatId = state.chatList.length
            }
        })
    }
})

export const addContact = createAsyncThunk<GetContactSchema, CreateContactSchema>(
    '/chat/addContact',
    async (contactFields: CreateContactSchema,
           {dispatch, rejectWithValue, getState}) => {
        const state = getState() as { user: UserState }
        const token = state.user.access_token
        try {
            const res = await fetch(baseUrl + '/api/contacts', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(contactFields)
            })
            if (!res.ok) {
                const errorData: FastApiError = await res.json()
                dispatch(notify({message: "Could not add new chat", type: NotificationType.ERROR}))
                console.error(errorData.detail)
                return rejectWithValue(errorData)
            }
            const data: GetContactSchema = await res.json()
            return data
        } catch (e) {
            const err = e as Error
            console.error('An error occurred: ', +err)
            dispatch(notify({message: "Could not add new chat", type: NotificationType.ERROR}))
            return rejectWithValue({detail: err.message})
        }
    }
)

export const getContacts = createAsyncThunk<GetContactsSchema>(
    '/chat/getContacts',
    async (_, {dispatch, rejectWithValue, getState}) => {
        const state = getState() as { user: UserState }
        const token = state.user.access_token
        try {
            const res = await fetch(baseUrl + '/api/contacts', {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            })
            if (!res.ok) {
                const errorData: FastApiError = await res.json()
                dispatch(notify({message: "Could not get contacts", type: NotificationType.ERROR}))
                console.error(errorData.detail)
                return rejectWithValue(errorData)
            }
            const data: GetContactsSchema = await res.json()
            return data
        } catch (e) {
            const err = e as Error
            console.error('An error occurred: ', +err)
            dispatch(notify({message: "Could not get contacts", type: NotificationType.ERROR}))
            return rejectWithValue({detail: err.message})
        }
    }
)

export const {setCurrentChat} = chatSlice.actions
export default chatSlice
