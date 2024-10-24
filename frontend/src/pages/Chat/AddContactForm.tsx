import {SubmitHandler, useForm} from 'react-hook-form';
import {useAppDispatch} from '../../hooks.ts';
import EmailInput from '../../components/EmailField/EmailInput.tsx';
import {Description, Field} from '@headlessui/react';
import {addContact, NewContactFields} from '../../reducers/chatSlice.ts';

export default function AddContactForm() {
    const dispatch = useAppDispatch()

    const {
        register,
        handleSubmit,
        reset,
        formState: {errors}
    } = useForm<NewContactFields>()

    const onSubmit: SubmitHandler<NewContactFields> = async (data: NewContactFields) => {
        try {
            await dispatch(addContact(data)).unwrap()
            reset() // on success
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
