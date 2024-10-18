import {useForm, SubmitHandler} from "react-hook-form"
import {Input, Label, Field, Description} from '@headlessui/react'

type Inputs = {
    firstName: string
    lastName: string
    email: string
    password: string
}

export default function Signup() {

    const {
        register,
        handleSubmit,
        reset,
        // watch,
        formState: {errors},
    } = useForm<Inputs>()

    const onSubmit: SubmitHandler<Inputs> = async (data) => {
        try{
            const baseUrl = 'http://localhost:8000'
            const res = await fetch(baseUrl + '/api/signup', {
                method: "POST",
                headers:{
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            })
            if (res.status === 201) {
                console.log("User register success")
                reset()
            } else {
                console.error("Failed to signup user, status: " + res.status)
            }
        } catch (e){
            console.error("An error occurred: " + e)
        }
    }

    return (

        <form onSubmit={handleSubmit(onSubmit)} className="w-full flex flex-col gap-4">
            <Field className="flex flex-col">
                <Label className="text-sm">First name</Label>
                <Input type="text" {...register("firstName", {required: true})}
                       className="border data-[hover]:shadow data-[focus]:bg-blue-100" />
                <Description className="text-xs text-orange-500">{errors.firstName && <span>First name is required</span>}</Description>
            </Field>


            <Field className="flex flex-col">
                <Label className="text-sm">Last name</Label>
                <Input type="text" {...register("lastName")}
                       className="border data-[hover]:shadow data-[focus]:bg-blue-100" />
            </Field>

            <Field className="flex flex-col">
                <Label className="text-sm">Email</Label>
                <Input type="text" {...register("email", {required: true})}
                       className="border data-[hover]:shadow data-[focus]:bg-blue-100" />
                <Description className="text-xs text-orange-500">{errors.email && <span>Email is required</span>}</Description>
            </Field>

            <Field className="flex flex-col">
                <Label className="text-sm">Password</Label>
                <Input type="text" {...register("password", {required: true})}
                       className="border data-[hover]:shadow data-[focus]:bg-blue-100" />
                <Description className="text-xs text-orange-500">{errors.password && <span>Password is required</span>}</Description>
            </Field>

            <input type="submit" value="Sign up" className="btn btn-primary btn-sm"/>
        </form>
    )
}
