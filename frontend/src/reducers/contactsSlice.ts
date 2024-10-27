import {createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import {baseUrl, FastApiError, fetchWithAuthHandler} from '../services/api.ts';
import {AppDispatch, RootState} from '../store.ts';


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

export const addContact = createAsyncThunk<GetContactSchema, CreateContactSchema, { rejectValue: FastApiError }>(
    '/contacts/add',
    async (contactFields: CreateContactSchema,
           thunkAPI) => {
        return await fetchWithAuthHandler<GetContactSchema>(
            `${baseUrl}/api/contacts`,
            {
                method: "POST",
                body: JSON.stringify(contactFields)
            },
            thunkAPI.getState as () => RootState,
            thunkAPI.dispatch as AppDispatch,
            thunkAPI.rejectWithValue,
            "Could not add new chat"
        )
    }
)

export const getContacts = createAsyncThunk<GetContactsSchema>(
    '/contacts/get',
    async (_, thunkAPI) => {
        return await fetchWithAuthHandler<GetContactsSchema>(
            `${baseUrl}/api/contacts`,
            {
                method: "GET",
            },
            thunkAPI.getState as () => RootState,
            thunkAPI.dispatch as AppDispatch,
            thunkAPI.rejectWithValue,
            "Could not get contacts"
        )
    }
)

export const {setCurrentContact} = contactsSlice.actions
export default contactsSlice
