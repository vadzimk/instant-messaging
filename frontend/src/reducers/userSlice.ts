import {createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SignupInputs} from '../pages/Signup/SignupForm.tsx';
import {NotificationType, notify} from './notificationSlice.ts';
import {LoginFields} from '../pages/Login/LoginForm.tsx';
import {baseUrl, FastApiError} from './api.ts';


export type UserState = {
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

interface UserSignupOut {
    email: string
    first_name: string
    last_name: string
}

interface UserLoginOut {
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
        userLoggedIn: function (state, action: PayloadAction<UserLoginOut>) {
            return {...state, ...action.payload}
        },
        userLoggedOut: function () {
            window.localStorage.removeItem('access_token')
            return initialState
        }
    },
    extraReducers: builder => {
        builder.addCase(loginUser.fulfilled, (state, action: PayloadAction<UserLoginOut>) => {
            return {...state, ...action.payload, status: 'succeeded'}
        })

    }
})


export const signupUser = createAsyncThunk<UserSignupOut, SignupInputs>(
    '/user/signup',
    async (userSignupFields: SignupInputs, {dispatch, rejectWithValue}) => {
        try {
            const res = await fetch(baseUrl + '/api/signup', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(userSignupFields)
            })
            if (!res.ok) {
                const errorData: FastApiError = await res.json()
                dispatch(notify({message: "Could not sign up", type: NotificationType.ERROR}))
                console.error(errorData.detail)
                return rejectWithValue(errorData)
            }
            const data: UserSignupOut = await res.json()
            // window.localStorage.setItem('UserCreateOut', JSON.stringify(data))
            return data
        } catch (e) {
            const err = e as Error
            console.error("An error occurred: " + err)
            dispatch(notify({message: "Could not sign up", type: NotificationType.ERROR}))
            return rejectWithValue({detail: err.message})
        }
    })

export const loginUser = createAsyncThunk<UserLoginOut, LoginFields>(
    '/user/login',
    async (userLoginFields: LoginFields, {dispatch, rejectWithValue}) => {
        try {
            const form = new FormData()
            form.append("username", userLoginFields.email)
            form.append("password", userLoginFields.password)
            const res = await fetch(baseUrl + '/api/login', {
                method: "POST",
                body: form, // send as FormData
            })
            if (!res.ok) {
                const errorData: FastApiError = await res.json()
                dispatch(notify({message: "Could not log in", type: NotificationType.ERROR}))
                console.error(errorData.detail)
                return rejectWithValue(errorData)
            }
            const data: UserLoginOut = await res.json()
            window.localStorage.setItem('access_token', data.access_token)
            // window.localStorage.setItem('UserLoginOut', JSON.stringify(data))
            return data
        } catch (e) {
            const err = e as Error
            console.error("An error occurred: " + err)
            dispatch(notify({message: "Could not log in", type: NotificationType.ERROR}))
            return rejectWithValue({detail: err.message})
        }
    }
)

export const {
    userLoggedIn,
    userLoggedOut
} = userSlice.actions

export default userSlice
