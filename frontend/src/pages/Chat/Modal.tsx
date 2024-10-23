import {useEffect, ReactNode} from 'react';

type ModalProps = {
    isOpen: boolean;
    onClose: () => void;
    children: ReactNode;
}


export default function Modal({isOpen, onClose, children}: ModalProps) {

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                onClose()
            }
        }
        if (isOpen) {
            window.addEventListener('keydown', handleKeyDown)
        }
        return () => {
            window.removeEventListener('keydown', handleKeyDown)
        }
    }, [isOpen, onClose])

    if (!isOpen) {
        return null
    }
    return (
        <div className="my-modal">
            <div className="modal-box bg-gray-300 dark:bg-gray-700 rounded">
                <button onClick={onClose}
                        className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕
                </button>
                {children}
            </div>
        </div>
    )
}
