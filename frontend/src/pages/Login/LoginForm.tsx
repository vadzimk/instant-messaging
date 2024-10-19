import {Fieldset} from '@headlessui/react';
import EmailField from '../../components/EmailField.tsx';
import PasswordField from '../../components/PasswordField.tsx';
import {useForm, SubmitHandler} from "react-hook-form"

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

    const onSubmit: SubmitHandler<LoginInputs> = async (data: LoginInputs)=>{
        console.log(data)
        reset()
    }
    return (
        <>
            <h1 className="text-4xl mb-6">Log in</h1>
            <form onSubmit={handleSubmit(onSubmit)}>
                <Fieldset>
                    <EmailField register={register} errors={errors}/>
                    <PasswordField register={register} errors={errors}/>
                    <input type="submit" value='Log in' className="btn btn-primary btn-sm"/>
                </Fieldset>
            </form>
        </>

    )
}
