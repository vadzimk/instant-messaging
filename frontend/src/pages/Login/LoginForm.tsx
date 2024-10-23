import {Fieldset} from '@headlessui/react';
import PasswordField from '../../components/PasswordField.tsx';
import {useForm, SubmitHandler} from "react-hook-form"
import {Link} from 'react-router-dom';
import {useAppDispatch} from '../../hooks.ts';
import {loginUser} from '../../reducers/userSlice.ts';
import EmailField from '../../components/EmailField';

export type LoginInputs = {
    email: string;
    password: string;
}
export default function LoginForm() {
    const dispatch = useAppDispatch()


    const {
        register,
        handleSubmit,
        reset,
        formState: {errors}
    } = useForm<LoginInputs>()

    const onSubmit: SubmitHandler<LoginInputs> = async (data: LoginInputs) => {
        try{
            await dispatch(loginUser(data)).unwrap()
            reset()
        } catch {
            /* empty */
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
