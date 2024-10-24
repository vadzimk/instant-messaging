import Avatar from '../../components/Avatar.tsx';
import {Chat} from '../../reducers/chatSlice.ts';

type ChatItemProps = {
    chat: Chat;
    className?: string;
    onClick: () => void;
}

export default function ChatItem({chat, className, onClick}: ChatItemProps) {

    return (
        <div onClick={onClick}
            className={`flex flex-row w-full my-2 p-2 rounded btn-ghost ${className}`}>
            <Avatar className="w-12"/>
            <div className="flex flex-col justify-between ml-3 gap-1 w-full">
                <div className="flex flex-row justify-between">
                    <p className="text-md text-black dark:text-white">
                        {chat.contact.first_name} {chat.contact.last_name}
                    </p>
                    <p className="text-sm">Oct/10/2024</p>
                </div>
                {
                    chat.messages.length > 0
                        ? <p className="text-xs">{chat.messages[chat.messages.length - 1]}</p>
                        : <p className="text-xs">Just added</p>
                }
            </div>
        </div>
    )
}
