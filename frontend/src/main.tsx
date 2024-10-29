import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './styles/index.css'
import {Provider} from 'react-redux';
import {store} from './store.ts';
import {PersistGate} from 'redux-persist/integration/react'
import {persistStore} from 'redux-persist'
import ErrorBoundary from './pages/ErrorBoundary'

const persistor = persistStore(store)

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <Provider store={store}>
            <ErrorBoundary>
                <PersistGate loading={null} persistor={persistor}>
                    <App/>
                </PersistGate>
            </ErrorBoundary>
        </Provider>
    </React.StrictMode>,
)
