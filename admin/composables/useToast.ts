interface ToastOptions {
    title: string
    message?: string
    type?: 'success' | 'error' | 'warning' | 'info'
    duration?: number
}

const toastState = reactive({
    visible: false,
    title: '',
    message: '',
    type: 'info' as 'success' | 'error' | 'warning' | 'info',
    duration: 4000
})

export const useToast = () => {
    const show = (options: ToastOptions) => {
        toastState.title = options.title
        toastState.message = options.message || ''
        toastState.type = options.type || 'info'
        toastState.duration = options.duration ?? 4000
        toastState.visible = true
    }

    const success = (title: string, message?: string) => {
        show({ title, message, type: 'success' })
    }

    const error = (title: string, message?: string) => {
        show({ title, message, type: 'error' })
    }

    const warning = (title: string, message?: string) => {
        show({ title, message, type: 'warning' })
    }

    const info = (title: string, message?: string) => {
        show({ title, message, type: 'info' })
    }

    const hide = () => {
        toastState.visible = false
    }

    return {
        state: toastState,
        show,
        success,
        error,
        warning,
        info,
        hide
    }
}
