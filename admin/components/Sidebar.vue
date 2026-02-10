<template>
    <aside class="sidebar" :class="{ 'show': isOpen }">
        <div class="sidebar-brand">
            <div class="brand-wrapper">
                <img src="/favicon.svg" alt="STL Admin" class="brand-logo" />
                <div class="brand-text">
                    <span class="brand-title">STL</span>
                    <span class="brand-subtitle">Admin</span>
                </div>
            </div>
        </div>

        <nav class="sidebar-nav">
            <NuxtLink to="/dashboard" class="nav-link" @click="$emit('close')">
                <div class="nav-link-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="3" y="3" width="7" height="7" rx="1" />
                        <rect x="14" y="3" width="7" height="7" rx="1" />
                        <rect x="14" y="14" width="7" height="7" rx="1" />
                        <rect x="3" y="14" width="7" height="7" rx="1" />
                    </svg>
                </div>
                <span>{{ $t('nav.dashboard') }}</span>
            </NuxtLink>

            <NuxtLink to="/applications" class="nav-link" @click="$emit('close')">
                <div class="nav-link-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" />
                        <line x1="16" y1="17" x2="8" y2="17" />
                        <polyline points="10 9 9 9 8 9" />
                    </svg>
                </div>
                <span>{{ $t('nav.applications') }}</span>
            </NuxtLink>

            <NuxtLink to="/cars" class="nav-link" @click="$emit('close')">
                <div class="nav-link-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path
                            d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9L18.7 7h-1.2l-1.3-4.4c-.1-.3-.4-.6-.7-.6H8.5c-.3 0-.6.3-.7.6L6.5 7H5.3l-1.8 11L6 13c0 .6.4 1 1 1h2m10 0v2c0 .6-.4 1-1 1H8c-.6 0-1-.4-1-1v-2m10 0H7" />
                    </svg>
                </div>
                <span>{{ $t('nav.cars') }}</span>
            </NuxtLink>

            <NuxtLink v-if="hasRole('operator')" to="/stories" class="nav-link" @click="$emit('close')">
                <div class="nav-link-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="12" cy="12" r="10" />
                        <circle cx="12" cy="12" r="6" />
                        <circle cx="12" cy="12" r="2" />
                    </svg>
                </div>
                <span>{{ $t('nav.stories') }}</span>
            </NuxtLink>

            <NuxtLink v-if="hasRole('operator')" to="/users" class="nav-link" @click="$emit('close')">
                <div class="nav-link-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                        <path d="M23 21v-2a4 4 0 00-3-3.87" />
                        <path d="M16 3.13a4 4 0 010 7.75" />
                    </svg>
                </div>
                <span>{{ $t('nav.users') }}</span>
            </NuxtLink>

            <NuxtLink v-if="hasRole('operator')" to="/payments" class="nav-link" @click="$emit('close')">
                <div class="nav-link-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
                        <line x1="1" y1="10" x2="23" y2="10" />
                    </svg>
                </div>
                <span>{{ $t('nav.payments') }}</span>
            </NuxtLink>

            <NuxtLink v-if="hasRole('supervisor')" to="/blacklist" class="nav-link" @click="$emit('close')">
                <div class="nav-link-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
                    </svg>
                </div>
                <span>{{ $t('nav.blacklist') }}</span>
            </NuxtLink>
        </nav>

        <div class="sidebar-footer"
            style="padding: 1rem; border-top: 1px solid var(--color-border); display: flex; flex-direction: column; gap: 0.5rem;">

            <!-- Language Switcher -->
            <div style="padding: 0 0.5rem 0.5rem;">
                <LanguageSwitcher />
            </div>

            <button class="nav-link theme-toggle-btn" @click="toggleTheme"
                style="width: 100%; border: none; background: transparent; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 8px; color: var(--color-text-secondary); transition: 0.2s;">
                <div class="nav-link-icon" style="display: flex; align-items: center; justify-content: center;">
                    <svg v-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                        width="18" height="18">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18"
                        height="18">
                        <circle cx="12" cy="12" r="5" />
                        <line x1="12" y1="1" x2="12" y2="3" />
                        <line x1="12" y1="21" x2="12" y2="23" />
                        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                        <line x1="1" y1="12" x2="3" y2="12" />
                        <line x1="21" y1="12" x2="23" y2="12" />
                        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                    </svg>
                </div>
                <span>{{ theme === 'light' ? $t('settings.darkTheme') : $t('settings.lightTheme') }}</span>
            </button>

            <NuxtLink v-if="hasRole('manager')" to="/settings" class="nav-link" @click="$emit('close')">
                <div class="nav-link-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="12" cy="12" r="3" />
                        <path
                            d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
                    </svg>
                </div>
                <span>{{ $t('nav.settings') }}</span>
            </NuxtLink>

            <button class="nav-link logout-btn-sidebar" @click="handleLogout">
                <div class="nav-link-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
                        <polyline points="16 17 21 12 16 7" />
                        <line x1="21" y1="12" x2="9" y2="12" />
                    </svg>
                </div>
                <span class="font-bold">{{ $t('nav.logout') }}</span>
            </button>
        </div>
    </aside>
</template>

<script setup>
import { inject } from 'vue'

const theme = inject('theme')
const toggleTheme = inject('toggleTheme')
const { hasRole, logout } = useApi()
const router = useRouter()

const handleLogout = () => {
    logout()
    router.push('/')
}

defineProps({
    isOpen: Boolean
})

defineEmits(['close'])
</script>

<style scoped>
.sidebar {
    width: 260px;
    height: 100vh;
    background: var(--color-bg-primary);
    border-right: 1px solid var(--color-border);
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.sidebar-brand {
    padding: 1.5rem;
    color: var(--color-text-primary);
}

.brand-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-logo {
    width: 32px;
    height: 32px;
}

.brand-text {
    display: flex;
    flex-direction: column;
    justify-content: center;
    line-height: 1;
}

.brand-title {
    font-weight: 700;
    font-size: 1.1rem;
    letter-spacing: -0.5px;
    color: var(--color-text-primary);
    background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.brand-subtitle {
    font-size: 0.75rem;
    color: var(--color-text-tertiary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.sidebar-nav {
    flex: 1;
    padding: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    color: var(--color-text-secondary);
    text-decoration: none;
    border-radius: var(--radius-md);
    transition: all 0.2s ease;
    font-size: 0.9rem;
}

.nav-link:hover {
    background: var(--color-bg-secondary);
    color: var(--color-text-primary);
}

.nav-link.router-link-active {
    background: rgba(255, 255, 255, 0.05);
    color: var(--color-text-primary);
    font-weight: 500;
}

.nav-link-icon {
    width: 20px;
    height: 20px;
}

.logout-btn-sidebar {
    width: 100%;
    border: none;
    background: rgba(239, 68, 68, 0.05) !important;
    cursor: pointer;
    text-align: left;
    color: #ef4444 !important;
}

.logout-btn-sidebar:hover {
    background: #ef4444 !important;
    color: white !important;
}

@media (max-width: 1024px) {
    .sidebar {
        position: fixed;
        left: -260px;
        transition: left 0.3s ease;
    }

    .sidebar.show {
        left: 0;
    }
}
</style>
