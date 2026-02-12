export const useApi = () => {
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase

    const authToken = useCookie('auth_token')
    const currentUser = useState<any>('current_user', () => null)

    const headers = computed(() => {
        const h: Record<string, string> = {
            'Content-Type': 'application/json'
        }
        if (authToken.value) {
            h['Authorization'] = `Bearer ${authToken.value}`
        }
        return h
    })

    // Auth
    const login = async (phone: string, password: string) => {
        const response = await $fetch<any>(`${apiBase}/auth/login`, {
            method: 'POST',
            body: { phone, password },
            headers: {
                'Content-Type': 'application/json'
            }
        }).catch(err => {
            if (err.status === 422) {
                console.warn('Login 422 Payload:', { phone, password })
            }
            throw err
        })

        if (response && response.access_token) {
            authToken.value = response.access_token
        }

        return response
    }

    const register = async (data: any) => {
        return await $fetch(`${apiBase}/auth/register`, {
            method: 'POST',
            body: data,
            headers: headers.value
        })
    }

    const logout = () => {
        authToken.value = null
        currentUser.value = null
    }

    const getCurrentUser = async () => {
        if (!authToken.value) return null
        if (currentUser.value) return currentUser.value

        try {
            const user = await $fetch(`${apiBase}/users/me`, {
                headers: headers.value
            })
            currentUser.value = user
            return user
        } catch (error) {
            authToken.value = null
            currentUser.value = null
            return null
        }
    }

    const hasRole = (role: string | string[]) => {
        if (!currentUser.value) return false
        const roles = Array.isArray(role) ? role : [role]

        const hierarchy: Record<string, number> = {
            'client': 1,
            'operator': 2,
            'manager': 3,
            'admin': 4
        }

        const userLevel = hierarchy[currentUser.value.role] || 0
        const requiredLevel = Math.min(...roles.map(r => hierarchy[r] || 99))

        return userLevel >= requiredLevel
    }

    // Admin Specific
    const getStats = async (params?: any) => {
        return await $fetch(`${apiBase}/admin/stats`, {
            params,
            headers: headers.value
        })
    }

    const getAuditLogs = async (params?: any) => {
        return await $fetch(`${apiBase}/admin/audit-logs`, {
            params,
            headers: headers.value
        })
    }

    const getSettings = async () => {
        return await $fetch(`${apiBase}/admin/settings`, {
            headers: headers.value
        })
    }

    const updateSetting = async (key: string, value: any) => {
        return await $fetch(`${apiBase}/admin/settings/${key}`, {
            method: 'PATCH',
            body: { value },
            headers: headers.value
        })
    }

    // Cars
    const getCars = async (params?: any) => {
        return await $fetch(`${apiBase}/cars`, {
            params,
            headers: headers.value
        })
    }

    const getCar = async (id: string) => {
        return await $fetch(`${apiBase}/cars/${id}`, {
            headers: headers.value
        })
    }

    const createCar = async (data: any) => {
        return await $fetch(`${apiBase}/cars`, {
            method: 'POST',
            body: data,
            headers: headers.value
        })
    }

    const updateCar = async (id: string, data: any) => {
        return await $fetch(`${apiBase}/cars/${id}`, {
            method: 'PATCH',
            body: data,
            headers: headers.value
        })
    }

    const deleteCar = async (id: string) => {
        return await $fetch(`${apiBase}/cars/${id}`, {
            method: 'DELETE',
            headers: headers.value
        })
    }

    // Applications
    const getApplications = async (params?: any) => {
        return await $fetch(`${apiBase}/applications`, {
            params,
            headers: headers.value
        })
    }

    const adminCreateApplication = async (data: any) => {
        return await $fetch(`${apiBase}/applications/admin`, {
            method: 'POST',
            body: data,
            headers: headers.value
        })
    }

    const getApplication = async (id: string) => {
        return await $fetch(`${apiBase}/applications/${id}`, {
            headers: headers.value
        })
    }

    const updateApplicationStatus = async (id: string, status: string, reason: string) => {
        return await $fetch(`${apiBase}/applications/${id}/status`, {
            method: 'PATCH',
            body: { status, reason },
            headers: headers.value
        })
    }

    const updateApplicationContactStatus = async (id: string, contactStatus: string, note?: string) => {
        return await $fetch(`${apiBase}/applications/${id}/contact-status`, {
            method: 'PATCH',
            body: { contact_status: contactStatus, note },
            headers: headers.value
        })
    }

    const updateApplicationChecklist = async (id: string, checklist: any) => {
        return await $fetch(`${apiBase}/applications/${id}/checklist`, {
            method: 'PATCH',
            body: { checklist },
            headers: headers.value
        })
    }

    const addApplicationComment = async (id: string, text: string, isInternal: boolean = true) => {
        return await $fetch(`${apiBase}/applications/${id}/comments`, {
            method: 'POST',
            body: { text, is_internal: isInternal },
            headers: headers.value
        })
    }

    const getApplicationComments = async (id: string) => {
        return await $fetch(`${apiBase}/applications/${id}/comments`, {
            headers: headers.value
        })
    }

    const assignOperator = async (appId: string, operatorId: string) => {
        return await $fetch(`${apiBase}/applications/${appId}/assign`, {
            method: 'PATCH',
            body: { operator_id: operatorId },
            headers: headers.value
        })
    }

    const assignManager = async (appId: string, managerId: string) => {
        return await $fetch(`${apiBase}/applications/${appId}/assign-manager`, {
            method: 'PATCH',
            body: { manager_id: managerId },
            headers: headers.value
        })
    }

    // Stories
    const getStories = async () => {
        return await $fetch(`${apiBase}/stories`, {
            headers: headers.value
        })
    }

    const createStory = async (data: any) => {
        return await $fetch(`${apiBase}/admin/stories`, {
            method: 'POST',
            body: data,
            headers: headers.value
        })
    }

    const updateStory = async (id: string, data: any) => {
        return await $fetch(`${apiBase}/admin/stories/${id}`, {
            method: 'PATCH',
            body: data,
            headers: headers.value
        })
    }

    const deleteStory = async (id: string) => {
        return await $fetch(`${apiBase}/admin/stories/${id}`, {
            method: 'DELETE',
            headers: headers.value
        })
    }

    const addSlide = async (storyId: string, data: any) => {
        return await $fetch(`${apiBase}/admin/stories/${storyId}/slides`, {
            method: 'POST',
            body: data,
            headers: headers.value
        })
    }

    const deleteSlide = async (slideId: string) => {
        return await $fetch(`${apiBase}/admin/stories/slides/${slideId}`, {
            method: 'DELETE',
            headers: headers.value
        })
    }

    const uploadStoryImage = async (file: File) => {
        const formData = new FormData()
        formData.append('file', file)

        return await $fetch(`${apiBase}/admin/stories/upload`, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${authToken.value}`
            }
        })
    }

    // Users
    const getUsers = async (params?: any) => {
        return await $fetch(`${apiBase}/users`, {
            params,
            headers: headers.value
        })
    }

    const deleteUser = async (id: string) => {
        return await $fetch(`${apiBase}/users/${id}`, {
            method: 'DELETE',
            headers: headers.value
        })
    }

    const createStaffUser = async (data: any) => {
        return await $fetch(`${apiBase}/users/staff`, {
            method: 'POST',
            body: data,
            headers: headers.value
        })
    }

    const updateUserStatus = async (id: string, is_active: boolean) => {
        return await $fetch(`${apiBase}/users/${id}/status`, {
            method: 'PATCH',
            body: { is_active },
            headers: headers.value
        })
    }

    // Blacklist
    const getBlacklist = async (params?: any) => {
        return await $fetch(`${apiBase}/blacklist`, {
            params,
            headers: headers.value
        })
    }

    const addToBlacklist = async (data: any) => {
        return await $fetch(`${apiBase}/blacklist`, {
            method: 'POST',
            body: data,
            headers: headers.value
        })
    }

    const removeFromBlacklist = async (id: string) => {
        return await $fetch(`${apiBase}/blacklist/${id}`, {
            method: 'DELETE',
            headers: headers.value
        })
    }

    const removeFromBlacklistByPhone = async (phone: string) => {
        return await $fetch(`${apiBase}/blacklist/by-phone/${encodeURIComponent(phone)}`, {
            method: 'DELETE',
            headers: headers.value
        })
    }

    // Payments
    const getPayments = async (params?: any) => {
        return await $fetch(`${apiBase}/payments`, {
            params,
            headers: headers.value
        })
    }

    const getPaymentStats = async () => {
        return await $fetch(`${apiBase}/payments/stats`, {
            headers: headers.value
        })
    }

    // Documents
    const uploadDocument = async (applicationId: string, file: File, documentType: string) => {
        const formData = new FormData()
        formData.append('file', file)

        return await $fetch(`${apiBase}/documents/upload`, {
            method: 'POST',
            params: {
                app_id: applicationId,
                type: documentType
            },
            body: formData,
            headers: {
                'Authorization': `Bearer ${authToken.value}`
            }
        })
    }

    const getDocuments = async (applicationId: string) => {
        return await $fetch(`${apiBase}/documents/applications/${applicationId}/documents`, {
            headers: headers.value
        })
    }

    const getVideos = async (applicationId: string) => {
        return await $fetch(`${apiBase}/documents/applications/${applicationId}/videos`, {
            headers: headers.value
        })
    }

    return {
        // Auth
        login,
        register,
        logout,
        getCurrentUser,
        authToken,
        currentUser,
        hasRole,
        apiBase,

        // Admin & System
        getStats,
        getAuditLogs,
        getSettings,
        updateSetting,

        // Cars
        getCars,
        getCar,
        createCar,
        updateCar,
        deleteCar,

        // Applications
        getApplications,
        getApplication,
        adminCreateApplication,
        updateApplicationStatus,
        updateApplicationContactStatus,
        updateApplicationChecklist,
        addApplicationComment,
        getApplicationComments,
        assignOperator,
        assignManager,
        getStories,
        createStory,
        updateStory,
        deleteStory,
        addSlide,
        deleteSlide,
        uploadStoryImage,

        // Users
        getUsers,
        deleteUser,
        createStaffUser,
        updateUserStatus,

        // Blacklist
        getBlacklist,
        addToBlacklist,
        removeFromBlacklist,
        removeFromBlacklistByPhone,

        // Payments
        getPayments,
        getPaymentStats,

        // Documents
        uploadDocument,
        getDocuments,
        getVideos
    }
}
