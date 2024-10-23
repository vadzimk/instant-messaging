import {SubmitHandler, useForm} from 'react-hook-form';
import {LoginInputs} from '../Login/LoginForm.tsx';
import {loginUser} from '../../reducers/userSlice.ts';
import {useAppDispatch} from '../../hooks.ts';
import EmailInput from '../../components/EmailField/EmailInput.tsx';
import {Description, Field} from '@headlessui/react';

export default function NewChatForm() {
    const dispatch = useAppDispatch()

    const {
        register,
        handleSubmit,
        reset,
        formState: {errors}
    } = useForm<LoginInputs>()

    const onSubmit: SubmitHandler<LoginInputs> = async (data: LoginInputs) => {
        try {
            await dispatch(loginUser(data)).unwrap()
            reset()
        } catch {
            /* empty */
        }
    }

    return (
        <div className="flex flex-col gap-4">
            <h3 className="font-bold text-lg">New Chat</h3>
            <form onSubmit={handleSubmit(onSubmit)}>
                <Field className="flex flex-col">
                    <EmailInput register={register} placeholder="Email"/>
                    <Description className="description-error">
                        {errors.email?.message && <span>{String(errors.email.message)}</span>}
                    </Description>
                    <input type="submit" value='Add' className="btn btn-primary btn-sm mt-4"/>
                </Field>
            </form>
        </div>
    )
}
