export default function NewIcon({className}: {className?: string}){
    return (
        <svg width="1em" height="1em" viewBox="0 0 32 32" fill="none" className={`fill-current w-[32px] h-[32px] ${className}`}>
            <defs>
                <path id="carbonNewTab0" fill="currentColor"
                      d="M26 26H6V6h10V4H6a2 2 0 0 0-2 2v20a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2V16h-2Z"/>
            </defs>
            <use href="#carbonNewTab0"/>
            <use href="#carbonNewTab0"/>
            <path fill="currentColor" d="M26 6V2h-2v4h-4v2h4v4h2V8h4V6z"/>
        </svg>
    )
}
