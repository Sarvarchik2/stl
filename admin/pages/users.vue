<template>
    <div v-if="isLoadingSession" class="flex-center py-20">
        <div class="text-center text-tertiary">
            <p>Проверка доступа...</p>
        </div>
    </div>
    <div v-else-if="!hasRole('operator')" class="flex-center py-20">
        <div class="text-center">
            <h2 class="text-thin">Доступ ограничен</h2>
            <p class="text-secondary">У вас нет прав для управления персоналом</p>
            <NuxtLink to="/dashboard" class="btn btn-primary btn-sm mt-4">Вернуться в хаб</NuxtLink>
        </div>
    </div>
    <div v-else class="users-page animate-fade-in">
        <header class="page-header">
            <div class="container">
                <div class="flex-between">
                    <div>
                        <h1 class="text-thin">Сотрудники</h1>
                        <p class="text-secondary text-light">Управление доступом и ролями системы</p>
                    </div>
                    <div class="header-actions" v-if="hasRole('admin')">
                        <button class="btn btn-primary btn-sm" @click="openModal()">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor"
                                stroke-width="2" style="margin-right: 8px;">
                                <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                                <circle cx="8.5" cy="7" r="4" />
                                <line x1="20" y1="8" x2="20" y2="14" />
                                <line x1="23" y1="11" x2="17" y2="11" />
                            </svg>
                            Добавить сотрудника
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <!-- Minimal Search Bar -->
            <div class="search-filter-row mb-8">
                <div class="flex gap-4">
                    <div class="search-wrap">
                        <input v-model="searchQuery" type="text" placeholder="Поиск по имени, телефону..."
                            class="input input-minimal">
                    </div>
                    <select v-model="roleFilter" class="input input-minimal" style="width: 160px;">
                        <option value="all">Все роли</option>
                        <option v-for="role in roles" :key="role.key" :value="role.key">
                            {{ role.label }}
                        </option>
                    </select>
                </div>
            </div>

            <!-- Clean Table -->
            <div class="card no-padding overflow-hidden border-light shadow-sm">
                <div class="table-responsive">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th class="pl-8">Пользователь</th>
                                <th>Роль</th>
                                <th>Телефон</th>
                                <th>Статус</th>
                                <th class="text-right pr-8">Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="loading" v-for="i in 3" :key="i">
                                <td colspan="5" class="py-12 text-center text-tertiary">Обновление...</td>
                            </tr>
                            <tr v-else v-for="user in filteredUsers" :key="user.id" class="premium-row clickable-row"
                                @click="hasRole('admin') && openModal(user)">
                                <td class="pl-8 py-5">
                                    <div class="flex items-center gap-4">
                                        <div class="user-id-circle">{{ user.first_name?.charAt(0) }}</div>
                                        <div>
                                            <div class="font-medium text-primary">{{ user.first_name }} {{
                                                user.last_name }}</div>
                                            <div class="smaller-text text-tertiary">{{ user.email || 'Нет email' }}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td><span class="badge" :class="user.role">{{ translateRole(user.role) }}</span></td>
                                <td class="text-secondary">{{ user.phone || '—' }}</td>
                                <td>
                                    <div class="flex items-center gap-2">
                                        <span class="status-dot" :class="{ active: user.is_active }"></span>
                                        <span class="text-secondary smaller-text">{{ user.is_active ? 'Активен' :
                                            'Заблокирован' }}</span>
                                    </div>
                                </td>
                                <td class="text-right pr-8">
                                    <div class="flex justify-end gap-2" @click.stop v-if="hasRole('admin')">
                                        <button @click="toggleStatus(user)" class="btn btn-sm btn-outline btn-minimal"
                                            :class="user.is_active ? 'text-error' : 'text-success'">
                                            {{ user.is_active ? 'Бан' : 'Активировать' }}
                                        </button>
                                        <button @click="openModal(user)" class="btn btn-icon-only btn-ghost">
                                            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor"
                                                fill="none" stroke-width="2">
                                                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                                                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                                            </svg>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="spacer"></div>
        </div>


        <!-- Confirmation Modal -->
        <Teleport to="body">
            <div v-if="showConfirmModal" class="modal-overlay" @click.self="closeConfirm">
                <div class="modal-card modal-compact animate-scale-in">
                    <div class="text-center mb-6">
                        <div class="icon-circle mb-4 mx-auto" :class="confirmType">
                            <svg v-if="confirmType === 'danger'" width="24" height="24" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2">
                                <path
                                    d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                            </svg>
                            <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                                <polyline points="22 4 12 14.01 9 11.01" />
                            </svg>
                        </div>
                        <h3 class="text-lg font-bold mb-2">{{ confirmTitle }}</h3>
                        <p class="text-secondary text-sm">{{ confirmMessage }}</p>
                    </div>

                    <div class="flex gap-3">
                        <button class="btn btn-sm flex-grow" @click="closeConfirm">Отмена</button>
                        <button class="btn btn-sm flex-grow font-bold"
                            :class="confirmType === 'danger' ? 'btn-error' : 'btn-primary'" @click="executeConfirm"
                            :disabled="processingConfirm">
                            {{ processingConfirm ? 'Загрузка...' : confirmButtonText }}
                        </button>
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const { getUsers, createStaffUser, updateUserStatus, addToBlacklist, removeFromBlacklistByPhone, hasRole, authToken, currentUser } = useApi()

const isLoadingSession = computed(() => !!authToken.value && !currentUser.value)

const users = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
// User Modal
const showModal = ref(false)
const editingId = ref<string | null>(null)

// Confirmation Modal
const showConfirmModal = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmButtonText = ref('Подтвердить')
const confirmType = ref('primary') // or 'danger'
const processingConfirm = ref(false)
let pendingConfirmAction: (() => Promise<void>) | null = null

const searchQuery = ref('')
const roleFilter = ref('all')

const roles = [
    { key: 'operator', label: 'Оператор' },
    { key: 'supervisor', label: 'Супервизор' },
    { key: 'manager', label: 'Менеджер' },
    { key: 'admin', label: 'Админ' },
    { key: 'owner', label: 'Владелец' },
    { key: 'client', label: 'Клиент' }
]

const form = ref({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    role: 'operator',
    password: ''
})

const fetchUsers = async () => {
    loading.value = true
    try {
        const response: any = await getUsers()
        users.value = response.items || response || []
    } catch (err) {
        users.value = []
    } finally {
        loading.value = false
    }
}

const openModal = (user?: any) => {
    if (user) {
        editingId.value = user.id
        form.value = { ...user, password: '' }
    } else {
        editingId.value = null
        form.value = { first_name: '', last_name: '', email: '', phone: '', role: 'operator', password: '' }
    }
    showModal.value = true
}

const saveUser = async () => {
    saving.value = true
    try {
        if (editingId.value) {
            // Update profile logic would go here
            // For now, we might just be handling creates. 
            // If update logic exists in standard API hook, call it here.
        } else {
            const newUser = await createStaffUser(form.value)
            users.value.unshift(newUser)
        }
        showModal.value = false
        fetchUsers()
    } catch (err: any) {
        alert(err?.data?.detail || 'Ошибка при сохранении')
    } finally {
        saving.value = false
    }
}

// Custom Confirm Logic
const openConfirm = (title: string, message: string, type: 'primary' | 'danger', action: () => Promise<void>) => {
    confirmTitle.value = title
    confirmMessage.value = message
    confirmType.value = type
    confirmButtonText.value = type === 'danger' ? 'Заблокировать' : 'Активировать'
    pendingConfirmAction = action
    showConfirmModal.value = true
}

const closeConfirm = () => {
    showConfirmModal.value = false
    pendingConfirmAction = null
}

const executeConfirm = async () => {
    if (!pendingConfirmAction) return
    processingConfirm.value = true
    try {
        await pendingConfirmAction()
        closeConfirm()
    } catch (e) {
        console.error(e)
    } finally {
        processingConfirm.value = false
    }
}

const toggleStatus = (user: any) => {
    const isBlocking = user.is_active
    const title = isBlocking ? 'Блокировка доступа' : 'Активация доступа'
    const message = isBlocking
        ? `Вы уверены, что хотите заблокировать ${user.first_name}? Пользователь будет также добавлен в черный список.`
        : `Восстановить доступ для ${user.first_name}? Пользователь также будет удален из черного списка.`

    openConfirm(title, message, isBlocking ? 'danger' : 'primary', async () => {
        try {
            await updateUserStatus(user.id, !user.is_active)
            user.is_active = !user.is_active

            if (isBlocking) {
                // Blocking: add to blacklist
                await addToBlacklist({
                    phone: user.phone,
                    reason: 'other',
                    reason_note: `Автоматическая блокировка администратором: ${user.first_name} ${user.last_name}`,
                    block_type: 'permanent'
                }).catch(err => console.warn('Failed to auto-add to blacklist', err))
            } else {
                // Unblocking: remove from blacklist
                await removeFromBlacklistByPhone(user.phone).catch(err => console.warn('Failed to remove from blacklist', err))
            }
        } catch (err: any) {
            alert(err?.data?.detail || 'Ошибка при изменении статуса')
        }
    })
}

const filteredUsers = computed(() => {
    return users.value.filter(u => {
        const fullName = `${u.first_name || ''} ${u.last_name || ''}`.toLowerCase()
        const matchesSearch = !searchQuery.value ||
            fullName.includes(searchQuery.value.toLowerCase()) ||
            u.phone?.includes(searchQuery.value)
        const matchesRole = roleFilter.value === 'all' || u.role === roleFilter.value
        return matchesSearch && matchesRole
    })
})

const translateRole = (r: string) => {
    const map: Record<string, string> = {
        'operator': 'Оператор',
        'supervisor': 'Супервизор',
        'manager': 'Менеджер',
        'admin': 'Админ',
        'owner': 'Владелец',
        'client': 'Клиент'
    }
    return map[r.toLowerCase()] || r
}

onMounted(() => {
    if (hasRole('operator')) {
        fetchUsers()
    }
})
definePageMeta({ layout: false })
</script>

<style scoped>
.page-header {
    padding: var(--spacing-xl) 0 var(--spacing-lg);
}

.search-wrap {
    flex-grow: 1;
    max-width: 400px;
}

.input-minimal {
    background: transparent;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
}

.input-minimal:focus {
    border-color: var(--color-text-primary);
    background: var(--color-bg-secondary);
}

.border-light {
    border-color: var(--color-border-light);
}

.user-id-circle {
    width: 36px;
    height: 36px;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--color-text-primary);
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--color-border);
}

.status-dot.active {
    background: var(--color-success);
}

.btn-ghost {
    background: transparent;
    border: none;
    opacity: 0.4;
}

.btn-ghost:hover {
    opacity: 1;
    background: var(--color-bg-hover);
}

.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.85);
    /* Darker backdrop */
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    height: 100vh;
}

/* Modal Card Refinements */
.modal-card {
    background: var(--color-bg-card);
    color: var(--color-text-primary);
    width: 100%;
    max-width: 450px;
    padding: 2.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--color-border);
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
}

/* Compact version for confirmation */
.modal-compact {
    max-width: 400px;
    padding: 2.5rem 2rem;
    text-align: center;
    /* Removed fixed background to respect theme */
}

.icon-circle {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    margin: 0 auto 1.5rem auto;
    /* Centered with margin */
}

.icon-circle.danger {
    color: var(--color-error);
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.2);
}

.icon-circle.primary {
    color: var(--color-success);
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.2);
}

.btn-error {
    background: var(--color-error);
    color: #ffffff;
    border: 1px solid var(--color-error);
}

.btn-error:hover {
    opacity: 0.9;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.section-label {
    display: block;
    text-transform: uppercase;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--color-text-tertiary);
    margin-bottom: 0.5rem;
}

.pl-8 {
    padding-left: 2rem;
}

.pr-8 {
    padding-right: 2rem;
}

.py-5 {
    padding-top: 1.25rem;
    padding-bottom: 1.25rem;
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

.animate-scale-in {
    animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.spacer {
    height: 8rem;
}

@media (max-width: 640px) {
    .search-filter-row .flex {
        flex-direction: column;
    }

    .search-filter-row .input {
        width: 100% !important;
    }

    .header-actions,
    .header-actions .btn {
        width: 100%;
    }
}
</style>
