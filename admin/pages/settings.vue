<template>
    <div class="settings-page animate-fade-in">
        <header class="page-header">
            <div class="container">
                <h1 class="text-thin">System Settings</h1>
                <p class="text-secondary">Configure business rules, API keys and general preferences</p>
            </div>
        </header>

        <div class="container">
            <div class="card card-minimal no-padding overflow-hidden">
                <div class="settings-layout">
                    <!-- Sidebar tabs -->
                    <div class="settings-sidebar">
                        <button v-for="t in tabs" :key="t.id" class="settings-tab-btn"
                            :class="{ active: activeTab === t.id }" @click="activeTab = t.id">
                            {{ t.label }}
                        </button>
                        <div class="spacer-flex"></div>
                        <button class="btn btn-outline btn-sm m-4 text-error" @click="handleLogout"
                            style="border-color: rgba(217, 0, 75, 0.1);">
                            Sign Out
                        </button>
                    </div>

                    <!-- Main content -->
                    <div class="settings-content">
                        <!-- General Tab -->
                        <div v-if="activeTab === 'general'" class="tab-pane">
                            <h3 class="mb-6">General Configuration</h3>
                            <div class="form-grid">
                                <div class="form-group">
                                    <label class="label mb-1 block">Company Name</label>
                                    <input v-model="settings.company_name" type="text" class="input"
                                        placeholder="STL Auto">
                                </div>
                                <div class="form-group">
                                    <label class="label mb-1 block">Contact Email</label>
                                    <input v-model="settings.contact_email" type="email" class="input"
                                        placeholder="info@stlauto.uz">
                                </div>
                                <div class="form-group">
                                    <label class="label mb-1 block">Support Phone</label>
                                    <input v-model="settings.support_phone" type="text" class="input"
                                        placeholder="+998 90 123 45 67">
                                </div>
                            </div>
                            <button class="btn btn-primary mt-8" @click="saveSettings" :disabled="saving">{{ saving ?
                                'Saving...' : 'Save Changes' }}</button>
                        </div>

                        <!-- Business Rules Tab -->
                        <div v-if="activeTab === 'business'" class="tab-pane">
                            <h3 class="mb-6">Business Logic & Pricing</h3>
                            <div class="card bg-hover p-4 mb-8">
                                <p class="small-text text-secondary m-0">These values affect calculation of car prices
                                    and loan eligibility across the platform.</p>
                            </div>
                            <div class="form-grid">
                                <div class="form-group">
                                    <label class="label mb-1 block">Default Markup (%)</label>
                                    <input v-model.number="settings.markup_percent" type="number" class="input"
                                        step="0.1">
                                    <p class="smaller-text text-tertiary mt-1">Added to car source price</p>
                                </div>
                                <div class="form-group">
                                    <label class="label mb-1 block">Min Down Payment (%)</label>
                                    <input v-model.number="settings.min_down_payment" type="number" class="input">
                                </div>
                                <div class="form-group">
                                    <label class="label mb-1 block">Blacklist Threshold</label>
                                    <input v-model.number="settings.blacklist_threshold" type="number" class="input">
                                    <p class="smaller-text text-tertiary mt-1">Number of rejections before auto-block
                                    </p>
                                </div>
                            </div>
                            <button class="btn btn-primary mt-8" @click="saveSettings" :disabled="saving">Update
                                Rules</button>
                        </div>

                        <!-- API tab placeholder -->
                        <div v-if="activeTab === 'api'" class="tab-pane">
                            <h3 class="mb-6">API & Integrations</h3>
                            <div class="form-group mb-4">
                                <label class="label mb-1 block">Public API Base</label>
                                <input v-model="settings.api_base" type="text" class="input text-secondary" readonly>
                            </div>
                            <div class="form-group mb-6">
                                <label class="label mb-1 block">Maps API Key</label>
                                <input type="password" value="************************" class="input" readonly>
                            </div>
                            <p class="text-tertiary small-text">API keys are managed via environment variables for
                                security.</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="spacer"></div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const { getSettings, updateSetting, logout } = useApi()
const router = useRouter()

const tabs = [
    { id: 'general', label: 'General' },
    { id: 'business', label: 'Business Rules' },
    { id: 'api', label: 'Integrations' }
]

const activeTab = ref('general')
const saving = ref(false)

const settings = ref({
    company_name: 'STL Auto',
    contact_email: 'admin@stlauto.uz',
    support_phone: '+998 90 000 00 00',
    markup_percent: 15.0,
    min_down_payment: 30,
    blacklist_threshold: 3,
    api_base: 'http://localhost:8000/api/v1'
})

const fetchSettings = async () => {
    try {
        const res: any = await getSettings()
        if (res && res.length > 0) {
            res.forEach((item: any) => {
                if (item.key in settings.value) {
                    (settings.value as any)[item.key] = item.value
                }
            })
        }
    } catch (err) {
        console.warn('Using default settings')
    }
}

const saveSettings = async () => {
    saving.value = true
    try {
        // We save settings one by one or as needed
        const promises = Object.entries(settings.value).map(([key, value]) => {
            return updateSetting(key, value)
        })
        await Promise.all(promises)
        alert('Settings updated successfully!')
    } catch (err: any) {
        alert(err?.data?.detail || 'Failed to save settings')
    } finally {
        saving.value = false
    }
}

const handleLogout = () => {
    logout()
    router.push('/')
}

onMounted(fetchSettings)

definePageMeta({ layout: false })
</script>

<style scoped>
.page-header {
    padding: var(--spacing-xl) 0 var(--spacing-lg);
}

.settings-layout {
    display: flex;
    min-height: 600px;
}

.settings-sidebar {
    width: 240px;
    background: var(--color-bg-secondary);
    border-right: 1px solid var(--color-border);
    display: flex;
    flex-direction: column;
}

.settings-tab-btn {
    padding: 1rem 1.5rem;
    text-align: left;
    background: transparent;
    border: none;
    border-left: 2px solid transparent;
    color: var(--color-text-secondary);
    cursor: pointer;
    font-size: 0.95rem;
    transition: all 0.2s;
}

.settings-tab-btn:hover {
    background: var(--color-bg-hover);
    color: var(--color-text-primary);
}

.settings-tab-btn.active {
    background: var(--color-bg-hover);
    color: var(--color-text-primary);
    border-left-color: var(--color-accent);
}

.settings-content {
    flex-grow: 1;
    padding: 2.5rem;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.spacer-flex {
    flex-grow: 1;
}

.m-4 {
    margin: 1rem;
}

.mb-6 {
    margin-bottom: 1.5rem;
}

.mt-1 {
    margin-top: 0.25rem;
}

.mt-8 {
    margin-top: 2rem;
}

.p-4 {
    padding: 1rem;
}

.bg-hover {
    background: var(--color-bg-hover);
}

.spacer {
    height: 4rem;
}

@media (max-width: 768px) {
    .settings-layout {
        flex-direction: column;
    }

    .settings-sidebar {
        width: 100%;
        flex-direction: row;
        overflow-x: auto;
        border-right: none;
        border-bottom: 1px solid var(--color-border);
    }

    .settings-tab-btn {
        border-left: none;
        border-bottom: 2px solid transparent;
        white-space: nowrap;
    }

    .settings-tab-btn.active {
        border-bottom-color: var(--color-accent);
    }

    .settings-content {
        padding: 1.5rem;
    }

    .tab-pane .btn {
        width: 100%;
    }
}
</style>
