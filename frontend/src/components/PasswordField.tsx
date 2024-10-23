import {Description, Field, Input, Label} from '@headlessui/react';
import EyeIcon from './icons/EyeIcon.tsx';
import {useState} from 'react';
import {FieldErrors, FieldValues, Path, UseFormRegister} from 'react-hook-form';

type PasswordFieldProps<T extends FieldValues> = {
    register: UseFormRegister<T>;
    errors: FieldErrors<T>;
}
export default function PasswordField<T extends FieldValues>({register, errors}: PasswordFieldProps<T>) {
    const [showPassword, setShowPassword] = useState<boolean>(false)

    return (
        <Field className="flex flex-col">
            <Label className="text-sm">Password</Label>
            <div className="relative">
                <Input data-focus
                       data-hover
                       type={showPassword ? "text" : "password"}
                       {...register("password" as Path<T>, {required: 'Password is required'})}
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
                {errors.password?.message && <span>{String(errors.password && errors.password.message)}</span>}
            </Description>
        </Field>
    )
}
