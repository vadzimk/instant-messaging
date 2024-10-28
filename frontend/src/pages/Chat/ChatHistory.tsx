import {useAppDispatch, useAppSelector} from '../../hooks.ts';
import {useEffect} from 'react';
import {getMessages, selectChatByContactId} from '../../reducers/chatSlice.ts';


export function ChatHistory() {
    const {currentContactId} = useAppSelector(
        state => state.contacts)
    const currentChat = useAppSelector(
        state => selectChatByContactId(state, currentContactId))
    const dispatch = useAppDispatch()

    useEffect(() => {
        if(currentContactId && ! currentChat?.messages){
            dispatch(getMessages(currentContactId))
        }
    }, [currentContactId, dispatch, currentChat])

    return (
        <div className="h-full flex flex-col justify-end">
            {
                currentChat?.messages.map(
                    m => (
                        <div key={m.id}>{m.content}</div>
                    )
                )
            }
        </div>
    )
}
