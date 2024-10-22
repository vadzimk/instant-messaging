import {createAsyncThunk, createSlice} from '@reduxjs/toolkit';

export enum NotificationType {
    ERROR = 'error',
    WARNING = 'warning',
    INFO = 'info',
    SUCCESS = 'success'
}

interface NotificationState {
    message: string
    type: NotificationType | null
}

interface NotificationConfig extends NotificationState {
    timeout: number
}

const initialState: NotificationState = {
    message: '',
    type: null,
}

const notificationSlice = createSlice({
    name: 'notification',
    initialState,
    reducers: {
        notify: function (state, action) {
            state.message = action.payload.message;
            state.type = action.payload.type;
        },
        clearNotification: function () {
            return initialState  // reset state
        }
    }
})

const sleep = (ms: number) => new Promise<void>(resolve => {
    setTimeout(() => resolve(), ms)
})

export const notifyTemp = createAsyncThunk(
    'notification/timed',
    async (conf: NotificationConfig, {dispatch}) => {
        // notification with timeout
        const {timeout, ...notification} = conf
        const ms = timeout ? timeout * 1000 : 5000
        dispatch(notify(notification))
        await sleep(ms)
        dispatch(notify({type: null, message: ''}))
    })


export const {
    notify,
    clearNotification
} = notificationSlice.actions

export default notificationSlice
