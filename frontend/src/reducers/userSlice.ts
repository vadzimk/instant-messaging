import {createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SignupInputs} from '../pages/Signup/SignupForm.tsx';
import {NotificationType, notify} from './notificationSlice.ts';


type UserState = {
    id: string | null;
    status: 'idle' | 'loading' | 'succeeded' | 'failed';

}
const initialState: UserState = {
    id: null,
    status: 'idle'
}

interface UserCreateOut {
    email: string
    first_name: string
    last_name: string
}

interface UserSignUpError {
    detail: string
}

interface UserLoginOut {
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
        builder.addCase(signupUser.fulfilled, (state, action: PayloadAction<UserCreateOut>) => {
            if (action.payload) {
                const {email} = action.payload
                state.id = email
            }

        })
    }
})

const baseUrl = 'http://localhost:8000'

export const signupUser = createAsyncThunk<UserCreateOut, SignupInputs>(
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
                const errorData: UserSignUpError = await res.json()
                dispatch(notify({message: "Could not sign up", type: NotificationType.ERROR}))
                console.error(errorData.detail)
                return rejectWithValue(errorData)
            }
            const data: UserCreateOut = await res.json()
            window.localStorage.setItem('UserCreateOut', JSON.stringify(data))
            return data
        } catch (e) {
            const err = e as Error
            console.error("An error occured: " + err)
            dispatch(notify({message: "Could not sign up", type: NotificationType.ERROR}))
            return rejectWithValue({detail: err.message})
        }
    })

export const {
    userLoggedIn,
    userLoggedOut
} = userSlice.actions

export default userSlice
