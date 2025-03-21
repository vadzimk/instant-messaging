import {createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import {FastApiError, fetchWithAuthHandler} from '../services/api.ts';
import {AppDispatch, RootState} from '../store.ts';
import {ContactsState, CreateContactSchema, GetContactSchema, GetContactsSchema} from './types';


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
            `/api/contacts`,
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
            `/api/contacts`,
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
