import ContactList from './ContactList.tsx';
import ActiveChat from './ActiveChat.tsx';

export default function Chat() {
    return (
        <div
            className="flex flex-row h-screen w-screen">  {/*h-screen w-screen to take the full viewport space*/}
            <ContactList/>
            <ActiveChat/>
        </div>

    )
}
