<template>
    <div class="applications-page animate-fade-in">
        <header class="page-header">
            <div class="container">
                <div class="flex-between applications-header">
                    <div class="header-info">
                        <h1 class="text-thin">{{ $t('applications.title') }}</h1>
                        <p class="text-secondary text-light">{{ $t('applications.subtitle') }}</p>
                    </div>
                    <div class="header-actions">
                        <div class="flex items-center gap-4">
                            <div class="search-wrap">
                                <input v-model="searchQuery" type="text"
                                    :placeholder="$t('applications.createModal.searchClient')"
                                    class="input input-minimal search-input-responsive">
                            </div>
                            <button class="btn btn-primary btn-sm shadow-sm" @click="showCreateModal = true">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2" style="margin-right: 8px;">
                                    <line x1="12" y1="5" x2="12" y2="19" />
                                    <line x1="5" y1="12" x2="19" y2="12" />
                                </svg>
                                {{ $t('applications.createModal.createButton') }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <!-- Personal Performance Stats -->
            <div v-if="dashboardStats?.personal_performance && dashboardStats.personal_performance.count > 0 && !hasRole('admin')"
                class="mb-6 animate-fade-in">
                <div class="glass-card p-5 border-accent-light flex items-center justify-between shadow-sm">
                    <div class="flex items-center gap-4">
                        <div class="p-3 bg-accent/10 rounded-xl text-accent">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                                <polyline points="22 4 12 14.01 9 11.01"></polyline>
                            </svg>
                        </div>
                        <div>
                            <p class="text-tertiary smaller-text font-bold uppercase tracking-wider mb-1">
                                {{ dashboardStats.personal_performance.label === 'processed' ?
                                    $t('dashboard.processed') : $t('dashboard.delivered') }}
                            </p>
                            <h2 class="m-0 text-primary font-black">{{ dashboardStats.personal_performance.count }}</h2>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="badge badge-accent mb-2">{{ $t('dashboard.myPerformance') }}</span>
                        <p class="smaller-text text-tertiary">{{ $t('dashboard.allTimeResults') }}</p>
                    </div>
                </div>
            </div>

            <!-- Quick Filter Chips -->
            <div class="filters-bar mb-8 overflow-x-auto py-2">
                <div class="flex gap-3">
                    <button v-for="f in filterStatuses" :key="f.key" class="filter-chip-premium"
                        :class="{ active: activeFilter === f.key }" @click="activeFilter = f.key">
                        {{ f.label }}
                    </button>
                </div>
            </div>

            <!-- Main Applications Table -->
            <div class="card no-padding overflow-hidden border-light shadow-sm bg-white">
                <div class="table-responsive">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th class="pl-8">{{ $t('common.date') }}</th>
                                <th>{{ $t('applications.createModal.client') }}</th>
                                <th>{{ $t('applications.createModal.selectCar') }}</th>
                                <th>{{ $t('cars.price') }}</th>
                                <th>{{ $t('applications.operator') }}</th>
                                <th>{{ $t('common.status') }}</th>
                                <th class="text-right pr-8">{{ $t('common.actions') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="loading" v-for="i in 5" :key="i">
                                <td colspan="7" class="py-12 text-center text-tertiary smaller-text">{{
                                    $t('common.loading') }}</td>
                            </tr>
                            <tr v-else v-for="app in filteredApplications" :key="app.id"
                                class="clickable-row premium-row" @click="openDetail(app)">
                                <td class="pl-8 py-5">
                                    <div class="text-tertiary smaller-text font-medium">{{ formatDate(app.created_at) }}
                                    </div>
                                </td>
                                <td>
                                    <div class="font-bold text-primary">{{ app.client_first_name }} {{
                                        app.client_last_name }}</div>
                                    <div class="smaller-text text-tertiary font-medium">{{ app.client_phone }}</div>
                                </td>
                                <td>
                                    <div class="text-secondary font-medium">{{ app.car_brand }} {{ app.car_model }}
                                    </div>
                                </td>
                                <td>
                                    <div class="text-primary font-bold">{{ app.final_price?.toLocaleString() }}</div>
                                    <div class="smaller-text text-tertiary">USD</div>
                                </td>
                                <td>
                                    <div class="operator-badge-minimal" :class="{ 'assigned': app.operator_id }">
                                        {{ getOperatorName(app.operator_id) }}
                                    </div>
                                </td>
                                <td><span class="badge" :class="app.status">{{ translateStatus(app.status) }}</span>
                                </td>
                                <td class="text-right pr-8 py-5" @click.stop>
                                    <button class="btn btn-icon-only btn-ghost hover-accent" @click="openDetail(app)">
                                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
                                            stroke="currentColor" stroke-width="2">
                                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                                            <circle cx="12" cy="12" r="3" />
                                        </svg>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Pagination Dummy -->
            <div class="flex-center mt-12 gap-3">
                <button class="btn btn-sm btn-outline btn-minimal" disabled>{{ $t('common.back') }}</button>
                <button class="btn btn-sm btn-primary shadow-sm" style="min-width: 40px;">1</button>
                <button class="btn btn-sm btn-outline btn-minimal" disabled>{{ $t('common.next') }}</button>
            </div>

            <div class="spacer"></div>
        </div>

        <!-- Create Application Modal -->
        <Teleport to="body">
            <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
                <div class="modal-panel animate-slide-in shadow-2xl">
                    <div class="modal-header-premium">
                        <h3 class="m-0 text-thin">{{ $t('applications.createModal.title') }}</h3>
                        <button class="btn btn-icon-only btn-ghost" @click="showCreateModal = false">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M18 6L6 18M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <div class="modal-body-premium">
                        <!-- Car Search & Select -->
                        <div class="form-group-premium mb-6">
                            <label class="section-label mb-2">{{ $t('applications.createModal.selectCar') }} <span
                                    class="text-error">*</span></label>
                            <div class="searchable-select-wrap">
                                <input v-model="carSearchQuery" type="text"
                                    :placeholder="$t('applications.createModal.searchCar')"
                                    class="input input-minimal w-full mb-2">
                                <div class="options-list-premium custom-scrollbar">
                                    <div v-for="car in filteredCars" :key="car.id" class="option-item-premium"
                                        :class="{ selected: createForm.car_id === car.id }"
                                        @click="createForm.car_id = car.id">
                                        <div class="flex-between">
                                            <div>
                                                <div class="font-bold text-primary">{{ car.brand }} {{ car.model }}
                                                </div>
                                                <div class="smaller-text text-tertiary">{{ car.year }} {{
                                                    $t('cars.yearShort') }} — {{
                                                        (car.final_price_usd || (car.source_price_usd *
                                                            1.2)).toLocaleString() }}$
                                                </div>
                                            </div>
                                            <div v-if="createForm.car_id === car.id" class="text-success">✓</div>
                                        </div>
                                    </div>
                                </div>
                                <div v-if="filteredCars.length === 0"
                                    class="p-4 text-center text-tertiary smaller-text">
                                    {{ $t('common.noData') }}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Client Search & Details -->
                    <div class="form-group-premium mb-6">
                        <label class="section-label mb-2">{{ $t('applications.createModal.client') }} <span
                                class="text-error">*</span></label>
                        <div class="relative">
                            <input v-model="clientSearchQuery" type="text"
                                :placeholder="$t('applications.createModal.searchClient')"
                                class="input input-minimal w-full mb-3 bg-dim shadow-inner">

                            <!-- Search Results Dropdown -->
                            <!-- Search Results Dropdown -->
                            <div v-if="clientSearchQuery.length >= 3" class="client-results-dropdown shadow-2xl">
                                <div v-if="clientSearchLoading" class="p-4 text-center text-secondary">
                                    {{ $t('common.searching') }}
                                </div>
                                <template v-else>
                                    <!-- Real Results -->
                                    <div v-for="client in clientSearchResults" :key="client.id"
                                        class="client-result-item" @click="selectExistingClient(client)">
                                        <div class="flex items-center gap-3">
                                            <div class="user-avatar-mini">{{ client.first_name[0] }}</div>
                                            <div>
                                                <div class="font-bold text-primary">{{ client.first_name }} {{
                                                    client.last_name }}</div>
                                                <div class="smaller-text text-tertiary">{{ client.phone }}</div>
                                            </div>
                                            <div class="ml-auto text-tertiary smaller-text italic opacity-60">{{
                                                $t('applications.sources.admin') }}</div>
                                        </div>
                                    </div>

                                    <!-- Virtual "Create New" Result -->
                                    <div class="client-result-item create-new-hint border-top"
                                        @click="clientSearchResults = []; clientSearchQuery = ''">
                                        <div class="flex items-center gap-3">
                                            <div class="user-avatar-mini bg-accent">+</div>
                                            <div>
                                                <div class="font-bold text-accent">{{ $t('users.create.title') }}</div>
                                                <div class="smaller-text text-tertiary">{{ clientSearchQuery }}
                                                </div>
                                            </div>
                                            <div class="ml-auto text-accent smaller-text font-bold">{{
                                                $t('common.new').toUpperCase() }}</div>
                                        </div>
                                    </div>
                                </template>
                            </div>
                        </div>

                        <div class="lead-details-grid grid grid-2 gap-4">
                            <div class="detail-input-wrap">
                                <label class="smaller-text text-tertiary mb-1 block">Телефон</label>
                                <input v-model="createForm.client_phone" type="text" placeholder="+99890XXXXXXX"
                                    class="input input-minimal w-full">
                            </div>
                            <div class="detail-input-wrap">
                                <label class="smaller-text text-tertiary mb-1 block">Имя (ФИО)</label>
                                <input v-model="createForm.client_name" type="text" placeholder="Иван Иванов"
                                    class="input input-minimal w-full">
                            </div>
                        </div>
                        <div v-if="createForm.client_id"
                            class="mt-2 text-success smaller-text font-medium flex items-center gap-1">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="3">
                                <path d="M20 6L9 17l-5-5" />
                            </svg>
                            Выбран существующий клиент
                        </div>
                    </div>

                    <div class="form-group-premium mb-8">
                        <label class="section-label mb-2">Источник</label>
                        <select v-model="createForm.source" class="input input-minimal w-full">
                            <option value="Admin Panel">Админ-панель (Вручную)</option>
                            <option value="Phone Call">Телефонный звонок</option>
                            <option value="Telegram">Telegram / WhatsApp</option>
                            <option value="Office Visit">Визит в офис</option>
                        </select>
                    </div>

                    <div class="modal-actions-premium mt-10">
                        <button class="btn btn-ghost mr-4" @click="showCreateModal = false" :disabled="isCreating">
                            Отмена
                        </button>
                        <button class="btn btn-primary btn-lg shadow-lg flex-grow font-bold" @click="handleAdminCreate"
                            :disabled="isCreating || !createForm.car_id || !createForm.client_phone">
                            {{ isCreating ? $t('common.loading') : $t('applications.createModal.createButton') }}
                        </button>
                    </div>
                </div>
            </div>
        </Teleport>

        <!-- Application Detail Modal -->
        <Teleport to="body">
            <div v-if="selectedApp" class="modal-overlay" @click.self="selectedApp = null">
                <div class="side-panel animate-slide-in shadow-2xl">
                    <div class="side-header">
                        <div class="flex-between">
                            <div>
                                <h3 class="m-0 text-thin text-primary">{{ $t('applications.detail.title') }}</h3>
                                <div class="mt-1">
                                    <code class="id-badge-minimal">ID: {{ selectedApp.id }}</code>
                                </div>
                            </div>
                            <button class="btn btn-icon-only btn-ghost hover-accent" @click="selectedApp = null">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M18 6L6 18M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <div class="side-content">
                        <!-- Status Section -->
                        <div class="detail-section mb-10">
                            <div class="flex-between mb-4">
                                <div class="status-group">
                                    <label class="section-label mb-2">{{ $t('applications.detail.currentStage')
                                    }}</label>
                                    <div class="mt-1">
                                        <span class="badge badge-lg" :class="selectedApp.status">{{
                                            translateStatus(selectedApp.status)
                                        }}</span>
                                    </div>
                                </div>
                                <div class="status-group">
                                    <label class="section-label mb-2">{{ $t('applications.detail.contactStatus')
                                    }}</label>
                                    <div class="mt-1">
                                        <select v-if="hasRole('operator') || hasRole('manager') || hasRole('admin')"
                                            :value="selectedApp.contact_status"
                                            @change="handleContactStatusUpdate(($event.target as HTMLSelectElement).value)"
                                            class="input input-sm contact-status-select"
                                            :class="selectedApp.contact_status">
                                            <option value="not_touched">{{
                                                $t('applications.contactStatuses.not_touched') }}
                                            </option>
                                            <option value="no_answer">{{ $t('applications.contactStatuses.no_answer') }}
                                            </option>
                                            <option value="contacted">{{ $t('applications.contactStatuses.contacted') }}
                                            </option>
                                            <option value="callback">{{ $t('applications.contactStatuses.callback') }}
                                            </option>
                                            <option value="rejected">{{ $t('applications.contactStatuses.rejected') }}
                                            </option>
                                            <option value="confirmed_interest">{{
                                                $t('applications.contactStatuses.confirmed_interest') }}</option>
                                        </select>
                                        <span v-else class="badge badge-outline">{{
                                            translateContactStatus(selectedApp.contact_status) }}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="flex-between mb-4">
                                <div class="assignment-group">
                                    <label class="section-label mb-2">{{ $t('applications.operator') }}</label>
                                    <div class="flex items-center gap-2">
                                        <select v-if="showAssign && hasRole('admin')"
                                            @change="handleAssign(($event.target as HTMLSelectElement).value)"
                                            class="input input-sm">
                                            <option value="">{{ $t('common.notAssigned') }}</option>
                                            <option v-for="op in operators" :key="op.id" :value="op.id">{{ op.first_name
                                            }} {{ op.last_name }}</option>
                                        </select>
                                        <div v-else class="text-primary font-bold">{{
                                            getOperatorName(selectedApp.operator_id) }}</div>
                                        <button v-if="hasRole('admin')" class="btn btn-icon-only btn-ghost btn-xs"
                                            @click="showAssign = !showAssign">
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                                                stroke="currentColor" stroke-width="2">
                                                <path
                                                    d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="assignment-group">
                            <label class="section-label mb-2">{{ $t('applications.manager') }}</label>
                            <div class="flex items-center gap-2">
                                <select v-if="showAssignManager && hasRole('admin')"
                                    @change="handleAssignManager(($event.target as HTMLSelectElement).value)"
                                    class="input input-sm">
                                    <option value="">{{ $t('common.notAssigned') }}</option>
                                    <option v-for="man in managers" :key="man.id" :value="man.id">{{ man.first_name
                                        }} {{ man.last_name }}</option>
                                </select>
                                <div v-else class="text-primary font-bold">{{
                                    getOperatorName(selectedApp.manager_id) }}</div>
                                <button v-if="hasRole('admin')" class="btn btn-icon-only btn-ghost btn-xs"
                                    @click="showAssignManager = !showAssignManager">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                        stroke-width="2">
                                        <path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <div class="action-buttons-group mt-6">
                            <!-- Operator Actions -->
                            <button v-if="hasRole('operator') && selectedApp.status === 'new'"
                                class="btn btn-sm btn-success flex-grow font-bold" @click="updateStatus('confirmed')">
                                {{ $t('applications.actions.confirm') }}
                            </button>

                            <!-- Manager Actions -->
                            <button v-if="hasRole('manager') && selectedApp.status === 'confirmed'"
                                class="btn btn-sm btn-outline flex-grow font-medium"
                                @click="updateStatus('contract_signed')">
                                {{ $t('applications.actions.contractSigned') }}
                            </button>
                            <button v-if="hasRole('manager') && selectedApp.status === 'contract_signed'"
                                class="btn btn-sm btn-success flex-grow font-bold" @click="updateStatus('paid')">
                                {{ $t('applications.actions.paid') }}
                            </button>
                            <button v-if="hasRole('manager') && selectedApp.status === 'paid'"
                                class="btn btn-sm btn-outline flex-grow font-medium" @click="updateStatus('delivered')">
                                {{ $t('applications.actions.delivered') }}
                            </button>
                            <button v-if="hasRole('admin')"
                                class="btn btn-sm btn-outline text-error flex-grow font-medium" @click="promptCancel">
                                {{ $t('applications.actions.cancel') }}
                            </button>
                        </div>

                        <!-- Info Cards Grid -->
                        <div class="grid grid-2 gap-6 mb-10">
                            <div class="detail-card">
                                <label class="section-label mb-3">{{ $t('applications.detail.clientProfile') }}</label>
                                <div class="text-primary font-bold mb-1">{{ selectedApp.client_first_name }} {{
                                    selectedApp.client_last_name }}</div>
                                <div class="text-secondary smaller-text mb-1">{{ selectedApp.client_phone }}</div>
                                <div v-if="selectedApp.client_email" class="text-tertiary smaller-text">{{
                                    selectedApp.client_email }}</div>
                            </div>
                            <div class="detail-card clickable-card"
                                @click="navigateTo('/cars?open=' + selectedApp.car_id)">
                                <div class="flex-between mb-3">
                                    <label class="section-label cursor-pointer">{{ $t('applications.detail.carInfo')
                                        }}</label>
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                        stroke-width="2" class="text-tertiary">
                                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                                        <polyline points="15 3 21 3 21 9"></polyline>
                                        <line x1="10" y1="14" x2="21" y2="3"></line>
                                    </svg>
                                </div>
                                <div class="flex gap-4">
                                    <div v-if="selectedApp.car_image_url" class="mini-thumb-wrap">
                                        <img :src="selectedApp.car_image_url" class="mini-thumb">
                                    </div>
                                    <div>
                                        <div class="text-primary font-bold mb-1">{{ selectedApp.car_brand }} {{
                                            selectedApp.car_model }}</div>
                                        <div class="text-accent font-bold">
                                            {{ selectedApp.final_price?.toLocaleString() }}
                                            <span class="smaller-text font-normal text-tertiary">USD</span>
                                        </div>
                                        <div class="smaller-text text-tertiary mt-1" v-if="selectedApp.car_year">{{
                                            selectedApp.car_year }} г.в.</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Checklist Section -->
                        <div class="detail-section mb-10">
                            <h4 class="section-label">{{ $t('applications.detail.checklist') }}</h4>
                            <div class="checklist-grid">
                                <div v-for="(val, key) in selectedApp.checklist" :key="key" class="check-item-premium"
                                    :class="{ checked: val, disabled: !hasRole(['operator', 'manager', 'admin']) }"
                                    @click="(hasRole('operator') || hasRole('manager') || hasRole('admin')) && toggleChecklist(key as string)">
                                    <div class="checkbox-premium">
                                        <div class="check-mark-mini" v-if="val">✓</div>
                                    </div>
                                    <span class="check-label-premium">{{ translateKey(key as string) }}</span>
                                </div>
                            </div>
                        </div>

                        <!-- Documents Section -->
                        <div class="detail-section mb-10">
                            <div class="flex-between mb-4">
                                <h4 class="section-label m-0">{{ $t('applications.detail.documents') }}</h4>
                                <button v-if="hasRole('manager')" class="btn btn-xs btn-outline"
                                    @click="fileInputContract?.click()" :disabled="isUploading">
                                    {{ isUploading ? '...' : $t('applications.detail.uploadContract') }}
                                </button>
                                <input ref="fileInputContract" type="file" class="hidden"
                                    @change="handleFileUpload($event, 'contract')" accept=".pdf,.doc,.docx,.jpg,.png">
                            </div>
                            <div class="document-list-premium">
                                <div v-for="doc in appDocuments" :key="doc.id" class="doc-item-premium">
                                    <div class="doc-icon">📄</div>
                                    <div class="doc-info">
                                        <div class="doc-name">{{ doc.original_filename }}</div>
                                        <div class="doc-meta">{{ formatDate(doc.created_at) }}</div>
                                    </div>
                                    <a :href="`${apiBase}/documents/${doc.id}/download?token=${authToken}`"
                                        target="_blank" class="doc-download">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                                            stroke="currentColor" stroke-width="2">
                                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v4" />
                                            <polyline points="7 10 12 15 17 10" />
                                            <line x1="12" y1="15" x2="12" y2="3" />
                                        </svg>
                                    </a>
                                </div>
                                <div v-if="appDocuments.length === 0" class="text-tertiary smaller-text italic py-2">
                                    {{ $t('applications.detail.noDocuments') }}
                                </div>
                            </div>
                        </div>

                        <!-- Videos Section -->
                        <div class="detail-section mb-10">
                            <div class="flex-between mb-4">
                                <h4 class="section-label m-0">{{ $t('applications.detail.videos') }}</h4>
                                <button v-if="hasRole('manager')" class="btn btn-xs btn-outline"
                                    @click="fileInputVideo?.click()" :disabled="isUploading">
                                    {{ isUploading ? '...' : $t('applications.detail.uploadVideo') }}
                                </button>
                                <input ref="fileInputVideo" type="file" class="hidden"
                                    @change="handleFileUpload($event, 'video_signature')" accept="video/*">
                            </div>
                            <div class="document-list-premium">
                                <div v-for="vid in appVideos" :key="vid.id" class="doc-item-premium">
                                    <div class="doc-icon">🎥</div>
                                    <div class="doc-info">
                                        <div class="doc-name">{{ vid.original_filename }}</div>
                                        <div class="doc-meta">{{ formatDate(vid.created_at) }}</div>
                                    </div>
                                    <a :href="`${apiBase}/documents/${vid.id}/download?token=${authToken}`"
                                        target="_blank" class="doc-download">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                                            stroke="currentColor" stroke-width="2">
                                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v4" />
                                            <polyline points="7 10 12 15 17 10" />
                                            <line x1="12" y1="15" x2="12" y2="3" />
                                        </svg>
                                    </a>
                                </div>
                                <div v-if="appVideos.length === 0" class="text-tertiary smaller-text italic py-2">
                                    {{ $t('applications.detail.noVideos') }}
                                </div>
                            </div>
                        </div>

                        <!-- Comments Section -->
                        <div class="detail-section">
                            <h4 class="section-label">{{ $t('applications.detail.comments') }}</h4>
                            <div class="comment-input-wrap mb-8">
                                <textarea v-model="newComment" :placeholder="$t('applications.detail.addNote')"
                                    class="input input-minimal comment-area" rows="3"></textarea>
                                <div class="flex-end mt-2">
                                    <button class="btn btn-sm btn-primary font-bold" @click="postComment">
                                        {{ $t('common.add') }}
                                    </button>
                                </div>
                            </div>

                            <div class="activity-ledger">
                                <div v-for="c in comments" :key="c.id" class="ledger-item">
                                    <div class="ledger-dot"></div>
                                    <div class="ledger-entry">
                                        <div class="flex-between mb-2">
                                            <span class="ledger-user">{{ c.user_first_name }} {{ c.user_last_name
                                                }}</span>
                                            <span class="ledger-time">{{ formatDate(c.created_at) }}</span>
                                        </div>
                                        <p class="ledger-text">{{ c.text }}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Teleport>

        <!-- Toast Notifications -->
        <Toast v-model="toast.state.visible" :title="toast.state.title" :message="toast.state.message"
            :type="toast.state.type" :duration="toast.state.duration" />
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

const toast = useToast()
const { t } = useI18n()
const route = useRoute()

const {
    getApplications,
    getApplication,
    updateApplicationStatus,
    updateApplicationContactStatus,
    updateApplicationChecklist,
    addApplicationComment,
    getApplicationComments,
    getUsers,
    assignOperator,
    assignManager,
    adminCreateApplication,
    getCars,
    hasRole,
    uploadDocument,
    getDocuments,
    getVideos,
    apiBase,
    authToken,
    currentUser,
    getStats
} = useApi()

const filterStatuses = computed(() => [
    { key: 'All', label: t('applications.filters.all') },
    { key: 'new', label: t('applications.filters.new') },
    { key: 'confirmed', label: t('applications.filters.confirmed') },
    { key: 'paid', label: t('applications.filters.paid') },
    { key: 'delivered', label: t('applications.filters.completed') },
    { key: 'cancelled', label: t('applications.filters.cancelled') }
])
const activeFilter = ref('All')
const searchQuery = ref('')
const loading = ref(true)
const selectedApp = ref<any>(null)
const applications = ref<any[]>([])
const comments = ref<any[]>([])
const newComment = ref('')
const operators = ref<any[]>([])
const managers = ref<any[]>([])
const showAssign = ref(false)
const showAssignManager = ref(false)
const appDocuments = ref<any[]>([])
const appVideos = ref<any[]>([])
const isUploading = ref(false)
const fileInputContract = ref<HTMLInputElement | null>(null)
const fileInputVideo = ref<HTMLInputElement | null>(null)
const dashboardStats = ref<any>(null)

// Create Application Modal
const showCreateModal = ref(false)
const isCreating = ref(false)
const availableCars = ref<any[]>([])
const carSearchQuery = ref('')
const clientSearchQuery = ref('')
const clientSearchResults = ref<any[]>([])
const createForm = ref({
    car_id: '',
    client_id: '',
    client_phone: '',
    client_name: '',
    source: 'Admin Panel'
})

const filteredCars = computed(() => {
    if (!carSearchQuery.value) return availableCars.value
    const query = carSearchQuery.value.toLowerCase()
    return availableCars.value.filter(car =>
        car.brand.toLowerCase().includes(query) ||
        car.model.toLowerCase().includes(query) ||
        car.year.toString().includes(query)
    )
})

const selectedCar = computed(() => {
    return availableCars.value.find(c => c.id === createForm.value.car_id)
})

// Consolidated Client Search Logic
let clientSearchTimeout: any = null
const clientSearchLoading = ref(false)

watch(clientSearchQuery, async (val) => {
    // 1. Sync phone if not selected existing
    if (val && !createForm.value.client_id) {
        if (/\d/.test(val)) {
            createForm.value.client_phone = val
        }
    }

    // 2. Debounced API Search for existing clients
    if (clientSearchTimeout) clearTimeout(clientSearchTimeout)

    if (!val || val.length < 3) {
        clientSearchResults.value = []
        return
    }

    clientSearchLoading.value = true
    clientSearchTimeout = setTimeout(async () => {
        console.log('Searching clients for:', val)
        try {
            const res: any = await getUsers({ search: val, role: 'client', per_page: 5 }).catch(e => {
                console.error('Search API error:', e)
                return []
            })
            clientSearchResults.value = res || []
            console.log('Found clients:', clientSearchResults.value.length)
        } catch (err) {
            clientSearchResults.value = []
        } finally {
            clientSearchLoading.value = false
        }
    }, 400)
})

const selectExistingClient = (client: any) => {
    createForm.value.client_id = client.id
    createForm.value.client_phone = client.phone
    createForm.value.client_name = `${client.first_name} ${client.last_name}`
    clientSearchResults.value = []
    clientSearchQuery.value = ''
}

const fetchCars = async () => {
    try {
        const res: any = await getCars({ is_active: true, per_page: 50 })
        availableCars.value = res.items || []
    } catch (err) { }
}

const handleAdminCreate = async () => {
    // If phone is empty but search query has a value, use it as phone
    if (!createForm.value.client_phone && clientSearchQuery.value) {
        createForm.value.client_phone = clientSearchQuery.value
    }

    if (!createForm.value.car_id || !createForm.value.client_phone) {
        toast.warning(t('common.warning'), t('applications.fillRequired'))
        return
    }

    isCreating.value = true
    try {
        await adminCreateApplication(createForm.value)
        showCreateModal.value = false
        // Reset form
        createForm.value = {
            car_id: '',
            client_id: '',
            client_phone: '',
            client_name: '',
            source: 'Admin Panel'
        }
        carSearchQuery.value = ''
        clientSearchQuery.value = ''
        fetchApplications()
    } catch (err: any) {
        toast.error(t('common.error'), err?.data?.detail || t('common.error'))
    } finally {
        isCreating.value = false
    }
}

const fetchApplications = async () => {
    loading.value = true
    try {
        const res: any = await getApplications()
        applications.value = res.items || []
    } catch (err) {
        applications.value = []
    } finally {
        loading.value = false
    }
}

const fetchOperators = async () => {
    try {
        // Fetch both operators and managers for assignment
        const ops: any = await getUsers({ role: 'operator', per_page: 100 })
        const mans: any = await getUsers({ role: 'manager', per_page: 100 })
        operators.value = ops || []
        managers.value = mans || []
    } catch (err) { }
}

const handleAssignManager = async (managerId: string) => {
    if (!selectedApp.value) return
    try {
        await assignManager(selectedApp.value.id, managerId)
        selectedApp.value.manager_id = managerId
        // Update local list
        const localApp = applications.value.find(a => a.id === selectedApp.value.id)
        if (localApp) localApp.manager_id = managerId

        toast.success(t('common.success'), t('applications.assigned'))
        showAssignManager.value = false
    } catch (e: any) {
        toast.error(t('common.error'), e?.data?.detail || t('common.error'))
    }
}

const filteredApplications = computed(() => {
    return applications.value.filter(a => {
        // Role-based visibility filtering
        if (!hasRole('admin')) {
            if (hasRole('manager')) {
                // Managers see everything from 'confirmed' onwards, excluding 'new' and 'cancelled'
                const managerHiddenStatuses = ['new', 'cancelled']
                if (managerHiddenStatuses.includes(a.status.toLowerCase())) return false
            } else if (hasRole('operator')) {
                // Operators see only 'new' applications
                if (a.status.toLowerCase() !== 'new') return false
            }
        }

        const matchesStatus = activeFilter.value === 'All' || a.status.toLowerCase() === activeFilter.value.toLowerCase()
        const clientName = `${a.client_first_name || ''} ${a.client_last_name || ''}`
        const carName = `${a.car_brand || ''} ${a.car_model || ''}`
        const matchesSearch = !searchQuery.value ||
            clientName.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            carName.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            a.client_phone?.includes(searchQuery.value)
        return matchesStatus && matchesSearch
    })
})

const openDetail = async (app: any) => {
    // Manager auto-assignment on click
    // When a manager opens a confirmed application, they become the manager of it.
    if (hasRole('manager') && app.status !== 'new' && app.operator_id !== (currentUser.value as any)?.id) {
        try {
            await assignOperator(app.id, (currentUser.value as any).id)
            app.operator_id = (currentUser.value as any).id
            // Update local applications list to reflect assignment
            const localApp = applications.value.find(a => a.id === app.id)
            if (localApp) localApp.operator_id = (currentUser.value as any).id
        } catch (e) {
            console.error('Auto-assignment failed', e)
        }
    }

    // Only show these specific checklist items per user request
    const checklist: Record<string, boolean> = {
        'agreed_visit': app.checklist?.agreed_visit || false,
        'documents': app.checklist?.documents || false
    }

    selectedApp.value = { ...app, checklist }

    try {
        const res: any = await getApplicationComments(app.id)
        comments.value = res || []
    } catch (err) {
        comments.value = []
    }

    fetchDocuments(app.id)
    fetchVideos(app.id)
}

const fetchDocuments = async (appId: string) => {
    try {
        const res: any = await getDocuments(appId)
        appDocuments.value = res || []
    } catch (err) {
        appDocuments.value = []
    }
}

const fetchVideos = async (appId: string) => {
    try {
        const res: any = await getVideos(appId)
        appVideos.value = res || []
    } catch (err) {
        appVideos.value = []
    }
}

const handleFileUpload = async (event: Event, type: 'contract' | 'video_signature') => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file || !selectedApp.value) return

    isUploading.value = true
    try {
        await uploadDocument(selectedApp.value.id, file, type)
        toast.success(t('common.success'), t('common.fileUploaded'))
        if (type === 'contract') fetchDocuments(selectedApp.value.id)
        else fetchVideos(selectedApp.value.id)
    } catch (err: any) {
        toast.error(t('common.error'), err?.data?.detail || t('common.error'))
    } finally {
        isUploading.value = false
        target.value = ''
    }
}

const updateStatus = async (newStatus: string) => {
    if (!selectedApp.value) return

    // Business validation on frontend
    if (newStatus === 'confirmed') {
        // Relaxed validation: Only require 'agreed_visit' per user request
        if (!selectedApp.value.checklist.agreed_visit) {
            toast.warning(t('applications.validation.cannotConfirm'), t('applications.validation.visitRequired'))
            return
        }
    }

    const reason = prompt(t('applications.actions.confirm'), t('common.updated'))
    if (reason === null) return

    try {
        await updateApplicationStatus(selectedApp.value.id, newStatus, reason)
        selectedApp.value.status = newStatus
        fetchApplications()
        toast.success(t('common.success'), t('common.updated'))
    } catch (err: any) {
        toast.error(t('common.error'), err?.data?.detail || t('applications.errors.updateStatusFailed'))
    }
}

const handleContactStatusUpdate = async (newContactStatus: string) => {
    if (!selectedApp.value) return
    try {
        await updateApplicationContactStatus(selectedApp.value.id, newContactStatus)
        selectedApp.value.contact_status = newContactStatus
        fetchApplications()
    } catch (err: any) {
        toast.error(t('common.error'), err?.data?.detail || t('common.error'))
    }
}

const promptCancel = () => updateStatus('cancelled')

const postComment = async () => {
    if (!newComment.value || !selectedApp.value) return
    try {
        const res: any = await addApplicationComment(selectedApp.value.id, newComment.value)
        comments.value.unshift(res)
        newComment.value = ''
    } catch (err) {
        toast.error(t('common.error'), t('common.error'))
    }
}

const toggleChecklist = async (key: string) => {
    if (!selectedApp.value) return
    const updatedChecklist = { ...selectedApp.value.checklist }
    updatedChecklist[key] = !updatedChecklist[key]

    try {
        await updateApplicationChecklist(selectedApp.value.id, updatedChecklist)
        selectedApp.value.checklist = updatedChecklist
    } catch (err) {
        toast.error(t('common.error'), t('common.error'))
    }
}

const handleAssign = async (opId: string) => {
    if (!selectedApp.value) return
    try {
        await assignOperator(selectedApp.value.id, opId)
        selectedApp.value.operator_id = opId
        showAssign.value = false
        fetchApplications()
    } catch (err) {
        toast.error(t('common.error'), t('common.error'))
    }
}

const formatDate = (d: string) => {
    if (!d) return '—'
    return new Date(d).toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const translateStatus = (s: string) => {
    return t(`applications.status.${s?.toLowerCase()}`)
}

const translateContactStatus = (s: string) => {
    return t(`applications.contactStatuses.${s?.toLowerCase()}`)
}

const translateKey = (key: string) => {
    return t(`applications.checklist.${key}`)
}

const getOperatorName = (id: string) => {
    const op = operators.value.find(o => o.id === id)
    return op ? `${op.first_name} ${op.last_name}` : t('common.notAssigned')
}

onMounted(async () => {
    fetchApplications()
    fetchOperators()
    fetchCars()

    // Auto-open application if ID is in URL
    if (route.query.id) {
        try {
            const app = await getApplication(route.query.id as string)
            if (app) openDetail(app)
        } catch (e) {
            console.error('Auto-open failed:', e)
        }
    }

    if (!hasRole('admin')) {
        try {
            dashboardStats.value = await getStats('all')
        } catch (e) {
            console.error('Failed to fetch stats', e)
        }
    }
})

// Watch for route changes to open application details dynamically
watch(() => route.query.id, async (newId) => {
    if (newId) {
        try {
            const app = await getApplication(newId as string)
            if (app) openDetail(app)
        } catch (e) {
            console.error('Dynamic open failed:', e)
        }
    }
})

definePageMeta({ layout: false })
</script>

<style scoped>
.disabled {
    opacity: 0.6;
    pointer-events: none;
}

.contact-status-select {
    font-weight: 700;
    border-radius: 4px;
    padding: 0.25rem 0.5rem;
    border: 1px solid var(--color-border);
    background: var(--color-bg-primary);
}

.contact-status-select.contacted,
.contact-status-select.confirmed_interest {
    color: var(--color-success);
    border-color: var(--color-success);
}

.contact-status-select.not_touched {
    color: var(--color-text-tertiary);
}

.contact-status-select.rejected {
    color: var(--color-error);
    border-color: var(--color-error);
}

.badge-outline {
    background: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-text-secondary);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
}

.page-header {
    padding: var(--spacing-xl) 0 var(--spacing-lg);
}

.input-minimal {
    background: transparent;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 0.5rem 1rem;
    color: var(--color-text-primary);
}

.filter-chip-premium {
    padding: 0.5rem 1.25rem;
    border-radius: 2rem;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    background: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-text-tertiary);
    cursor: pointer;
    transition: all var(--transition);
    white-space: nowrap;
}

.filter-chip-premium.active {
    background: var(--color-text-primary);
    color: var(--color-bg-primary);
    border-color: var(--color-text-primary);
}

.operator-badge-minimal {
    font-size: 0.75rem;
    color: var(--color-text-secondary);
    background: var(--color-bg-secondary);
    padding: 4px 10px;
    border-radius: 100px;
    display: inline-block;
    border: 1px solid var(--color-border);
    transition: all var(--transition);
}

.operator-badge-minimal.assigned {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
    border-color: rgba(16, 185, 129, 0.2);
    font-weight: 600;
}

/* Status Badges */
.badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}

.badge.new {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    border: 1px solid rgba(59, 130, 246, 0.2);
}

.badge.confirmed {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.badge.contract_signed {
    background: rgba(139, 92, 246, 0.1);
    color: #8b5cf6;
    border: 1px solid rgba(139, 92, 246, 0.2);
}

.badge.paid {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.2);
}

.badge.delivered {
    background: rgba(16, 185, 129, 0.15);
    color: #059669;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge.cancelled {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.2);
}

/* Modal Core Styles */
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(8px);
    display: flex;
    justify-content: flex-end;
    z-index: 2000;
    animation: modalFadeIn 0.3s ease;
}

.modal-panel {
    background: var(--color-bg-primary);
    box-shadow: -10px 0 30px rgba(0, 0, 0, 0.4);
    position: relative;
}

.side-panel {
    width: 100%;
    max-width: 600px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--color-bg-primary);
    border-left: 1px solid var(--color-border);
}

.side-header {
    padding: 1.5rem 2.5rem;
    border-bottom: 1px solid var(--color-border);
    background: var(--color-bg-primary);
}

.side-content {
    flex: 1;
    padding: 2.5rem;
    overflow-y: auto;
    background: var(--color-bg-primary);
}

/* Create Modal Specific */
.modal-header-premium {
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--color-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--color-bg-primary);
}

.modal-body-premium {
    padding: 2rem;
    background: var(--color-bg-primary);
    overflow-y: auto;
    max-height: calc(100vh - 120px);
}

.options-list-premium {
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-bg-card);
}

.option-item-premium {
    padding: 1rem;
    cursor: pointer;
    transition: var(--transition);
    border-bottom: 1px solid var(--color-border);
    background: var(--color-bg-card);
}

.option-item-premium:last-child {
    border-bottom: none;
}

.option-item-premium:hover {
    background: var(--color-bg-hover);
}

.option-item-premium.selected {
    background: var(--color-bg-hover);
    border-left: 3px solid var(--color-success);
}

.client-results-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    z-index: 100;
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    margin-top: 4px;
    max-height: 200px;
    overflow-y: auto;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.client-result-item {
    padding: 0.75rem 1rem;
    cursor: pointer;
    border-bottom: 1px solid var(--color-border);
    background: var(--color-bg-card);
}

.client-result-item:hover {
    background: var(--color-bg-hover);
}

.section-label {
    display: block;
    text-transform: uppercase;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--color-text-tertiary);
}

/* Detail Elements */
.detail-card {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
}

.mini-thumb-wrap {
    width: 80px;
    height: 60px;
    border-radius: var(--radius-sm);
    overflow: hidden;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
}

.mini-thumb {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* Checklist Premium */
.checklist-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.check-item-premium {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.85rem 1.25rem;
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition);
    border: 1px solid var(--color-border);
}

.check-item-premium:hover {
    background: var(--color-bg-hover);
    border-color: var(--color-text-tertiary);
}

.check-item-premium.checked {
    border-color: var(--color-success);
    background: rgba(16, 185, 129, 0.08);
}

.checkbox-premium {
    width: 20px;
    height: 20px;
    border: 2px solid var(--color-border);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition);
    flex-shrink: 0;
}

.check-item-premium.checked .checkbox-premium {
    background: var(--color-success);
    border-color: var(--color-success);
}

.check-mark-mini {
    color: white;
    font-size: 11px;
    font-weight: 900;
}

.check-label-premium {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-secondary);
}

.check-item-premium.checked .check-label-premium {
    color: var(--color-success);
}

/* Ledger/History */
.ledger-item {
    position: relative;
    padding-left: 2rem;
    padding-bottom: 2rem;
}

.ledger-item:last-child {
    padding-bottom: 0;
}

.ledger-item::before {
    content: '';
    position: absolute;
    left: 4px;
    top: 10px;
    bottom: 0;
    width: 2px;
    background: var(--color-border);
}

.ledger-item:last-child::before {
    display: none;
}

.ledger-dot {
    position: absolute;
    left: 0;
    top: 6px;
    width: 10px;
    height: 10px;
    background: var(--color-text-tertiary);
    border: 2px solid var(--color-bg-primary);
    border-radius: 50%;
    z-index: 1;
}

.ledger-entry {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    padding: 1.25rem;
    border-radius: var(--radius-md);
}

.comment-area {
    width: 100%;
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: 1rem;
    resize: none;
    font-family: inherit;
    color: var(--color-text-primary);
    min-height: 80px;
}

/* Document List Styles */
.document-list-premium {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.doc-item-premium {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    transition: var(--transition);
}

.doc-item-premium:hover {
    border-color: var(--color-accent);
}

.doc-icon {
    font-size: 1.25rem;
}

.doc-info {
    flex: 1;
}

.doc-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 250px;
}

.doc-meta {
    font-size: 0.7rem;
    color: var(--color-text-tertiary);
}

.doc-download {
    color: var(--color-text-tertiary);
    transition: var(--transition);
}

.doc-download:hover {
    color: var(--color-accent);
}

/* Animations */
@keyframes modalFadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
    }

    to {
        transform: translateX(0);
    }
}

.animate-slide-in {
    animation: slideInRight 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@media (max-width: 640px) {
    .modal-panel.side-panel {
        max-width: 100%;
    }

    .checklist-grid {
        grid-template-columns: 1fr;
    }
}

.hidden {

    display: none;
}

.detail-card.clickable-card {
    cursor: pointer;
    transition: all var(--transition);
}

.detail-card.clickable-card:hover {
    border-color: var(--color-accent);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.markup-badge-mini {
    background: rgba(16, 185, 129, 0.08);
    color: var(--color-success);
    font-size: 0.65rem;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 4px;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.id-badge-minimal {
    font-family: monospace;
    font-size: 0.7rem;
    color: var(--color-text-tertiary);
    background: var(--color-bg-secondary);
    padding: 2px 6px;
    border-radius: 4px;
    opacity: 0.8;
}
</style>
