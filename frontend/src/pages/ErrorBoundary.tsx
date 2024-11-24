import React, {ReactNode} from 'react';
interface ErrorBoundaryProps {
    children: ReactNode
}

interface ErrorBoundaryState {
    hasError: boolean
}

export default class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = {hasError: false}
    }

    static getDerivedStateFromError(): ErrorBoundaryState {
        return {hasError: true}
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
        console.error("ErrorBoundary caught an error", error, errorInfo)
    }

    render() {
        if (this.state.hasError) {
            return (
                <div>
                    <h1>Error </h1>
                    <p>Enable cookies to use this app</p>
                </div>
            )
        }
        return this.props.children
    }
}
