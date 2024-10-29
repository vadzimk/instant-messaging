import {useAppDispatch, useAppSelector} from '../../hooks.ts';
import {useEffect, useRef} from 'react';
import {getMessages, selectChatByContactId} from '../../reducers/chatSlice.ts';
import clsx from 'clsx';


export function ChatHistory() {
    const {currentContactId} = useAppSelector(
        state => state.contacts)
    const currentChat = useAppSelector(
        state => selectChatByContactId(state, currentContactId))
    const dispatch = useAppDispatch()
    const messagesEndRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (currentContactId && !currentChat?.messages) {
            dispatch(getMessages(currentContactId))
        }
    }, [currentContactId, dispatch, currentChat])

    useEffect(()=>{
        // scroll to the bottom of the chat when new messages are added
        if (messagesEndRef.current){
            messagesEndRef.current.scrollIntoView({behavior: 'smooth'})
        }
    })

    return (
        <div className="h-full flex-1 flex-col justify-end overflow-y-auto"> {/* overflow appears with flex-1 */}
            {
                currentChat?.messages.map(
                    m => (
                        <div key={m.id}
                             className={clsx('chat', m.user_from_id===currentContactId ? "chat-start": "chat-end")}
                        >
                            <div className={clsx("chat-bubble", m.user_from_id===currentContactId ? "chat-bubble-primary" : "chat-bubble-accent")}>
                                {m.content}
                            </div>
                        </div>
                    )
                )
            }
            <div ref={messagesEndRef}/>
        </div>
    )
}
