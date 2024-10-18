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
        // watch,
        formState: {errors},
    } = useForm<Inputs>()

    const onSubmit: SubmitHandler<Inputs> = (data) => console.log(data)

    // console.log(watch("example")) // watch input value by passing the name of it

    return (

        <form onSubmit={handleSubmit(onSubmit)} className="w-full">
            <Field className="flex flex-col">
                <Label>First name</Label>
                <Input type="text" {...register("firstName", {required: true})}
                       className="border data-[hover]:shadow data-[focus]:bg-blue-100" />
                <Description>{errors.firstName && <span>This field is required</span>}</Description>
            </Field>


            <Field className="flex flex-col">
                <Label>Last name</Label>
                <Input type="text" {...register("lastName")}
                       className="border data-[hover]:shadow data-[focus]:bg-blue-100" />
            </Field>

            <Field className="flex flex-col">
                <Label>Email</Label>
                <Input type="text" {...register("email", {required: true})}
                       className="border data-[hover]:shadow data-[focus]:bg-blue-100" />
                <Description>{errors.email && <span>This field is required</span>}</Description>
            </Field>

            <Field className="flex flex-col">
                <Label>Password</Label>
                <Input type="text" {...register("password", {required: true})}
                       className="border data-[hover]:shadow data-[focus]:bg-blue-100" />
                <Description>{errors.password && <span>This field is required</span>}</Description>
            </Field>

            <input type="submit" className="btn btn-primary btn-sm"/>
        </form>
    )
}
