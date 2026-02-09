<template>
    <div class="language-switcher">
        <button class="lang-trigger" @click="isOpen = !isOpen" :title="$t('settings.language')">
            <span class="lang-code">{{ locale.toUpperCase() }}</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        </button>

        <Transition name="dropdown">
            <div v-if="isOpen" class="lang-dropdown">
                <button v-for="loc in locales" :key="loc.code" class="lang-option"
                    :class="{ active: locale === loc.code }" @click="setLocale(loc.code)">
                    <span class="lang-flag">{{ getFlagEmoji(loc.code) }}</span>
                    <span class="lang-name">{{ loc.name }}</span>
                    <svg v-if="locale === loc.code" width="16" height="16" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2.5">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                </button>
            </div>
        </Transition>
    </div>
</template>

<script setup lang="ts">
const { locale, locales, setLocale } = useI18n()
const isOpen = ref(false)

const getFlagEmoji = (code: string) => {
    const flags: Record<string, string> = {
        'ru': '🇷🇺',
        'uz': '🇺🇿',
        'en': '🇬🇧'
    }
    return flags[code] || '🌐'
}

// Close dropdown when clicking outside
onMounted(() => {
    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement
        if (!target.closest('.language-switcher')) {
            isOpen.value = false
        }
    })
})
</script>

<style scoped>
.language-switcher {
    position: relative;
}

.lang-trigger {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    color: var(--color-text-primary);
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.85rem;
    font-weight: 600;
}

.lang-trigger:hover {
    background: var(--color-bg-hover);
    border-color: var(--color-text-tertiary);
}

.lang-code {
    letter-spacing: 0.05em;
}

.lang-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    min-width: 160px;
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    z-index: 1000;
}

.lang-option {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 10px 14px;
    background: none;
    border: none;
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: all 0.15s;
    text-align: left;
    font-size: 0.9rem;
}

.lang-option:hover {
    background: var(--color-bg-hover);
    color: var(--color-text-primary);
}

.lang-option.active {
    background: var(--color-bg-hover);
    color: var(--color-success);
}

.lang-flag {
    font-size: 1.1rem;
}

.lang-name {
    flex: 1;
}

/* Dropdown animation */
.dropdown-enter-active {
    animation: dropdownIn 0.2s ease-out;
}

.dropdown-leave-active {
    animation: dropdownOut 0.15s ease-in forwards;
}

@keyframes dropdownIn {
    from {
        opacity: 0;
        transform: translateY(-8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes dropdownOut {
    from {
        opacity: 1;
        transform: translateY(0);
    }

    to {
        opacity: 0;
        transform: translateY(-8px);
    }
}
</style>
