import {combineReducers, configureStore} from '@reduxjs/toolkit';
import {persistReducer} from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import userSlice from './reducers/userSlice.ts';
import notificationSlice from './reducers/notificationSlice.ts';
import contactsSlice from './reducers/contactsSlice.ts';
import chatSlice from './reducers/chatSlice.ts';


const reducers = combineReducers({
    user: userSlice.reducer,
    notification: notificationSlice.reducer,
    contacts: contactsSlice.reducer,
    chat: chatSlice.reducer,
})

const persistConfig = {
    key: 'root',
    storage,
}

const persistedReducer = persistReducer(persistConfig, reducers)

// https://redux.js.org/usage/configuring-your-store#simplifying-setup-with-redux-toolkit
export const store = configureStore({
    reducer: persistedReducer,
})

// Get the type of our store variable
export type AppStore = typeof store
// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<AppStore['getState']>
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = AppStore['dispatch']
