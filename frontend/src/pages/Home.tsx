import LoginForm from './Login/LoginForm.tsx';
import {useAppSelector} from '../hooks.ts';
import Chat from './Chat';

export default function Home() {
    const userStatus = useAppSelector(state => state.user.status)

    return (
        <>
            {userStatus === 'succeeded'
                ? <Chat/>
                : <LoginForm/>
            }
        </>
    )
}
