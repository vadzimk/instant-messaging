import NewIcon from '../../components/icons/NewIcon.tsx';
import ChatItem from './ChatItem.tsx';
import {useState} from 'react';
import Modal from './Modal.tsx';
import AddContactForm from './AddContactForm.tsx';
import {useAppDispatch, useAppSelector} from '../../hooks.ts';
import {setCurrentChat} from '../../reducers/chatSlice.ts';

export default function ChatsList() {
    const dispatch = useAppDispatch()
    const {chatList, currentChatId} = useAppSelector(state => state.chat)
    const [isModalOpen, setModalOpen] = useState<boolean>(false)
    const handleModalClose = () => {
        setModalOpen(false)
        console.log('close modal clicked')
    }
    const handleChatClick = (chatId: number) => {
        dispatch(setCurrentChat(chatId))
    }
    return (
        <div
            className="flex flex-col min-w-[340px] bg-gray-100 dark:bg-gray-800 dark:text-gray-300 p-2 h-full relative">
            <div className="flex flex-row py-2">
                <h1 className="text-lg">Chats</h1>
                <button className="ml-auto"
                        onClick={() => setModalOpen(true)}>
                    <NewIcon className="btn btn-sm btn-circle btn-ghost"/>
                </button>
            </div>
            <div className="flex flex-col">
                {
                    chatList.map(ch => (
                        <ChatItem
                            key={ch.id}
                            chat={ch}
                            className={currentChatId === ch.id ? "bg-custom-fallback-bc bg-opacity-30 dark:bg-opacity-15" : ""}
                            onClick={() => handleChatClick(ch.id)}
                        />
                    )).reverse()
                }
            </div>
            <Modal onClose={handleModalClose} isOpen={isModalOpen}>
                <AddContactForm/>
            </Modal>
        </div>
    )
}
