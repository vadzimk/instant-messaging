import NewIcon from '../../components/icons/NewIcon.tsx';
import ContactItem from './ContactItem.tsx';
import {useState} from 'react';
import Modal from './Modal.tsx';
import AddContactForm from './AddContactForm.tsx';
import {useAppDispatch, useAppSelector} from '../../hooks.ts';
import {setCurrentContact} from '../../reducers/contactsSlice.ts';

export default function ContactList() {
    const dispatch = useAppDispatch()
    const {contactList, currentContactId} = useAppSelector(state => state.contacts)
    const [isModalOpen, setModalOpen] = useState<boolean>(false)
    const handleModalClose = () => {
        setModalOpen(false)
        console.log('close modal clicked')
    }
    const handleContactClick = (contactId: string) => {
        dispatch(setCurrentContact(contactId))
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
                    contactList.map(c => (
                        <ContactItem
                            key={c.id}
                            contact={c}
                            className={currentContactId === c.id ? "bg-custom-fallback-bc bg-opacity-30 dark:bg-opacity-15" : ""}
                            onClick={() => handleContactClick(c.id)}
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
