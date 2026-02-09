<template>
    <div class="command-page">
        <div class="container">
            <div class="header">
                <div class="flex-between">
                    <h1>Command</h1>
                    <div class="status">
                        <span class="dot"></span> Online
                    </div>
                </div>
                <p class="subtitle">STL Auto AI / v1.0.4</p>
            </div>

            <div class="terminal-content">
                <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="log.type">
                    <span class="bullet" v-if="log.type === 'system'">•</span>
                    <span class="bullet" v-else-if="log.type === 'input'">›</span>
                    <span class="bullet" v-else-if="log.type === 'success'">✓</span>
                    <p>{{ log.text }}</p>
                </div>

                <!-- Result Card Example from Reference -->
                <div class="card card-minimal animate-fade-in" v-if="showResult">
                    <div class="flex-between">
                        <div>
                            <p class="label">New Application</p>
                            <h3 style="margin-bottom: 0.25rem;">Toyota Camry</h3>
                            <p class="small-text">Just now</p>
                        </div>
                        <div class="amount-display">
                            <div class="number-medium">45 000</div>
                            <p class="small-text">USD</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="command-input-container">
                <div class="input-wrapper">
                    <input type="text" v-model="commandInput" placeholder="Type a command..."
                        @keyup.enter="sendCommand" />
                    <div class="icons">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="1.5">
                            <path d="M12 1v22M5 12h14" />
                        </svg>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="1.5">
                            <path d="M12 18.5a6.5 6.5 0 100-13 6.5 6.5 0 000 13zM12 12v3M12 9v.01" />
                        </svg>
                    </div>
                </div>
            </div>
        </div>

        <!-- Reuse Navigation -->
        <nav class="bottom-nav">
            <NuxtLink to="/dashboard" class="nav-item">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="7" height="7" rx="1" />
                    <rect x="14" y="3" width="7" height="7" rx="1" />
                    <rect x="14" y="14" width="7" height="7" rx="1" />
                    <rect x="3" y="14" width="7" height="7" rx="1" />
                </svg>
            </NuxtLink>

            <NuxtLink to="/command" class="nav-item active">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 8v8M8 12h8" />
                </svg>
            </NuxtLink>

            <NuxtLink to="/history" class="nav-item">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            </NuxtLink>

            <NuxtLink to="/plan" class="nav-item">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="4" width="18" height="18" rx="2" />
                    <path d="M16 2v4M8 2v4M3 10h18" />
                </svg>
            </NuxtLink>

            <NuxtLink to="/settings" class="nav-item">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="12" cy="12" r="3" />
                    <path
                        d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24" />
                </svg>
            </NuxtLink>
        </nav>
    </div>
</template>

<script setup lang="ts">
const commandInput = ref('')
const showResult = ref(true)

const logs = ref([
    { type: 'system', text: 'System initialized. Ready.' },
    { type: 'input', text: 'Show latest applications' },
    { type: 'success', text: 'Retrieved 5 new applications. Most recent: Toyota Camry.' }
])

const sendCommand = () => {
    if (!commandInput.value) return

    logs.value.push({ type: 'input', text: commandInput.value })

    // Fake response
    setTimeout(() => {
        logs.value.push({ type: 'system', text: 'Processing command...' })
        setTimeout(() => {
            logs.value.push({ type: 'success', text: 'Action completed successfully.' })
        }, 1000)
    }, 500)

    commandInput.value = ''
}

definePageMeta({
    layout: false
})

useHead({
    title: 'Command - STL Auto Admin'
})
</script>

<style scoped>
.command-page {
    min-height: 100vh;
    background: var(--color-bg-primary);
    padding-bottom: 8rem;
}

.header {
    padding: var(--spacing-xl) 0 var(--spacing-lg);
}

.header h1 {
    font-size: 1.75rem;
    font-weight: 200;
    margin: 0;
}

.status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: var(--color-text-secondary);
    font-weight: 300;
}

.dot {
    width: 6px;
    height: 6px;
    background: var(--color-success);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--color-success);
}

.terminal-content {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.log-entry {
    display: flex;
    gap: 1rem;
    font-size: 0.95rem;
    font-weight: 300;
}

.bullet {
    color: var(--color-text-tertiary);
    flex-shrink: 0;
}

.log-entry.input p {
    color: var(--color-text-primary);
}

.log-entry.system p {
    color: var(--color-text-secondary);
}

.log-entry.success p {
    color: var(--color-text-secondary);
}

.command-input-container {
    position: fixed;
    bottom: 80px;
    left: 0;
    right: 0;
    padding: 0 var(--spacing-lg);
    max-width: 800px;
    margin: 0 auto;
}

.input-wrapper {
    position: relative;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: 2rem;
    display: flex;
    align-items: center;
    padding: 0 1.5rem;
}

.input-wrapper input {
    width: 100%;
    background: transparent;
    border: none;
    padding: 0.875rem 0;
    color: var(--color-text-primary);
    font-size: 1rem;
    font-weight: 300;
}

.input-wrapper input:focus {
    outline: none;
}

.icons {
    display: flex;
    gap: 1rem;
    color: var(--color-text-tertiary);
}

/* Bottom Navigation Styles (Shared) */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--color-bg-card);
    border-top: 1px solid var(--color-border);
    display: flex;
    justify-content: space-around;
    padding: var(--spacing-sm) 0;
}

.nav-item {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    color: var(--color-text-secondary);
    transition: all 0.3s ease;
}

.nav-item.active {
    color: var(--color-text-primary);
    background: var(--color-text-primary);
}

.nav-item.active svg {
    stroke: var(--color-bg-primary);
}
</style>
