import {useForm, SubmitHandler} from "react-hook-form"
import {Input, Label, Field, Description, Fieldset} from '@headlessui/react'
import auth from '../../services/auth.ts';
import {useState} from 'react';
import EyeIcon from '../../components/icons/EyeIcon.tsx';

export type SignupInputs = {
    firstName: string
    lastName: string
    email: string
    password: string
}

type SignupFormProps = {
    setSignup: (value: boolean) => void;
}

export default function SignupForm({setSignup}: SignupFormProps) {
    const [showPassword, setShowPassword] = useState<boolean>(false)

    const {
        register,
        handleSubmit,
        reset,
        // watch,
        formState: {errors},
    } = useForm<SignupInputs>()

    const onSubmit: SubmitHandler<SignupInputs> = async (data) => {
        const res = await auth.signup(data)
        if (res && res.status === 201) {
            console.log("User register success")
            console.dir(res)
            reset()
            setSignup(true)
        } else {
            const errorDetail = res ? await res.json() : {detail: "Unknown error"}
            console.error("Failed to signup user, error detail: " + errorDetail)
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
                            <Input type="text" {...register("firstName", {required: 'First name is required'})}
                                   className="input-base"/>
                            <Description className="description-error">
                                {errors.firstName && <span>{errors.firstName.message}</span>}
                            </Description>
                        </Field>

                        <Field className="flex flex-col">
                            <Label className="text-sm">Last name</Label>
                            <Input type="text" {...register("lastName")}
                                   className="input-base"/>
                        </Field>
                    </div>
                    <Field className="flex flex-col">
                        <Label className="text-sm">Email</Label>
                        <Input type="text" {...register('email', {
                            required: 'Email is required',
                            pattern: {
                                value: /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/,
                                message: 'Please enter a valid email address',
                            },
                        })}
                               className="input-base"/>
                        <Description className="description-error">
                            {errors.email && <span>{errors.email.message}</span>}
                        </Description>
                    </Field>

                    <Field className="flex flex-col">
                        <Label className="text-sm">Password</Label>
                        <div className="relative">
                            <Input type={showPassword ? "text" : "password"}
                                   {...register("password", {required: 'Password is required'})}
                                   className="input-base w-full"
                            />
                            <div
                                className="flex flex-col justify-center mr-2 p-1 absolute top-0 right-0"
                                onMouseDown={() => setShowPassword(true)}
                                onMouseUp={() => setShowPassword(false)}
                                onMouseLeave={() => setShowPassword(false)}
                            >
                                <EyeIcon/>
                            </div>
                        </div>
                        <Description className="description-error">
                            {errors.password && <span>{errors.password && errors.password.message}</span>}
                        </Description>
                    </Field>
                    <input type="submit" value="Sign up" className="btn btn-primary btn-sm"/>
                </Fieldset>
            </form>
        </>

    )
}
