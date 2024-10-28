import {useAppSelector} from '../../hooks.ts';


export function ChatHistory() {
    const {chatList} = useAppSelector(state => state.chat)
    const {currentContactId} = useAppSelector(state => state.contacts)

    return (
        <div className="h-full flex flex-col justify-end">
            {
                chatList
                    .filter(ch => ch.contactId === currentContactId)
                    ?.map(chi =>
                        chi.messages.map(m => (
                            <div key={m.id}>{m.content}</div>
                        )))
            }
        </div>
    )
}
