import {createBrowserRouter, RouterProvider} from 'react-router-dom';
import ErrorPage from './pages/ErrorPage.tsx';
import Layout from './Layout.tsx';
import Home from './pages/Home.tsx';
import Index from './pages/Signup';
import {useEffect} from 'react';
import {SocketClient} from './services/socketClient.ts';

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
    useEffect(() => {
        const access_token = window.localStorage.getItem('access_token')
        const socketClient = new SocketClient(access_token) // init singleton and socket.io connection
        return () => socketClient.disconnect()
    }, [])

    return (
        <>
            <RouterProvider router={router}/>
        </>

    )
}

export default App
