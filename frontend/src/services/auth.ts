import {SignupInputs} from '../pages/Signup/SignupForm.tsx';

const baseUrl = 'http://localhost:8000'

const signup = async (formData: SignupInputs ) => {
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

export default {signup}
