import Avatar from '../../components/Avatar.tsx';

export default function ChatItem(){
    return (
        <div className="flex flex-row w-full my-2">
            <Avatar className="w-12"/>
            <div className="flex flex-col justify-between ml-3 gap-1 w-full">
                <div className="flex flex-row justify-between">
                    <p className="text-md text-black dark:text-white">FirstName LastName</p>
                    <p className="text-sm">Oct/10/2024</p>
                </div>
                <p className="text-xs">last message goes here...</p>
            </div>
        </div>
    )
}
