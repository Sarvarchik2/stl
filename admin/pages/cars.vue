<template>
    <div class="inventory-page animate-fade-in">
        <header class="page-header">
            <div class="container">
                <div class="flex-between items-end">
                    <div>
                        <h1 class="text-thin">{{ $t('cars.title') }}</h1>
                        <p class="text-secondary text-light">{{ $t('cars.subtitle') }}</p>
                    </div>
                    <div class="header-actions flex gap-4">
                        <div class="view-switcher-minimal">
                            <button class="switcher-btn" :class="{ active: viewMode === 'grid' }"
                                @click="viewMode = 'grid'">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <rect x="3" y="3" width="7" height="7" />
                                    <rect x="14" y="3" width="7" height="7" />
                                    <rect x="14" y="14" width="7" height="7" />
                                    <rect x="3" y="14" width="7" height="7" />
                                </svg>
                            </button>
                            <button class="switcher-btn" :class="{ active: viewMode === 'list' }"
                                @click="viewMode = 'list'">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <line x1="8" y1="6" x2="21" y2="6" />
                                    <line x1="8" y1="12" x2="21" y2="12" />
                                    <line x1="8" y1="18" x2="21" y2="18" />
                                    <circle cx="3" cy="6" r="1" />
                                    <circle cx="3" cy="12" r="1" />
                                    <circle cx="3" cy="18" r="1" />
                                </svg>
                            </button>
                        </div>
                        <button v-if="hasRole('manager')" class="btn btn-primary btn-sm shadow-lg" @click="openModal()">
                            <span class="mr-2">+</span> {{ $t('cars.add') }}
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <!-- Search and Filter Bar -->
            <div class="controls-bar-dark mb-8 card card-minimal py-3 px-5">
                <div class="flex gap-6 items-center flex-wrap">
                    <div class="search-wrap-minimal flex-grow max-w-lg">
                        <input v-model="searchQuery" type="text" :placeholder="$t('cars.search')" class="input-clean"
                            style="width: 100%;">
                    </div>
                    <div class="filter-wrap">
                        <select v-model="statusFilter" class="select-clean">
                            <option value="all">{{ $t('applications.filters.all') }}</option>
                            <option value="available">{{ $t('cars.status.available') }}</option>
                            <option value="sold">{{ $t('cars.status.sold') }}</option>
                            <option value="reserved">{{ $t('cars.status.reserved') }}</option>
                        </select>
                    </div>
                    <div class="flex-grow"></div>
                    <div class="text-tertiary smaller-text font-bold tracking-widest opacity-50">
                        {{ loading ? $t('common.loading').toUpperCase() : `${filteredCars.length}
                        ${$t('common.objects').toUpperCase()}` }}
                    </div>
                </div>
            </div>

            <!-- Grid View -->
            <div v-if="viewMode === 'grid'" class="grid-view animate-slide-up">
                <div class="cars-grid gap-8">
                    <div v-if="loading && cars.length === 0" v-for="i in 6" :key="i" class="skeleton-card"></div>

                    <div v-else v-for="car in filteredCars" :key="car.id" class="car-pill-card clickable-row"
                        @click="openModal(car)">
                        <div class="car-visual-area">
                            <img v-if="car.image_url" :src="car.image_url" class="car-thumb" alt="Car thumbnail">
                            <div v-else class="car-placeholder">
                                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="1" class="opacity-10">
                                    <path
                                        d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9L18.7 7h-1.2l-1.3-4.4c-.1-.3-.4-.6-.7-.6H8.5c-.3 0-.6.3-.7.6L6.5 7H5.3l-1.8 11L6 13c0 .6.4 1 1 1h2m10 0v2c0 .6-.4 1-1 1H8c-.6 0-1-.4-1-1v-2m10 0H7" />
                                </svg>
                            </div>
                            <div class="status-pill" :class="car.status || 'available'">
                                {{ translateStatus(car.status || 'available') }}
                            </div>
                        </div>
                        <div class="car-details-area p-5">
                            <div class="flex-between mb-1">
                                <span class="smaller-text text-tertiary font-bold">{{ car.year }} {{
                                    $t('cars.yearShort') }}</span>
                                <span class="smaller-text text-secondary">{{ (car.mileage || 0).toLocaleString() }}
                                    {{ $t('cars.km') }}</span>
                            </div>
                            <h3 class="car-title text-white">{{ car.brand }} {{ car.model }}</h3>
                            <div class="flex-between items-center mt-auto">
                                <div class="price-box">
                                    <div class="text-accent font-bold text-lg">
                                        {{ (car.final_price_usd || (car.source_price_usd * 1.15)).toLocaleString() }}
                                        <span class="smaller-text font-normal text-tertiary">USD</span>
                                    </div>
                                </div>
                                <div class="card-actions" @click.stop v-if="hasRole('manager')">
                                    <button class="btn-circle-action" @click="openModal(car)">
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                                            stroke="currentColor" stroke-width="2">
                                            <path
                                                d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- List View -->
            <div v-else class="list-view animate-fade-in">
                <div class="card card-minimal no-padding overflow-hidden">
                    <div class="table-responsive">
                        <table class="admin-table">
                            <thead>
                                <tr>
                                    <th class="pl-8">{{ $t('cars.car') }}</th>
                                    <th>{{ $t('cars.specs') }}</th>
                                    <th>{{ $t('cars.mileage') }}</th>
                                    <th>{{ $t('cars.sourcePrice') }}</th>
                                    <th>{{ $t('cars.price') }}</th>
                                    <th>{{ $t('common.status') }}</th>
                                    <th class="text-right pr-8">{{ $t('common.actions') }}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-if="loading && cars.length === 0" v-for="i in 5" :key="i">
                                    <td colspan="7" class="py-10 text-center text-tertiary smaller-text">{{
                                        $t('common.loading') }}</td>
                                </tr>
                                <tr v-else v-for="car in filteredCars" :key="car.id" class="premium-row clickable-row"
                                    @click="openModal(car)">
                                    <td class="pl-8 py-5">
                                        <div class="flex items-center gap-4">
                                            <div class="table-thumb-wrap">
                                                <img v-if="car.image_url" :src="car.image_url" class="table-thumb">
                                                <div v-else class="table-thumb-placeholder"></div>
                                            </div>
                                            <div>
                                                <div class="font-bold text-white">{{ car.brand }} {{ car.model }}</div>
                                                <div class="smaller-text text-tertiary">VIN: {{ car.vin || '---' }}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <div class="smaller-text text-secondary font-medium">{{ car.engine || '---' }}
                                        </div>
                                        <div class="smaller-text text-tertiary">{{ car.year }} г.в. | {{
                                            car.exterior_color || '---' }}</div>
                                    </td>
                                    <td>
                                        <div class="font-medium text-white">{{ (car.mileage || 0).toLocaleString() }} км
                                        </div>
                                    </td>
                                    <td>
                                        <div class="text-secondary smaller-text">{{
                                            car.source_price_usd?.toLocaleString() }} USD</div>
                                    </td>
                                    <td>
                                        <div class="font-bold text-accent">{{ (car.final_price_usd ||
                                            (car.source_price_usd *
                                                1.15)).toLocaleString() }} USD</div>
                                    </td>
                                    <td><span class="badge" :class="car.status || 'available'">{{
                                        translateStatus(car.status || 'available') }}</span></td>
                                    <td class="text-right pr-8 py-5" @click.stop v-if="hasRole('manager')">
                                        <div class="flex justify-end gap-2">
                                            <button class="btn btn-sm btn-outline btn-icon-only"
                                                @click="openModal(car)">
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                                                    stroke="currentColor" stroke-width="2">
                                                    <path
                                                        d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                                                </svg>
                                            </button>
                                            <button class="btn btn-sm btn-icon-only text-error"
                                                @click="handleDelete(car.id)"
                                                style="background: rgba(239, 68, 68, 0.05);">
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                                                    stroke="currentColor" stroke-width="2">
                                                    <polyline points="3 6 5 6 21 6" />
                                                    <path d="M19 6L18.1 19.4a2 2 0 01-2 1.6H7.9a2 2 0 01-2-1.6L5 6" />
                                                </svg>
                                            </button>
                                        </div>
                                    </td>
                                    <td v-else class="text-right pr-8 py-5 text-tertiary smaller-text italic">
                                        {{ $t('common.viewOnly') }}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <p class="smaller-text text-tertiary mt-6 opacity-30 italic">
                * {{ $t('cars.priceNote') }}
            </p>

            <div class="spacer"></div>
        </div>

        <!-- Car Form Modal - Expanded for Full Details -->
        <Teleport to="body">
            <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
                <div class="modal-card-expanded animate-scale-in">
                    <header class="modal-header-minimal flex-between items-start mb-8">
                        <div>
                            <h2 class="text-thin m-0 text-white">{{ modalTitle }}</h2>
                            <p class="text-secondary smaller-text">{{ $t('cars.modal.subtitle') }}</p>
                        </div>
                        <button class="btn-close-minimal" @click="showModal = false">&times;</button>
                    </header>

                    <div class="modal-tabs mb-6">
                        <button v-for="tab in tabs" :key="tab.id" class="tab-btn"
                            :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id">
                            {{ tab.label }}
                        </button>
                    </div>

                    <div class="modal-body-scrollable">
                        <!-- Основная информация -->
                        <div v-show="activeTab === 'general'" class="grid gap-6">
                            <div class="grid grid-3 gap-4">
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.brand') }}</label>
                                    <input v-model="form.brand" type="text" class="input input-sm"
                                        placeholder="e.g. BMW">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.model') }}</label>
                                    <input v-model="form.model" type="text" class="input input-sm"
                                        placeholder="e.g. X5">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.trim') }}</label>
                                    <input v-model="form.trim" type="text" class="input input-sm"
                                        placeholder="e.g. M Sport">
                                </div>
                            </div>

                            <div class="grid grid-3 gap-4">
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.year') }}</label>
                                    <input v-model.number="form.year" type="number" class="input input-sm">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.mileage') }}</label>
                                    <input v-model.number="form.mileage" type="number" class="input input-sm">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.vin') }}</label>
                                    <input v-model="form.vin" type="text" class="input input-sm"
                                        placeholder="17-char code">
                                </div>
                            </div>

                            <div class="grid grid-2 gap-4">
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.sourcePrice') }}</label>
                                    <input v-model.number="form.source_price_usd" type="number" class="input input-sm">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('common.status') }}</label>
                                    <select v-model="form.status" class="input input-sm">
                                        <option value="available">{{ $t('cars.status.available') }}</option>
                                        <option value="sold">{{ $t('cars.status.sold') }}</option>
                                        <option value="reserved">{{ $t('cars.status.reserved') }}</option>
                                    </select>
                                </div>
                            </div>

                            <div class="grid grid-2 gap-4">
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.bodyType') }}</label>
                                    <input v-model="form.body_type" type="text" class="input input-sm">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.engine') }}</label>
                                    <input v-model="form.engine" type="text" class="input input-sm">
                                </div>
                            </div>
                        </div>

                        <!-- Технические детали -->
                        <div v-show="activeTab === 'specs'" class="grid gap-6">
                            <div class="grid grid-2 gap-4">
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.transmission') }}</label>
                                    <input v-model="form.transmission" type="text" class="input input-sm">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.drivetrain') }}</label>
                                    <input v-model="form.drivetrain" type="text" class="input input-sm">
                                </div>
                            </div>
                            <div class="grid grid-2 gap-4">
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.exteriorColor') }}</label>
                                    <input v-model="form.exterior_color" type="text" class="input input-sm">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.interiorColor') }}</label>
                                    <input v-model="form.interior_color" type="text" class="input input-sm">
                                </div>
                            </div>
                            <div class="grid grid-2 gap-4">
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.fuelType') }}</label>
                                    <input v-model="form.fuel_type" type="text" class="input input-sm">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.mpg') }}</label>
                                    <div class="flex gap-2">
                                        <input v-model.number="form.mpg_city" type="number" class="input input-sm"
                                            :placeholder="$t('cars.mpgCity')">
                                        <input v-model.number="form.mpg_highway" type="number" class="input input-sm"
                                            :placeholder="$t('cars.mpgHighway')">
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="micro-label mb-2">{{ $t('cars.features') }} ({{ $t('cars.commaSeparated')
                                }})</label>
                                <textarea v-model="featuresString" class="input input-sm" rows="3"
                                    :placeholder="$t('cars.featuresPlaceholder')"></textarea>
                            </div>
                        </div>

                        <!-- Медиа и Фото -->
                        <div v-show="activeTab === 'media'" class="grid gap-6">
                            <div class="form-group">
                                <label class="micro-label mb-2">{{ $t('cars.mainImage') }}</label>
                                <input v-model="form.image_url" type="text" class="input input-sm"
                                    placeholder="https://...">
                            </div>
                            <div class="form-group">
                                <label class="micro-label mb-2">{{ $t('cars.gallery') }}</label>
                                <textarea v-model="photosString" class="input input-sm" rows="8"
                                    :placeholder="$t('cars.galleryPlaceholder')"></textarea>
                            </div>
                            <!-- Image Grid Preview -->
                            <div v-if="form.photos?.length" class="photos-preview-grid">
                                <div v-for="(photo, idx) in form.photos" :key="idx" class="photo-preview-item">
                                    <img :src="photo" class="photo-preview-img">
                                </div>
                            </div>
                        </div>

                        <!-- Дилер и Локация -->
                        <div v-show="activeTab === 'dealer'" class="grid gap-6">
                            <div class="form-group">
                                <label class="micro-label mb-2">{{ $t('cars.dealer') }}</label>
                                <input v-model="form.dealer" type="text" class="input input-sm">
                            </div>
                            <div class="grid grid-2 gap-4">
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.locationCity') }}</label>
                                    <input v-model="form.location_city" type="text" class="input input-sm">
                                </div>
                                <div class="form-group">
                                    <label class="micro-label mb-2">{{ $t('cars.locationState') }}</label>
                                    <input v-model="form.location_state" type="text" class="input input-sm">
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="micro-label mb-2">{{ $t('cars.sourceUrl') }}</label>
                                <input v-model="form.source_url" type="text" class="input input-sm"
                                    placeholder="https://cars.com/...">
                            </div>
                        </div>
                    </div>

                    <footer class="modal-footer-minimal flex gap-3 mt-8">
                        <button class="btn btn-sm flex-grow font-medium" @click="showModal = false">{{
                            $t('common.close') }}</button>
                        <button v-if="hasRole('manager')" class="btn btn-primary btn-sm flex-grow font-bold"
                            @click="saveCar">{{ $t('common.save') }}</button>
                    </footer>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

const { t } = useI18n()
const toast = useToast()

const { getCars, createCar, updateCar, deleteCar, hasRole } = useApi()

const cars = ref<any[]>([])
const loading = ref(true)
const showModal = ref(false)
const searchQuery = ref('')
const statusFilter = ref('all')
const editingId = ref<string | null>(null)
const viewMode = ref<'grid' | 'list'>('grid')
const activeTab = ref('general')

const modalTitle = computed(() => editingId.value ? t('cars.modal.edit') : t('cars.modal.add'))

const tabs = computed(() => [
    { id: 'general', label: t('cars.modal.tabs.general') },
    { id: 'specs', label: t('cars.modal.tabs.specs') },
    { id: 'media', label: t('cars.modal.tabs.media') },
    { id: 'dealer', label: t('cars.modal.tabs.dealer') }
])

const form = ref<any>({
    brand: '',
    make: '',
    model: '',
    year: 2024,
    trim: '',
    body_type: '',
    mileage: 0,
    exterior_color: '',
    interior_color: '',
    transmission: '',
    drivetrain: '',
    fuel_type: '',
    engine: '',
    mpg_city: null,
    mpg_highway: null,
    vin: '',
    source_price_usd: 0,
    dealer: '',
    location_city: '',
    location_state: '',
    source_url: '',
    image_url: '',
    photos: [],
    features: [],
    status: 'available'
})

// Helper for textarea syncing
const photosString = ref('')
const featuresString = ref('')

watch(photosString, (val) => {
    form.value.photos = val.split('\n').map(l => l.trim()).filter(l => l.length > 0)
})

watch(featuresString, (val) => {
    form.value.features = val.split(',').map(s => s.trim()).filter(s => s.length > 0)
})

const fetchCars = async () => {
    loading.value = true
    try {
        const res: any = await getCars()
        cars.value = res.items || []
    } catch (err) {
        console.error('Error fetching cars:', err)
        cars.value = []
    } finally {
        loading.value = false
    }
}

const filteredCars = computed(() => {
    return cars.value.filter(c => {
        const matchesStatus = statusFilter.value === 'all' || c.status === statusFilter.value
        const brandModelVin = `${c.brand || ''} ${c.model || ''} ${c.vin || ''}`.toLowerCase()
        const matchesSearch = !searchQuery.value ||
            brandModelVin.includes(searchQuery.value.toLowerCase()) ||
            c.year?.toString().includes(searchQuery.value)
        return matchesStatus && matchesSearch
    })
})

const openModal = (car?: any) => {
    console.log('openModal called with:', car)
    activeTab.value = 'general'
    if (car) {
        editingId.value = car.id
        // Load all fields safely
        try {
            form.value = JSON.parse(JSON.stringify(car)) // Deep copy safety

            // Handle photos safely
            let photos = car.photos
            if (typeof photos === 'string') {
                // Try parsing if it's a JSON string, otherwise treat as single URL
                try { photos = JSON.parse(photos) } catch (e) { photos = [photos] }
            }
            if (!Array.isArray(photos)) photos = []

            // Handle features safely
            let features = car.features
            if (typeof features === 'string') {
                try { features = JSON.parse(features) } catch (e) { features = [features] }
            }
            if (!Array.isArray(features)) features = []

            photosString.value = photos.join('\n')
            featuresString.value = features.join(', ')

            // Ensure form has arrays
            form.value.photos = photos
            form.value.features = features
        } catch (e) {
            console.error('Error preparing form data:', e)
            toast.error(t('common.error'), t('cars.dataError'))
        }
    } else {
        editingId.value = null
        form.value = {
            brand: '', model: '', year: 2024, mileage: 0, status: 'available',
            source_price_usd: 0, trim: '', body_type: '', exterior_color: '',
            interior_color: '', engine: '', transmission: '', photos: [], features: []
        }
        photosString.value = ''
        featuresString.value = ''
    }
    showModal.value = true
}

const saveCar = async () => {
    try {
        // Ensure make is same as brand if empty
        if (!form.value.make) form.value.make = form.value.brand

        if (editingId.value) {
            await updateCar(editingId.value, form.value)
        } else {
            await createCar(form.value)
        }
        showModal.value = false
        fetchCars()
    } catch (err: any) {
        toast.error(t('common.error'), err?.data?.detail || t('cars.saveError'))
    }
}

const handleDelete = async (id: string) => {
    if (confirm(t('common.confirmDelete'))) {
        try {
            await deleteCar(id)
            fetchCars()
        } catch (err: any) {
            toast.error(t('common.error'), err?.data?.detail || t('cars.deleteError'))
        }
    }
}

const translateStatus = (s: string) => {
    return t(`cars.status.${s?.toLowerCase()}`)
}

onMounted(fetchCars)
definePageMeta({ layout: false })
</script>

<style scoped>
.page-header {
    padding: var(--spacing-xl) 0 var(--spacing-lg);
}

.view-switcher-minimal {
    display: flex;
    background: var(--color-bg-secondary);
    padding: 3px;
    border-radius: 8px;
    border: 1px solid var(--color-border);
}

.switcher-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    border-radius: 6px;
    color: var(--color-text-tertiary);
    cursor: pointer;
    transition: all 0.2s ease;
}

.switcher-btn.active {
    background: var(--color-bg-primary);
    color: var(--color-text-primary);
}

.controls-bar-dark {
    background: rgba(255, 255, 255, 0.02);
    border-color: var(--color-border);
}

.input-clean {
    background: transparent;
    border: none;
    color: #fff;
    font-size: 0.85rem;
    outline: none;
}

.select-clean {
    background: transparent;
    border: none;
    color: var(--color-text-secondary);
    font-size: 0.85rem;
    outline: none;
    cursor: pointer;
}

/* Grid View Improvements */
.cars-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 2rem;
}

.car-pill-card {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    display: flex;
    flex-direction: column;
    cursor: pointer;
    position: relative;
    height: 100%;
}

.car-pill-card:hover {
    transform: translateY(-5px);
    border-color: var(--color-text-tertiary);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
}

.car-pill-card:hover .car-visual-area img {
    transform: scale(1.05);
}

.car-visual-area {
    height: 200px;
    background: radial-gradient(circle at center, var(--color-bg-hover), var(--color-bg-secondary));
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    border-bottom: 1px solid var(--color-border);
    overflow: hidden;
    padding: 1rem;
}

.car-thumb {
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: transform 0.5s ease;
    filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.3));
}

.status-pill {
    position: absolute;
    top: 0.75rem;
    left: 0.75rem;
    right: auto;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 6px;
    backdrop-filter: blur(12px);
    background: rgba(0, 0, 0, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    z-index: 2;
    letter-spacing: 0.05em;
}

.status-pill.available {
    color: var(--color-success);
    border-color: rgba(16, 185, 129, 0.3);
}

.status-pill.reserved {
    color: #f59e0b;
    border-color: rgba(245, 158, 11, 0.3);
}

.status-pill.sold {
    color: var(--color-text-tertiary);
}

.car-details-area {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

.car-title {
    font-size: 1.1rem;
    line-height: 1.4;
    font-weight: 400;
    margin-bottom: 0.5rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    height: 3.2em;
    /* Ensure consistent height for 2 lines */
}

.price-box {
    margin-top: auto;
}

.btn-circle-action {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    color: var(--color-text-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-circle-action:hover {
    background: var(--color-text-primary);
    color: var(--color-bg-primary);
    transform: rotate(15deg);
}

/* Modal Overlay & Animation */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(8px);
    z-index: 2000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    animation: fadeIn 0.2s ease-out;
}

.animate-scale-in {
    animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.95) translateY(10px);
    }

    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

/* List View Improvements */
.table-thumb-wrap {
    width: 60px;
    height: 40px;
    border-radius: 6px;
    overflow: hidden;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    display: flex;
    align-items: center;
    justify-content: center;
}

.table-thumb {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* Expanded Modal Styling */
.modal-card-expanded {
    background: var(--color-bg-primary);
    width: 100%;
    max-width: 800px;
    padding: 2.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--color-border);
    box-shadow: 0 40px 100px rgba(0, 0, 0, 0.7);
    max-height: 90vh;
    display: flex;
    flex-direction: column;
}

.modal-body-scrollable {
    overflow-y: auto;
    padding-right: 0.5rem;
    flex: 1;
}

.modal-tabs {
    display: flex;
    gap: 1.5rem;
    border-bottom: 1px solid var(--color-border);
    padding-bottom: 0.5rem;
}

.tab-btn {
    background: transparent;
    border: none;
    color: var(--color-text-tertiary);
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding-bottom: 0.5rem;
    cursor: pointer;
    position: relative;
    transition: color 0.2s;
}

.tab-btn.active {
    color: var(--color-text-primary);
}

.tab-btn.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--color-accent);
}

.photos-preview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
    margin-top: 1rem;
}

.photo-preview-item {
    aspect-ratio: 4/3;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--color-border);
}

.photo-preview-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.btn-close-minimal {
    background: transparent;
    border: none;
    color: var(--color-text-tertiary);
    font-size: 1.5rem;
    cursor: pointer;
    line-height: 1;
}

.micro-label {
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--color-text-tertiary);
    display: block;
}

textarea.input {
    resize: vertical;
}

.spacer {
    height: 8rem;
}

@media (max-width: 768px) {
    .modal-card-expanded {
        padding: 1.5rem;
        max-width: 95%;
    }

    .grid-3 {
        grid-template-columns: 1fr;
    }

    .modal-tabs {
        overflow-x: auto;
        white-space: nowrap;
    }
}
</style>
