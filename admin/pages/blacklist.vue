<template>
    <div class="blacklist-page animate-fade-in">
        <header class="page-header">
            <div class="container">
                <div class="flex-between items-end">
                    <div>
                        <h1 class="text-thin">{{ $t('blacklist.title') }}</h1>
                        <p class="text-secondary text-light">{{ $t('blacklist.subtitle') }}</p>
                    </div>
                    <div class="header-actions">
                        <button class="btn btn-error btn-sm shadow-lg" @click="showModal = true">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor"
                                stroke-width="2" style="margin-right: 8px;">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                            </svg>
                            {{ $t('blacklist.block') }}
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <!-- Subtle Safety Banner -->
            <div class="safety-banner mb-10 card border-error-light shadow-sm">
                <div class="flex gap-4 items-center">
                    <div class="safety-icon-wrap">
                        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor"
                            stroke-width="2" class="text-error">
                            <path
                                d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                            <line x1="12" y1="9" x2="12" y2="13" />
                            <line x1="12" y1="17" x2="12.01" y2="17" />
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-thin m-0 mb-1 text-primary">{{ $t('blacklist.bannerTitle') }}</h3>
                        <p class="smaller-text text-secondary font-medium m-0">
                            {{ $t('blacklist.bannerText') }}
                        </p>
                    </div>
                </div>
            </div>

            <!-- Blacklist Table -->
            <div class="card no-padding overflow-hidden border-light shadow-lg">
                <div class="table-responsive">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th class="pl-8">{{ $t('blacklist.table.identifier') }}</th>
                                <th>{{ $t('blacklist.table.reason') }}</th>
                                <th>{{ $t('blacklist.table.issuer') }}</th>
                                <th>{{ $t('blacklist.table.date') }}</th>
                                <th class="text-right pr-8">{{ $t('common.actions') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="loading && items.length === 0" v-for="i in 3" :key="i">
                                <td colspan="5" class="py-12 text-center text-tertiary smaller-text">{{
                                    $t('blacklist.empty.checking') }}</td>
                            </tr>
                            <tr v-else-if="items.length === 0">
                                <td colspan="5" class="py-20 text-center text-tertiary">
                                    <div class="mb-4 opacity-20 mx-auto w-12">
                                        <svg viewBox="0 0 24 24" width="48" height="48" fill="none"
                                            stroke="currentColor" stroke-width="1">
                                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                                        </svg>
                                    </div>
                                    <p class="font-medium">{{ $t('blacklist.empty.clean') }}</p>
                                </td>
                            </tr>
                            <tr v-else v-for="item in items" :key="item.id" class="premium-row hover-effect">
                                <td class="pl-8 py-5">
                                    <div class="flex items-center gap-3">
                                        <div class="user-avatar-placeholder danger">
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                                                stroke="currentColor" stroke-width="2">
                                                <path
                                                    d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                                            </svg>
                                        </div>
                                        <div class="font-bold text-primary mono-font">{{ formatPhone(item.phone) }}
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div class="smaller-text text-secondary font-medium">
                                        {{ translateReason(item) }}
                                    </div>
                                </td>
                                <td>
                                    <div class="small-badge">{{ item.blocked_by_name || 'System' }}</div>
                                </td>
                                <td class="text-tertiary smaller-text font-medium">{{ formatDate(item.created_at) }}
                                </td>
                                <td class="text-right pr-8 py-5">
                                    <div class="flex justify-end">
                                        <button @click="removeItem(item.id)"
                                            class="btn-ghost-success smaller-text font-bold">
                                            {{ $t('blacklist.unblock') }}
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Block Identity Modal -->
        <Teleport to="body">
            <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
                <div class="modal-card animate-scale-in">
                    <div class="modal-header mb-8">
                        <h3 class="text-thin m-0 text-white">{{ $t('blacklist.modal.title') }}</h3>
                        <p class="text-tertiary smaller-text">{{ $t('blacklist.modal.subtitle') }}</p>
                    </div>

                    <div class="modal-body mb-8">
                        <div class="form-group mb-6">
                            <label class="section-label">{{ $t('blacklist.form.phone') }}</label>
                            <input v-model="form.phone" type="text" placeholder="+998 90 123 45 67"
                                class="input input-lg font-medium">
                        </div>
                        <div class="form-group mb-6">
                            <label class="section-label">{{ $t('blacklist.form.category') }}</label>
                            <select v-model="form.reason" class="input input-lg">
                                <option value="" disabled>{{ $t('blacklist.form.select') }}</option>
                                <option value="fraud">{{ $t('blacklist.reasons.fraud') }}</option>
                                <option value="spam">{{ $t('blacklist.reasons.spam') }}</option>
                                <option value="bad_history">{{ $t('blacklist.reasons.badHistory') }}</option>
                                <option value="harassment">{{ $t('blacklist.reasons.harassment') }}</option>
                                <option value="policy_violation">{{ $t('blacklist.reasons.policyViolation') }}</option>
                                <option value="other">{{ $t('blacklist.reasons.other') }}</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="section-label">{{ $t('blacklist.form.note') }}</label>
                            <textarea v-model="form.reason_note" rows="3" class="input input-lg"
                                :placeholder="$t('blacklist.form.reasonNote')"></textarea>
                        </div>
                    </div>

                    <div class="modal-footer flex gap-3">
                        <button class="btn btn-sm flex-grow font-medium" @click="showModal = false">{{
                            $t('common.cancel') }}</button>
                        <button class="btn btn-error btn-sm flex-grow font-bold" @click="handleBlock"
                            :disabled="!form.phone || !form.reason">
                            {{ $t('blacklist.confirmBlock') }}
                        </button>
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const { t, locale } = useI18n()
const toast = useToast()
const { getBlacklist, addToBlacklist, removeFromBlacklist } = useApi()

const items = ref<any[]>([])
const loading = ref(true)
const showModal = ref(false)

const form = ref({
    phone: '',
    reason: '',
    reason_note: ''
})

const fetchList = async () => {
    loading.value = true
    try {
        const response: any = await getBlacklist()
        items.value = response.items || response || []
    } catch (err) {
        items.value = []
    } finally {
        loading.value = false
    }
}

const handleBlock = async () => {
    try {
        const res: any = await addToBlacklist(form.value)
        items.value.unshift(res)
        showModal.value = false
        form.value = { phone: '', reason: '', reason_note: '' }
        fetchList()
        toast.success(t('common.success'))
    } catch (err: any) {
        toast.error(t('blacklist.error'), err?.data?.detail)
    }
}

const removeItem = async (id: string) => {
    if (confirm(t('blacklist.confirmRemove'))) {
        try {
            await removeFromBlacklist(id)
            fetchList()
            toast.success(t('common.success'))
        } catch (err: any) {
            toast.error(t('blacklist.removeError'), err?.data?.detail)
        }
    }
}

const formatDate = (dateStr: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString(locale.value, {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    })
}

const formatPhone = (phone: string) => {
    return phone || t('blacklist.reasons.notSpecified')
}

const translateReason = (item: any) => {
    if (!item.reason) return t('blacklist.reasons.notSpecified')

    if (item.reason === 'other' && item.reason_note) {
        return item.reason_note
    }

    const map: Record<string, string> = {
        'fraud': 'fraud',
        'spam': 'spam',
        'bad_history': 'badHistory',
        'harassment': 'harassment',
        'policy_violation': 'policyViolation',
        'other': 'other'
    }

    const key = map[item.reason.toLowerCase()]
    return key ? t(`blacklist.reasons.${key}`) : item.reason
}

onMounted(fetchList)

definePageMeta({ layout: false })
</script>

<style scoped>
.page-header {
    padding: var(--spacing-xl) 0 var(--spacing-lg);
}

.safety-banner {
    background: rgba(239, 68, 68, 0.05);
    border: 1px solid rgba(239, 68, 68, 0.1);
    padding: 2rem;
    border-radius: var(--radius-lg);
    transition: all 0.3s ease;
}

.safety-banner:hover {
    background: rgba(239, 68, 68, 0.08);
}

.safety-icon-wrap {
    width: 48px;
    height: 48px;
    background: rgba(239, 68, 68, 0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.15);
}

.small-badge {
    display: inline-block;
    padding: 4px 10px;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    font-size: 0.75rem;
    color: var(--color-text-tertiary);
    font-weight: 600;
}

.user-avatar-placeholder {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
}

.user-avatar-placeholder.danger {
    color: var(--color-error);
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.2);
}

.mono-font {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
}

.btn-ghost-success {
    background: transparent;
    border: none;
    color: var(--color-success);
    cursor: pointer;
    padding: 0.5rem 1rem;
    border-radius: var(--radius-sm);
    transition: var(--transition);
    letter-spacing: 0.05em;
    opacity: 0.8;
}

.btn-ghost-success:hover {
    background: rgba(16, 185, 129, 0.1);
    opacity: 1;
    text-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
}

.btn-error {
    background: var(--color-error);
    color: #fff;
    border: none;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.btn-error:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

/* Modal Styling to match Users */
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    z-index: 2000;
}

.modal-card {
    background: var(--color-bg-card);
    width: 100%;
    max-width: 500px;
    padding: 3rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--color-border);
    box-shadow: 0 40px 100px rgba(0, 0, 0, 0.6);
}

.section-label {
    display: block;
    text-transform: uppercase;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--color-text-tertiary);
    margin-bottom: 0.6rem;
}

.input-lg {
    width: 100%;
    padding: 1rem;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    color: var(--color-text-primary);
    font-size: 1rem;
    transition: all 0.2s;
}

.input-lg:focus {
    border-color: var(--color-text-primary);
    outline: none;
    background: var(--color-bg-primary);
}

.border-light {
    border-color: var(--color-border-light);
}

.pl-8 {
    padding-left: 2.5rem;
}

.pr-8 {
    padding-right: 2.5rem;
}

.py-5 {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}

.py-20 {
    padding-top: 5rem;
    padding-bottom: 5rem;
}

.mb-10 {
    margin-bottom: 2.5rem;
}

.hover-effect {
    transition: background 0.2s;
}

.hover-effect:hover {
    background: var(--color-bg-hover);
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.96) translateY(10px);
    }

    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

.animate-scale-in {
    animation: scaleIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@media (max-width: 768px) {
    .header-actions {
        width: 100%;
    }

    .safety-banner {
        padding: 1.5rem;
        flex-direction: column;
        align-items: flex-start;
    }

    .safety-banner svg {
        margin-bottom: 0.5rem;
    }
}
</style>
