import {Description, Field, Input, Label} from '@headlessui/react';
import {FieldErrors, FieldValues, Path, UseFormRegister} from 'react-hook-form';

type EmailFieldProps<T extends FieldValues> = {
    register: UseFormRegister<T>;
    errors: FieldErrors<T>;
}
export default function EmailField<T extends FieldValues>({register, errors}: EmailFieldProps<T>) {
    return (
        <Field className="flex flex-col">
            <Label className="text-sm">Email</Label>
            <Input data-focus
                   data-hover
                   type="text" {...register('email' as Path<T>, {
                required: 'Email is required',
                pattern: {
                    value: /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/,
                    message: 'Please enter a valid email address',
                },
            })}
                   className="input-base"/>
            <Description className="description-error">
                {errors.email?.message && <span>{String(errors.email.message)}</span>}
            </Description>
        </Field>
    )
}
