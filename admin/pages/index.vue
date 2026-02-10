<template>
    <div class="admin-login">
        <div class="login-container">
            <div class="login-card animate-fade-in">
                <div class="logo-area">
                    <img src="/favicon.svg" alt="STL Auto" class="login-logo" />
                    <h1>STL Auto</h1>
                </div>
                <p class="subtitle">{{ $t('auth.title') }}</p>

                <div class="auth-tabs">
                    <button class="auth-tab" :class="{ active: mode === 'login' }" @click="mode = 'login'">
                        {{ $t('auth.login') }}
                    </button>
                    <button class="auth-tab" :class="{ active: mode === 'register' }" @click="mode = 'register'">
                        {{ $t('auth.register') }}
                    </button>
                </div>

                <div v-if="mode === 'login'" class="demo-hint">
                    <p>{{ $t('auth.demo') }}</p>
                </div>

                <!-- Login Form -->
                <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="login-form">
                    <div class="form-group">
                        <input id="phone" v-model="loginForm.phone" type="tel" class="input"
                            :placeholder="$t('auth.phone')" required />
                    </div>

                    <div class="form-group">
                        <input id="password" v-model="loginForm.password" type="password" class="input"
                            :placeholder="$t('auth.password')" required />
                    </div>

                    <div v-if="error" class="error-message">
                        {{ error }}
                    </div>

                    <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
                        <span v-if="loading">{{ $t('auth.signingIn') }}</span>
                        <span v-else>{{ $t('auth.signIn') }}</span>
                    </button>
                </form>

                <!-- Register Form -->
                <form v-else @submit.prevent="handleRegister" class="login-form">
                    <div class="form-row">
                        <div class="form-group">
                            <input v-model="registerForm.first_name" type="text" class="input"
                                :placeholder="$t('auth.firstName')" required />
                        </div>
                        <div class="form-group">
                            <input v-model="registerForm.last_name" type="text" class="input"
                                :placeholder="$t('auth.lastName')" required />
                        </div>
                    </div>

                    <div class="form-group">
                        <input v-model="registerForm.phone" type="tel" class="input" :placeholder="$t('auth.phone')"
                            required />
                    </div>

                    <div class="form-group">
                        <input v-model="registerForm.email" type="email" class="input"
                            :placeholder="$t('auth.email')" />
                    </div>

                    <div class="form-group">
                        <input v-model="registerForm.password" type="password" class="input"
                            :placeholder="$t('auth.passwordHint')" minlength="6" required />
                    </div>

                    <div v-if="error" class="error-message">
                        {{ error }}
                    </div>

                    <div v-if="successMsg" class="success-message">
                        {{ successMsg }}
                    </div>

                    <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
                        <span v-if="loading">{{ $t('auth.signingUp') }}</span>
                        <span v-else>{{ $t('auth.signUp') }}</span>
                    </button>
                </form>

            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const router = useRouter()
const { login, register, getCurrentUser } = useApi()
const { t } = useI18n()

const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const error = ref('')
const successMsg = ref('')

const loginForm = ref({
    phone: '',
    password: ''
})

const registerForm = ref({
    phone: '',
    password: '',
    first_name: '',
    last_name: '',
    email: ''
})

const handleLogin = async () => {
    loading.value = true
    error.value = ''
    successMsg.value = ''

    try {
        await login(loginForm.value.phone.trim(), loginForm.value.password)
        const user: any = await getCurrentUser()

        if (user && user.role === 'client') {
            error.value = t('auth.errorAdmin')
            return
        }

        router.push('/dashboard')
    } catch (err: any) {
        console.error('Login error:', err)
        if (err.data && err.data.detail) {
            if (Array.isArray(err.data.detail)) {
                // Pydantic validation error is an array of objects
                error.value = err.data.detail.map((e: any) => `${e.loc[1] || e.loc[0]}: ${e.msg}`).join('; ')
            } else {
                error.value = err.data.detail
            }
        } else {
            error.value = t('auth.errorGeneric')
        }
    } finally {
        loading.value = false
    }
}

const handleRegister = async () => {
    loading.value = true
    error.value = ''
    successMsg.value = ''

    try {
        const payload = { ...registerForm.value, phone: registerForm.value.phone.trim() }
        await register(payload)
        successMsg.value = t('auth.success')

        // Pre-fill login
        loginForm.value.phone = registerForm.value.phone.trim()
        loginForm.value.password = registerForm.value.password

        // Auto login or switch to login tab
        // Let's try auto login for convenience
        await handleLogin()

    } catch (err: any) {
        console.error('Registration error:', err)
        if (err.data && err.data.detail) {
            if (Array.isArray(err.data.detail)) {
                error.value = err.data.detail.map((e: any) => `${e.loc[1] || e.loc[0]}: ${e.msg}`).join('; ')
            } else {
                error.value = err.data.detail
            }
        } else {
            error.value = t('auth.errorGeneric')
        }
    } finally {
        loading.value = false
    }
}

definePageMeta({
    layout: false
})

useHead({
    title: 'STL Auto Admin'
})
</script>

<style scoped>
.admin-login {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-bg-primary);
    padding: var(--spacing-lg);
}

.login-container {
    width: 100%;
    max-width: 420px;
}

.login-card {
    text-align: center;
    background: var(--color-bg-secondary);
    /* Added background for card look */
    padding: 2.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--color-border);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.logo-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    margin-bottom: 8px;
}

.login-logo {
    width: 64px;
    height: 64px;
    filter: drop-shadow(0 4px 12px rgba(79, 70, 229, 0.3));
}

.login-card h1 {
    font-size: 2rem;
    font-weight: 200;
    margin-bottom: var(--spacing-xs);
    letter-spacing: -0.02em;
    color: var(--color-text-primary);
}

.subtitle {
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-lg);
    font-size: 0.95rem;
    font-weight: 300;
}

.auth-tabs {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--color-border);
    padding-bottom: 0.5rem;
}

.auth-tab {
    flex: 1;
    background: none;
    border: none;
    color: var(--color-text-secondary);
    padding: 0.5rem;
    cursor: pointer;
    font-size: 0.95rem;
    transition: all 0.2s;
    border-bottom: 2px solid transparent;
}

.auth-tab.active {
    color: var(--color-primary);
    border-bottom-color: var(--color-primary);
    font-weight: 500;
}

.demo-hint {
    background: rgba(var(--color-primary-rgb), 0.1);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
}

.demo-hint p {
    color: var(--color-primary);
    font-size: 0.85rem;
    margin: 0;
    font-family: 'Courier New', monospace;
    font-weight: 500;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.form-row {
    display: flex;
    gap: var(--spacing-md);
}

.form-row .form-group {
    flex: 1;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.input {
    width: 100%;
    padding: 0.8rem 1rem;
    background: var(--color-bg-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    color: var(--color-text-primary);
    transition: all 0.2s;
}

.input:focus {
    border-color: var(--color-primary);
    outline: none;
    box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

.error-message {
    padding: var(--spacing-sm);
    background: rgba(255, 0, 85, 0.1);
    border: 1px solid var(--color-error);
    border-radius: var(--radius-sm);
    color: var(--color-error);
    text-align: center;
    font-size: 0.85rem;
}

.success-message {
    padding: var(--spacing-sm);
    background: rgba(0, 255, 157, 0.1);
    border: 1px solid var(--color-success);
    border-radius: var(--radius-sm);
    color: var(--color-success);
    text-align: center;
    font-size: 0.85rem;
}

.btn-full {
    width: 100%;
    margin-top: var(--spacing-sm);
    padding: 0.9rem;
    font-weight: 500;
}
</style>
