import {Description, Field, Label} from '@headlessui/react';
import {FieldErrors, FieldValues, UseFormRegister} from 'react-hook-form';
import EmailInput from './EmailInput.tsx';

type EmailFieldProps<T extends FieldValues> = {
    register: UseFormRegister<T>;
    errors: FieldErrors<T>;
}
export default function EmailField<T extends FieldValues>({register, errors}: EmailFieldProps<T>) {
    return (
        <Field className="flex flex-col">
            <Label className="text-sm">Email</Label>
            <EmailInput register={register}/>
            <Description className="description-error">
                {errors.email?.message && <span>{String(errors.email.message)}</span>}
            </Description>
        </Field>
    )
}
