import {Input} from '@headlessui/react';
import {FieldValues, Path, UseFormRegister,} from 'react-hook-form';

type EmailInputProps<T extends FieldValues> = {
    register: UseFormRegister<T>;
} & React.InputHTMLAttributes<HTMLInputElement>

export default function EmailInput<T extends FieldValues>({register, ...inputProps}: EmailInputProps<T>) {
    return (
        <>
            <Input data-focus
                   data-hover
                   type="text" {...register('email' as Path<T>, {
                required: 'Email is required',
                pattern: {
                    value: /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/,
                    message: 'Please enter a valid email address',
                },
            })}
                   className="input-base"
                   {...inputProps}
            />

        </>
    )
}
