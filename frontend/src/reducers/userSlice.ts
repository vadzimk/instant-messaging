import {createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SignupInputs} from '../pages/Signup/SignupForm.tsx';
import {LoginFields} from '../pages/Login/LoginForm.tsx';
import {baseUrl, fetchWithHandler} from '../services/api.ts';
import {AppDispatch} from '../store.ts';


export type UserState = {
    id: string // uuid
    email?: string
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    first_name?: string
    last_name?: string
    access_token?: string
    token_type?: string
}
const initialState: UserState = {
    status: 'idle',
}

interface GetUserSchema {
    id: string // uuid
    email: string
    first_name: string
    last_name: string
}

interface LoginUserSchema {
    id: string // uuid
    email: string
    first_name: string
    last_name: string | undefined
    access_token: string
    token_type: string
}


const userSlice = createSlice({
    name: 'user',
    initialState,
    reducers: {
        userLoggedIn: function (state, action: PayloadAction<LoginUserSchema>) {
            return {...state, ...action.payload}
        },
        userLoggedOut: function () {
            window.localStorage.removeItem('access_token')
            return initialState
        }
    },
    extraReducers: builder => {
        builder.addCase(loginUser.fulfilled, (state, action: PayloadAction<LoginUserSchema>) => {
            return {...state, ...action.payload, status: 'succeeded'}
        })

    }
})


export const signupUser = createAsyncThunk<GetUserSchema, SignupInputs>(
    '/user/signup',
    async (userSignupFields: SignupInputs, thunkAPI) => {
        return await fetchWithHandler(
            `${baseUrl}/api/users`,
            {
                method: "POST",
                body: JSON.stringify(userSignupFields)
            },
            thunkAPI.dispatch as AppDispatch,
            thunkAPI.rejectWithValue,
            "Could not sign up"
        )
    })

export const loginUser = createAsyncThunk<LoginUserSchema, LoginFields>(
    '/user/login',
    async (userLoginFields: LoginFields, thunkAPI) => {
        const form = new FormData()
        form.append("username", userLoginFields.email)
        form.append("password", userLoginFields.password)
        const data = await fetchWithHandler(
            `${baseUrl}/api/users/login`,
            {
                method: "POST",
                body: form, // send as FormData
            },
            thunkAPI.dispatch as AppDispatch,
            thunkAPI.rejectWithValue,
            "Could not log in"
        )
        window.localStorage.setItem('access_token', data.access_token)
        return data
    }
)

export const {
    userLoggedIn,
    userLoggedOut
} = userSlice.actions

export default userSlice
