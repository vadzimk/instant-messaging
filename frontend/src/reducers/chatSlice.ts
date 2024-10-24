import {createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import {NotificationType, notify} from './notificationSlice.ts';
import {baseUrl, FastApiError} from './api.ts';
import {UserState} from './userSlice.ts';

type Message = [string, string, string] // Tuple: [message content, sender ID, recipient ID]

export interface NewContactFields {
    email: string
}

interface Contact extends NewContactFields {
    first_name: string;
    last_name: string;
}

interface Chat {
    id: number;
    contact: Contact;
    messages: Message[]
}

type ChatState = {
    chatList: Chat[]
    currentChat: number | null
}

const initialState: ChatState = {
    chatList: [],
    currentChat: null,
}

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        setCurrentChat(state, action: PayloadAction<number | null>) {
            state.currentChat = action.payload
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
            state.currentChat = newChat.id
        })
    }
})

export const addContact = createAsyncThunk<Contact, NewContactFields>(
    '/chat/addNewChat',
    async (contactFields: NewContactFields,
           {dispatch, rejectWithValue, getState}) => {
        const state = getState() as {user: UserState}
        const token = state.user.access_token
        try {
            // post request to /api/add-new-chat
            const res = await fetch(baseUrl + '/api/add-contact', {
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
            const data: Contact = await res.json()
            return data
        } catch (e) {
            const err = e as Error
            console.error('An error occurred: ', +err)
            dispatch(notify({message: "Could not add new chat", type: NotificationType.ERROR}))
            return rejectWithValue({detail: err.message})
        }
    }
)


export const {setCurrentChat} = chatSlice.actions
export default chatSlice
