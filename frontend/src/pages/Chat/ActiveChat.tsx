import Avatar from '../../components/Avatar.tsx';
import KebabHorizontalIcon from '../../components/icons/KebabHorizontalIcon.tsx';
import PaperAirplaneIcon from '../../components/icons/PaperAirplaneIcon.tsx';
import {Textarea} from '@headlessui/react';
import {useRef, useState} from 'react';
import {useAppDispatch, useAppSelector} from '../../hooks.ts';
import {sendMessage} from '../../reducers/chatSlice.ts';
import {ChatHistory} from './ChatHistory.tsx';

export default function ActiveChat() {
    const {contactList, currentContactId} = useAppSelector(state => state.contacts)
    const currentContact = currentContactId !== null ? contactList.find(c => c.id === currentContactId) : null
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [message, setMessage] = useState('');
    const dispatch = useAppDispatch()

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setMessage(e.target.value);

        // Dynamically adjust height based on scrollHeight
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'; // Reset height
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`; // Set height based on content
        }
    };

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault()
        if (message.trim() && currentContactId) {
            try {
                await dispatch(sendMessage({contact_id: currentContactId, content: message})).unwrap()
                setMessage('')
            } catch {
                /* empty */
            }

        }
    }
    return (
        <div className="flex flex-col w-full p-4">
            {/*Active chat header*/}
            <div className="flex flex-row justify-between ">
                <div className="flex flex-row">
                    <Avatar className="w-8"/>
                    {
                        currentContact &&
                        (
                            <div className="ml-3">
                                <p className="text-md text-black dark:text-white">{currentContact.first_name} {currentContact.last_name}</p>
                                <p className="text-xs">Last seen 45 minutes ago</p>
                            </div>
                        )
                    }
                </div>
                <div className="flex flex-col justify-center">
                    <KebabHorizontalIcon className="mr-3"/>
                </div>
            </div>
            <ChatHistory/>
            <form onSubmit={handleSendMessage}
                  className="relative">
                <Textarea
                    ref={textareaRef}
                    name="message"
                    data-focus
                    data-hover
                    rows={1}
                    value={message}
                    onChange={handleInputChange}
                    placeholder="start typing"
                    className="input-base w-full resize-none overflow-hidden focus:outline-none min-h-12 p-2"
                />
                <button type="submit"
                        className="flex flex-col justify-center px-4 absolute top-0 right-0 h-full">
                    <PaperAirplaneIcon/>
                </button>
            </form>
        </div>
    );
}
