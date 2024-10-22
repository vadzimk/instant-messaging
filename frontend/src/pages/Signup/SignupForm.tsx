import {useForm, SubmitHandler} from "react-hook-form"
import {Input, Label, Field, Description, Fieldset} from '@headlessui/react'
// import auth from '../../services/auth.ts';
import {Link} from 'react-router-dom';
import EmailField from '../../components/EmailField.tsx';
import PasswordField from '../../components/PasswordField.tsx';
import {signupUser} from '../../reducers/userSlice.ts';
import {useAppDispatch} from '../../hooks.ts';

export type SignupInputs = {
    first_name: string
    last_name: string
    email: string
    password: string
}

type SignupFormProps = {
    setSignup: (value: boolean) => void;
}

export default function SignupForm({setSignup}: SignupFormProps) {
    const dispatch = useAppDispatch()  // ts setup requires typed dispatch


    const {
        register,
        handleSubmit,
        reset,
        // watch,
        formState: {errors},
    } = useForm<SignupInputs>()

    const onSubmit: SubmitHandler<SignupInputs> = async (data) => {
        try {
            // https://redux.js.org/tutorials/essentials/part-5-async-logic#checking-thunk-results-in-components
            await dispatch(signupUser(data)).unwrap()
            reset()
            setSignup(true)
        } catch {
            /* empty */
        }
    }

    return (
        <>
            <h1 className="text-4xl mb-6">Sign up</h1>
            <form onSubmit={handleSubmit(onSubmit)}>
                <Fieldset className="w-full flex flex-col gap-4">
                    <div className="flex flex-row justify-between gap-4">
                        <Field className="flex flex-col">
                            <Label className="text-sm">First name</Label>
                            <Input type="text" {...register("first_name", {required: 'First name is required'})}
                                   className="input-base"/>
                            <Description className="description-error">
                                {errors.first_name && <span>{errors.first_name.message}</span>}
                            </Description>
                        </Field>
                        <Field className="flex flex-col">
                            <Label className="text-sm">Last name</Label>
                            <Input type="text" {...register("last_name")}
                                   className="input-base"/>
                        </Field>
                    </div>
                    <EmailField register={register} errors={errors}/>
                    <PasswordField register={register} errors={errors}/>
                    <input type="submit" value="Sign up" className="btn btn-primary btn-sm"/>
                </Fieldset>
            </form>
            <div className="mt-6">
                <p className="text-center text-sm">Already on Messaging? &nbsp;
                    <Link to="/"
                          className="underline text-blue-600 dark:text-blue-500">
                        Log in
                    </Link>
                </p>
            </div>
        </>

    )
}
