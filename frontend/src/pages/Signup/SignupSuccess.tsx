import CheckboxCompleteIcon from '../../components/icons/CheckboxCompleteIcon.tsx';
import {Link} from 'react-router-dom';


export default function SignupSuccess(){
    return (
        <div className="flex flex-col justify-between gap-6">
            <div className="flex flex-row justify-center">
                <CheckboxCompleteIcon className="text-current"/>
            </div>
            <div className="font-bold">Your account has been created</div>
            <Link to="/" className="btn btn-primary btn-sm">Return to homepage</Link>
        </div>
    )
}
