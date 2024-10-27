import Avatar from '../../components/Avatar.tsx';
import {GetContactSchema} from '../../reducers/contactsSlice.ts';
import {useAppSelector} from '../../hooks.ts';

type ContactItemProps = {
    contact: GetContactSchema;
    className?: string;
    onClick: () => void;
}

export default function ContactItem({contact, className, onClick}: ContactItemProps) {
    const chatList = useAppSelector(state => state.chat.chatList)
    return (
        <div onClick={onClick}
             className={`flex flex-row w-full my-2 p-2 rounded btn-ghost ${className}`}>
            <Avatar className="w-12"/>
            <div className="flex flex-col justify-between ml-3 gap-1 w-full">
                <div className="flex flex-row justify-between">
                    <p className="text-md text-black dark:text-white">
                        {contact.first_name} {contact.last_name}
                    </p>
                    <p className="text-sm">Oct/10/2024</p>
                </div>
                {
                    chatList.map(c => (
                        c.messages.length > 0
                            ? <p className="text-xs">{
                                c.messages.find(m => m.user_from_id == contact.id)?.content
                            }</p>
                            : <p className="text-xs">Just added</p>
                    ))
                }
            </div>
        </div>
    )
}


