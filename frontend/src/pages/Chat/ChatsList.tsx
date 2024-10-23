import NewIcon from '../../components/icons/NewIcon.tsx';
import ChatItem from './ChatItem.tsx';

export default function ChatsList() {

    return (
        <div className="flex flex-col min-w-[340px] bg-gray-100 dark:bg-gray-800 dark:text-gray-300 p-4 h-full">
            <div className="flex flex-row py-2">
                <h1 className="text-lg">Chats</h1>
                <NewIcon className="ml-auto"/>
            </div>
            <div className="flex flex-col">
                <ChatItem/>
                <ChatItem/>
                <ChatItem/>
                <ChatItem/>

            </div>
        </div>
    )
}
