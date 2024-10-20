import {SignupInputs} from '../pages/Signup/SignupForm.tsx';
import {LoginInputs} from '../pages/Login/LoginForm.tsx';

const baseUrl = 'http://localhost:8000'

const signup = async (formData: SignupInputs) => {
    try {
        return await fetch(baseUrl + '/api/signup', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(formData),
        })
    } catch (e) {
        console.error("An error occurred: " + e)
    }
}

const login = async (formData: LoginInputs) => {
    try {
        const form  = new FormData()
        form.append("username", formData.email)
        form.append("password", formData.password)
        return await fetch(baseUrl + '/api/login', {
            method: "POST",
            body: form,  // send as FormData
        })
    } catch (e) {
        console.log("An error occured: " + e)
    }
}


export default {signup, login}
