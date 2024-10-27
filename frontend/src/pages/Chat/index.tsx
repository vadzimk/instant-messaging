import ContactList from './ContactList.tsx';
import ActiveChat from './ActiveChat.tsx';

export default function Chat(){
    return(
        <div className="flex flex-row  min-h-[calc(100vh)] min-w-[calc(100vw)]">
            <ContactList/>
            <ActiveChat/>
        </div>

    )
}
