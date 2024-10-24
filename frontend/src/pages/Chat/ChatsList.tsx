import NewIcon from '../../components/icons/NewIcon.tsx';
import ChatItem from './ChatItem.tsx';
import {useState} from 'react';
import Modal from './Modal.tsx';
import AddContactForm from './AddContactForm.tsx';

export default function ChatsList() {
    const [isModalOpen, setModalOpen] = useState<boolean>(false)
    const handleModalClose = ()=>{
        setModalOpen(false)
        console.log('close modal clicked')
    }
    return (
        <div className="flex flex-col min-w-[340px] bg-gray-100 dark:bg-gray-800 dark:text-gray-300 p-4 h-full relative">
            <div className="flex flex-row py-2">
                <h1 className="text-lg">Chats</h1>
                <button className="ml-auto"
                    onClick={() => setModalOpen(true)}>
                    <NewIcon className="btn btn-sm btn-circle btn-ghost" />
                </button>
            </div>
            <div className="flex flex-col">
                <ChatItem/>
                <ChatItem/>
                <ChatItem/>
                <ChatItem/>
            </div>
            <Modal onClose={handleModalClose} isOpen={isModalOpen}>
                <AddContactForm/>
            </Modal>
        </div>
    )
}
