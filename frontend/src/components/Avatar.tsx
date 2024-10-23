export default function Avatar({className}: {className?: string}){
    return (
        <div className="avatar">
            <div className={`w-12 rounded-full ${className}`}>
                <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp"/>
            </div>
        </div>
    )
}
