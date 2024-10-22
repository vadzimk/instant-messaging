import {createBrowserRouter, RouterProvider} from 'react-router-dom';
import ErrorPage from './pages/ErrorPage.tsx';
import Layout from './Layout.tsx';
import Home from './pages/Home.tsx';
import Index from './pages/Signup';

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

    return (
        <>
            <RouterProvider router={router}/>
        </>

    )
}

export default App
