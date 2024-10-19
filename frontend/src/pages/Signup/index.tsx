import SignupForm from './SignupForm.tsx';
import {useState} from 'react';
import SignupSuccess from './SignupSuccess.tsx';

export default function Signup() {
    const [isSignup, setSignup] = useState<boolean>(false)

    return (
        <>
            {isSignup
                ? <SignupSuccess/>
                : <SignupForm setSignup={setSignup}/>
            }
        </>
    )
}
