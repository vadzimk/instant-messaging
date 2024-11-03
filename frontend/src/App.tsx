import {createBrowserRouter, RouterProvider} from 'react-router-dom';
import ErrorPage from './pages/ErrorPage.tsx';
import Layout from './Layout.tsx';
import Home from './pages/Home.tsx';
import Index from './pages/Signup';
import {useEffect, useState} from 'react';
import {SocketClient} from './services/socketClient.ts';
import {useAppDispatch, useAppSelector} from './hooks.ts';
import {GetUserSchema} from './reducers/types';

const router = createBrowserRouter([
    {
        path: '/', element: <Layout/>, errorElement: <ErrorPage/>,
        children: [
            {index: true, element: <Home/>},
            {path: 'signup/', element: <Index/>},
        ]
    }
])


function App() {
    const [accessToken, setAccessToken] = useState<string | null>(
        window.localStorage.getItem('access_token'))

    const dispatch = useAppDispatch()
    const user = useAppSelector(state => state.user)

    useEffect(() => {
        const handleStorageChange = ()=> {
            const token = window.localStorage.getItem('access_token')
            setAccessToken(token)
        }

        window.addEventListener('storage', handleStorageChange)  // 'storage' event only triggers when changes are made to localStorage from another tab or window
        handleStorageChange() // to handle updates made within the same tab

        if(accessToken && user.id !== undefined){

            new SocketClient(accessToken, user as GetUserSchema, dispatch)
            console.log('SocketClient created')
        }
        return () => {
            try {
                SocketClient.getInstance() // if initialized
                SocketClient.disconnect()
            } catch {
                /* empty */
            } finally {
                window.removeEventListener('storage', handleStorageChange)
            }
        }
    }, [accessToken, dispatch, user])

    return (
        <>
            <RouterProvider router={router}/>
        </>

    )
}

export default App
