import {createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import {NotificationType, notify} from './notificationSlice.ts';
import {baseUrl, FastApiError} from './api.ts';
import {UserState} from './userSlice.ts';


export interface CreateContactSchema {
    email: string
}

export interface GetContactSchema {
    id: string // uuid
    first_name: string;
    last_name: string;
}

interface GetContactsSchema {
    contacts: GetContactSchema[];
}

export type ContactsState = {
    contactList: GetContactSchema[]
    currentContactId: string | null
}

const initialState: ContactsState = {
    contactList: [],
    currentContactId: null,
}

const contactsSlice = createSlice({
    name: 'contacts',
    initialState,
    reducers: {
        setCurrentContact(state, action: PayloadAction<string | null>) {
            state.currentContactId = action.payload
        }
    },
    extraReducers: builder => {
        builder.addCase(addContact.fulfilled, (state, action) => {
            state.contactList = [...state.contactList, action.payload]
            state.currentContactId = action.payload.id
        }).addCase(getContacts.fulfilled, (state, action) => {
            if (!action.payload.contacts.length) {
                return state
            }
            state.contactList = action.payload.contacts
            if (state.contactList.length > 0) {
                state.currentContactId = state.contactList[state.contactList.length - 1].id
            }
        })
    }
})

export const addContact = createAsyncThunk<GetContactSchema, CreateContactSchema>(
    '/contacts/add',
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
    '/contacts/get',
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

export const {setCurrentContact} = contactsSlice.actions
export default contactsSlice
