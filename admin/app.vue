<template>
    <div class="layout-wrapper">
        <!-- Top Bar for Mobile -->
        <header class="mobile-top-bar" v-if="isLoggedIn">
            <button class="burger-btn" @click="isSidebarOpen = !isSidebarOpen">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="3" y1="12" x2="21" y2="12" />
                    <line x1="3" y1="6" x2="21" y2="6" />
                    <line x1="3" y1="18" x2="21" y2="18" />
                </svg>
            </button>
            <div class="mobile-logo">STL Admin</div>
            <div style="width: 40px;"></div> <!-- Spacer -->
        </header>

        <!-- Sidebar Component -->
        <Sidebar v-if="isLoggedIn" :isOpen="isSidebarOpen" @close="isSidebarOpen = false" />

        <!-- Overlay for mobile sidebar -->
        <div class="sidebar-overlay" v-if="isSidebarOpen" @click="isSidebarOpen = false"></div>

        <main class="main-container" :class="{ 'full-width': !isLoggedIn }">
            <NuxtPage />
        </main>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const isSidebarOpen = ref(false)
const route = useRoute()
const router = useRouter()
const theme = ref('light')

// Simple check for login state based on route
const isLoggedIn = computed(() => {
    return route.path !== '/' && route.path !== '/login'
})

// Theme Logic
const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    updateTheme(theme.value)
}

const updateTheme = (newTheme) => {
    if (process.client) {
        document.documentElement.setAttribute('data-theme', newTheme)
        localStorage.setItem('stl-theme', newTheme)
    }
}

const { getCurrentUser } = useApi()

onMounted(async () => {
    if (process.client) {
        // Restore Theme
        const savedTheme = localStorage.getItem('stl-theme') || 'light'
        theme.value = savedTheme
        updateTheme(savedTheme)

        // Restore Session if on a protected route
        if (route.path !== '/' && route.path !== '/login') {
            try {
                const user = await getCurrentUser()
                if (!user || user.role === 'client') {
                    router.push('/')
                }
            } catch (err) {
                router.push('/')
            }
        }
    }
})

// Provide theme and toggle to children if needed
provide('theme', theme)
provide('toggleTheme', toggleTheme)

// Close sidebar on route change on mobile
watch(() => route.path, () => {
    isSidebarOpen.value = false
})
</script>

<style>
/* Layout Specific Styles */
.mobile-top-bar {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: var(--color-bg-secondary);
    border-bottom: 1px solid var(--color-border);
    align-items: center;
    justify-content: space-between;
    padding: 0 1rem;
    z-index: 900;
}

.burger-btn {
    background: transparent;
    border: none;
    color: var(--color-text-primary);
    cursor: pointer;
    width: 40px;
    height: 40px;
}

.mobile-logo {
    font-weight: 200;
    font-size: 1.25rem;
    letter-spacing: -1px;
}

.sidebar-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    z-index: 950;
    animation: fadeInOverlay 0.3s ease;
}

@keyframes fadeInOverlay {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.main-container.full-width {
    padding-left: 0 !important;
}

@media (max-width: 1023px) {
    .mobile-top-bar {
        display: flex;
    }

    .main-container {
        padding-top: 60px;
    }
}
</style>
