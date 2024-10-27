import {io, Socket} from 'socket.io-client';
import {baseUrl} from './api.ts';
// // example of using buffer for binary data
// const buffer = new ArrayBuffer(8); // Create an ArrayBuffer of size 8 bytes
// const view = new Uint8Array(buffer); // Create a view for the ArrayBuffer
// view[0] = 42; // Fill the buffer with some data

interface ServerToClientEvents {
    noArg: () => void;
    basicEmit: (a: number, b: string, c: ArrayBuffer) => void;
    withAck: (d: string, callback: (e: number) => void) => void;
}

interface ClientToServerEvents {
    hello: () => void;
}


// using singleton pattern
export class SocketClient {
    private static instance: SocketClient
    private access_token: string
    private socket: Socket<ServerToClientEvents, ClientToServerEvents> | null = null

    public constructor(access_token: string | null) {
        if (!access_token) {
            throw Error('Access token is required to initialize SocketClient')
        }
        this.access_token = access_token
        this.socket = io(baseUrl, {
            auth: {token: this.access_token}
        })
        this.setupListeners()
        SocketClient.instance = this
    }

    public static getInstance(): SocketClient {
        if (!SocketClient.instance) {
            throw Error('SocketClient not initialized. Call `new SocketClient(access_token)` to create instance')
        }
        return SocketClient.instance
    }

    private setupListeners() {
        this.socket?.on('connect', () => {
            console.log('socket connected')
        })
        this.socket?.on('disconnect', () => {
            console.log('socket disconnected')
        })
        this.socket?.on('connect_error', ()=>{
            console.error('Could not connect to socket.io server')
        })
        // other listeners
    }


    public emit(
        event,
        ...args
    ) {
        this.socket?.emit(event, ...args)
    }

    public emitWithAck(
        event,
        ...args
    ) {
        return this.socket?.emitWithAck(event, ...args)
    }

    public on(
        event,
        callback,
    ) {
        this.socket?.on(event, callback)
    }


    public disconnect() {
        this.socket?.disconnect()
    }
}
