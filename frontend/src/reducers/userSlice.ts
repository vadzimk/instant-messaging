import {createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SignupInputs} from '../pages/Signup/SignupForm.tsx';
import {LoginFields} from '../pages/Login/LoginForm.tsx';
import {fetchWithHandler} from '../services/api.ts';
import {AppDispatch} from '../store.ts';
import {GetUserSchema, LoginUserSchema, UserState} from './types';


const initialState: UserState = {
    status: 'idle'
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
            `/api/users`,
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
            `/api/users/login`,
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
