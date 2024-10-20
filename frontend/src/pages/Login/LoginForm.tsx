import {Fieldset} from '@headlessui/react';
import EmailField from '../../components/EmailField.tsx';
import PasswordField from '../../components/PasswordField.tsx';
import {useForm, SubmitHandler} from "react-hook-form"
import {Link} from 'react-router-dom';
import auth from '../../services/auth.ts';

export type LoginInputs = {
    email: string;
    password: string;
}
export default function LoginForm() {
    const {
        register,
        handleSubmit,
        reset,
        formState: {errors}
    } = useForm<LoginInputs>()

    const onSubmit: SubmitHandler<LoginInputs> = async (data: LoginInputs) => {
        const res = await auth.login(data)
        if (!res){
            console.error("Login failed, no response returned")
            return // TODO show error message
        }
        const body = await res.json()
        if (res.status === 200) {
            reset()
            // save token
            localStorage.setItem('access_token', body.access_token)
        } else {
            console.error("Failed to login user, error detail: " + body?.detail || "Unknown error")
        }
    }
    return (
        <>
            <h1 className="text-4xl mb-6">Log in</h1>
            <form onSubmit={handleSubmit(onSubmit)}>
                <Fieldset className="w-full flex flex-col gap-4 min-w-96">
                    <EmailField register={register} errors={errors}/>
                    <PasswordField register={register} errors={errors}/>
                    <input type="submit" value='Log in' className="btn btn-primary btn-sm"/>
                </Fieldset>
            </form>
            <div className="mt-6">
                <p className="text-center text-sm">New to Messaging? &nbsp;
                    <Link to="/signup"
                          className="underline text-blue-600 dark:text-blue-500">
                        Sign up
                    </Link>
                </p>
            </div>
        </>

    )
}
