<template>
  <div class="stories-page animate-fade-in">
    <header class="page-header">
      <div class="container">
        <div class="flex-between">
          <div class="header-info">
            <h1 class="text-thin">{{ $t('stories.title') }}</h1>
            <p class="text-secondary text-light">{{ $t('stories.subtitle') }}</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-primary btn-sm shadow-sm" @click="openCreateStory">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                class="mr-2">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              {{ $t('stories.addStory') }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <div class="container pb-20">
      <div v-if="loading" class="flex-center py-20">
        <p class="text-tertiary">{{ $t('common.loading') }}</p>
      </div>

      <div v-else-if="stories.length === 0" class="card text-center py-20 flex-column items-center">
        <div class="mb-4 text-tertiary opacity-50">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <circle cx="12" cy="12" r="10" />
            <circle cx="12" cy="12" r="6" />
          </svg>
        </div>
        <h3 class="text-thin">{{ $t('stories.empty.title') }}</h3>
        <p class="text-secondary mb-6">{{ $t('stories.empty.text') }}</p>
        <button class="btn btn-primary btn-sm" @click="openCreateStory">{{ $t('stories.addStory') }}</button>
      </div>

      <div v-else class="stories-grid gap-6">
        <div v-for="story in stories" :key="story.id" class="card story-card overflow-hidden">
          <div class="story-preview-bg" :style="{ backgroundImage: `url(${story.preview_image})` }">
            <div class="story-overlay">
              <div class="flex items-center justify-between w-full">
                <span class="badge" :class="story.is_active ? 'badge-success' : 'badge-outline'">{{ story.is_active ?
                  $t('stories.status.active') : $t('stories.status.draft') }}</span>
                <div class="order-badge">#{{ story.order }}</div>
              </div>
            </div>
          </div>
          <div class="p-4">
            <h3 class="font-bold mb-1">{{ getLocalizedTitle(story.title) }}</h3>
            <p class="smaller-text text-tertiary mb-4">{{ story.slides.length }} {{
              $t('stories.form.slides').toLowerCase() }}</p>
            <div class="flex gap-2">
              <button class="btn btn-outline btn-xs flex-grow" @click="editStory(story)">{{ $t('stories.edit')
                }}</button>
              <button class="btn btn-ghost btn-xs text-error" @click="confirmDelete(story)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Story Modal (Create/Edit Group) -->
    <Teleport to="body">
      <div v-if="showStoryModal" class="modal-overlay" @click.self="showStoryModal = false">
        <div class="modal-panel side-panel animate-slide-in shadow-2xl">
          <div class="side-header">
            <h3 class="m-0 text-thin">{{ isEditing ? $t('stories.modal.edit') : $t('stories.modal.create') }}</h3>
            <button class="btn btn-icon-only btn-ghost" @click="showStoryModal = false">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="side-content custom-scrollbar">
            <div class="form-section mb-8">
              <label class="section-label mb-3">{{ $t('stories.form.title') }} <span class="text-error">*</span></label>
              <div class="flex flex-column gap-3">
                <input v-model="storyForm.title.ru" type="text" placeholder="Заголовок RU" class="input input-minimal">
                <input v-model="storyForm.title.uz" type="text" placeholder="Заголовок UZ" class="input input-minimal">
                <input v-model="storyForm.title.en" type="text" placeholder="Заголовок EN" class="input input-minimal">
              </div>
            </div>

            <div class="form-section mb-8">
              <label class="section-label mb-3">{{ $t('stories.form.icon') }} <span class="text-error">*</span></label>
              <p class="smaller-text text-secondary mb-2">{{ $t('stories.form.previewHint') || 'Upload image or URL' }}
              </p>

              <div class="flex gap-2 mb-2">
                <input type="file" ref="storyImageInput" @change="handleStoryImageUpload" accept="image/*"
                  class="input input-minimal w-full">
                <div v-if="uploadingImage" class="flex-center px-2">
                  <div class="spinner-sm"></div>
                </div>
              </div>
              <input v-model="storyForm.preview_image" type="text" placeholder="https://..."
                class="input input-minimal w-full">

              <div v-if="storyForm.preview_image" class="mt-2">
                <img :src="storyForm.preview_image" class="preview-thumb rounded">
              </div>
            </div>

            <div class="flex gap-4 mb-10">
              <div class="flex-grow">
                <label class="section-label mb-3">{{ $t('stories.form.order') }}</label>
                <input v-model.number="storyForm.order" type="number" class="input input-minimal w-full">
              </div>
              <div>
                <label class="section-label mb-3">{{ $t('stories.form.status') }}</label>
                <div class="flex items-center gap-2 mt-2">
                  <input type="checkbox" v-model="storyForm.is_active" id="is_active_check">
                  <label for="is_active_check" class="smaller-text font-bold">{{ $t('stories.form.active') }}</label>
                </div>
              </div>
            </div>

            <hr class="border-light my-8">

            <div v-if="isEditing">
              <div class="flex-between mb-4">
                <h4 class="m-0 text-thin">{{ $t('stories.form.slides') }}</h4>
                <button class="btn btn-outline btn-xs" @click="openAddSlide">{{ $t('stories.modal.addSlide') }}</button>
              </div>

              <div v-if="storyForm.slides.length === 0"
                class="text-center py-6 text-tertiary smaller-text border-dashed-light rounded-lg">
                {{ $t('stories.form.noSlides') }}
              </div>

              <div class="slides-list flex flex-column gap-3">
                <div v-for="slide in storyForm.slides" :key="slide.id" class="slide-item-mini card-mini">
                  <div class="flex gap-3">
                    <img :src="slide.image_url" class="mini-thumb rounded">
                    <div class="flex-grow min-w-0">
                      <div class="font-bold text-truncate">{{ getLocalizedTitle(slide.title) }}</div>
                      <div class="smaller-text text-tertiary text-truncate">{{ getLocalizedTitle(slide.content) }}</div>
                    </div>
                    <button class="btn btn-ghost btn-xs text-error p-1" @click="handleDeleteSlide(slide.id)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="side-footer">
            <button class="btn btn-primary btn-lg w-full font-bold" @click="handleSaveStory" :disabled="saving">
              {{ saving ? $t('common.loading') : (isEditing ? $t('common.save') : $t('stories.addStory')) }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Slide Modal (Add Slide to Group) -->
    <Teleport to="body">
      <div v-if="showSlideModal" class="modal-overlay second-level" @click.self="showSlideModal = false">
        <div class="modal-panel animate-scale-in max-w-lg w-full m-4">
          <div class="modal-header-premium">
            <h3 class="m-0 text-thin">{{ $t('stories.modal.addSlide') }}</h3>
            <button class="btn btn-icon-only btn-ghost" @click="showSlideModal = false">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="modal-body-premium custom-scrollbar max-h-80vh">
            <div class="form-group mb-6">
              <label class="section-label mb-2">{{ $t('stories.form.slideTitle') }}</label>
              <div class="flex flex-column gap-2">
                <input v-model="slideForm.title.ru" type="text" placeholder="RU" class="input input-minimal">
                <input v-model="slideForm.title.uz" type="text" placeholder="UZ" class="input input-minimal">
                <input v-model="slideForm.title.en" type="text" placeholder="EN" class="input input-minimal">
              </div>
            </div>

            <div class="form-group mb-6">
              <label class="section-label mb-2">{{ $t('stories.form.content') }}</label>
              <div class="flex flex-column gap-2">
                <textarea v-model="slideForm.content.ru" placeholder="RU" class="input input-minimal"
                  rows="2"></textarea>
                <textarea v-model="slideForm.content.uz" placeholder="UZ" class="input input-minimal"
                  rows="2"></textarea>
                <textarea v-model="slideForm.content.en" placeholder="EN" class="input input-minimal"
                  rows="2"></textarea>
              </div>
            </div>

            <div class="form-group mb-6">
              <label class="section-label mb-2">{{ $t('stories.form.image') }}</label>
              <div class="flex gap-2 mb-2">
                <input type="file" ref="slideImageInput" @change="handleSlideImageUpload" accept="image/*"
                  class="input input-minimal w-full">
                <div v-if="uploadingSlideImage" class="flex-center px-2">
                  <div class="spinner-sm"></div>
                </div>
              </div>
              <input v-model="slideForm.image_url" type="text" placeholder="https://..."
                class="input input-minimal w-full">
              <div v-if="slideForm.image_url" class="mt-2">
                <img :src="slideForm.image_url" class="preview-thumb rounded">
              </div>
            </div>

            <div class="grid grid-2 gap-4">
              <div class="form-group">
                <label class="section-label mb-2">{{ $t('stories.form.btnText') }}</label>
                <input v-model="slideForm.button_text.ru" type="text" placeholder="RU"
                  class="input input-minimal w-full mb-1">
                <input v-model="slideForm.button_text.uz" type="text" placeholder="UZ"
                  class="input input-minimal w-full mb-1">
                <input v-model="slideForm.button_text.en" type="text" placeholder="EN"
                  class="input input-minimal w-full">
              </div>
              <div class="form-group">
                <label class="section-label mb-2">{{ $t('stories.form.link') }}</label>
                <input v-model="slideForm.button_link" type="text" placeholder="stlapp://catalog"
                  class="input input-minimal w-full">
                <label class="section-label mb-2 mt-4">{{ $t('stories.form.order') }}</label>
                <input v-model.number="slideForm.order" type="number" class="input input-minimal w-full">
              </div>
            </div>
          </div>
          <div class="modal-actions-premium">
            <button class="btn btn-ghost" @click="showSlideModal = false">{{ $t('common.cancel') }}</button>
            <button class="btn btn-primary" @click="handleSaveSlide" :disabled="savingSlide">
              {{ savingSlide ? $t('common.loading') : $t('stories.modal.addSlide') }}
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
const { getStories, createStory, updateStory, deleteStory, addSlide, deleteSlide, uploadStoryImage } = useApi()

const stories = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const savingSlide = ref(false)
const showStoryModal = ref(false)
const showSlideModal = ref(false)
const isEditing = ref(false)
const uploadingImage = ref(false)
const uploadingSlideImage = ref(false)
const storyImageInput = ref<HTMLInputElement | null>(null)
const slideImageInput = ref<HTMLInputElement | null>(null)

const initialStoryForm = {
  title: { ru: '', uz: '', en: '' },
  preview_image: '',
  order: 0,
  is_active: true,
  slides: []
}

const storyForm = ref<any>(JSON.parse(JSON.stringify(initialStoryForm)))

const initialSlideForm = {
  title: { ru: '', uz: '', en: '' },
  content: { ru: '', uz: '', en: '' },
  image_url: '',
  button_text: { ru: '', uz: '', en: '' },
  button_link: '',
  order: 0
}

const slideForm = ref<any>(JSON.parse(JSON.stringify(initialSlideForm)))

const fetchStoriesData = async () => {
  loading.value = true
  try {
    const res: any = await getStories()
    stories.value = res || []
  } catch (err) {
    console.error('Failed to fetch stories:', err)
  } finally {
    loading.value = false
  }
}

const getLocalizedTitle = (titleObj: any) => {
  if (!titleObj) return ''
  return titleObj[locale.value] || titleObj.ru || ''
}

const openCreateStory = () => {
  isEditing.value = false
  storyForm.value = JSON.parse(JSON.stringify(initialStoryForm))
  showStoryModal.value = true
}

const editStory = (story: any) => {
  isEditing.value = true
  storyForm.value = JSON.parse(JSON.stringify(story))
  showStoryModal.value = true
}

const handleStoryImageUpload = async (event: any) => {
  const file = event.target.files[0]
  if (!file) return

  uploadingImage.value = true
  try {
    const res: any = await uploadStoryImage(file)
    if (res && res.url) {
      storyForm.value.preview_image = res.url
    }
  } catch (err: any) {
    toast.error(t('common.error'), err?.message)
  } finally {
    uploadingImage.value = false
  }
}

const handleSlideImageUpload = async (event: any) => {
  const file = event.target.files[0]
  if (!file) return

  uploadingSlideImage.value = true
  try {
    const res: any = await uploadStoryImage(file)
    if (res && res.url) {
      slideForm.value.image_url = res.url
    }
  } catch (err: any) {
    toast.error(t('common.error'), err?.message)
  } finally {
    uploadingSlideImage.value = false
  }
}

const handleSaveStory = async () => {
  if (!storyForm.value.title.ru || !storyForm.value.preview_image) {
    toast.warning(t('common.warning'), 'Fill required fields (RU title)')
    return
  }

  saving.value = true
  try {
    if (isEditing.value) {
      await updateStory(storyForm.value.id, {
        title: storyForm.value.title,
        preview_image: storyForm.value.preview_image,
        order: storyForm.value.order,
        is_active: storyForm.value.is_active
      })
    } else {
      await createStory(storyForm.value)
    }
    showStoryModal.value = false
    fetchStoriesData()
    toast.success(t('common.success'))
  } catch (err: any) {
    toast.error(t('common.saveError'), err?.message)
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (story: any) => {
  if (confirm(t('stories.confirmDelete'))) {
    try {
      await deleteStory(story.id)
      fetchStoriesData()
      toast.success(t('common.success'))
    } catch (err: any) {
      toast.error(t('common.deleteError'), err?.message)
    }
  }
}

const openAddSlide = () => {
  slideForm.value = JSON.parse(JSON.stringify(initialSlideForm))
  showSlideModal.value = true
}

const handleSaveSlide = async () => {
  if (!slideForm.value.title.ru || !slideForm.value.content.ru || !slideForm.value.image_url) {
    toast.warning(t('common.warning'), 'Fill required fields (RU)')
    return
  }

  savingSlide.value = true
  try {
    const btnText = slideForm.value.button_text
    const hasBtnText = btnText.ru || btnText.uz || btnText.en

    const payload = {
      ...slideForm.value,
      button_text: hasBtnText ? btnText : null,
      button_link: slideForm.value.button_link || null
    }

    await addSlide(storyForm.value.id, payload)
    // Refresh slides
    const updatedRes: any = await getStories()
    const updatedStory = updatedRes.find((s: any) => s.id === storyForm.value.id)
    if (updatedStory) {
      // Update both list and form
      const idx = stories.value.findIndex(s => s.id === storyForm.value.id)
      if (idx !== -1) stories.value[idx] = updatedStory
      storyForm.value.slides = updatedStory.slides
    }
    showSlideModal.value = false
    toast.success(t('common.success'))
  } catch (err: any) {
    toast.error(t('common.saveError'), err?.message)
  } finally {
    savingSlide.value = false
  }
}

const handleDeleteSlide = async (slideId: string) => {
  if (confirm(t('stories.confirmDeleteSlide'))) {
    try {
      await deleteSlide(slideId)
      storyForm.value.slides = storyForm.value.slides.filter((s: any) => s.id !== slideId)
      // Sync main list
      const storyIdx = stories.value.findIndex(s => s.id === storyForm.value.id)
      if (storyIdx !== -1) {
        stories.value[storyIdx].slides = storyForm.value.slides
      }
      toast.success(t('common.success'))
    } catch (err: any) {
      toast.error(t('common.deleteError'))
    }
  }
}

onMounted(() => {
  fetchStoriesData()
})

definePageMeta({ layout: false })
</script>

<style scoped>
.page-header {
  padding: 2rem 0;
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 2rem;
}

.stories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.story-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.story-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.story-preview-bg {
  height: 180px;
  background-size: cover;
  background-position: center;
  position: relative;
  background-color: #f3f4f6;
}

.story-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
  padding: 1rem;
  display: flex;
  align-items: flex-end;
}

.order-badge {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: bold;
}

.side-panel {
  width: 100%;
  max-width: 500px;
  height: 100vh;
  background: var(--color-bg-primary);
  display: flex;
  flex-direction: column;
}

.side-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.side-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.side-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.badge-outline {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: white;
}

.modal-overlay.second-level {
  z-index: 3000;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-mini {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  padding: 10px;
  border-radius: 8px;
}

.mini-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
}

.preview-thumb {
  width: 100%;
  height: 100px;
  object-fit: cover;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.border-dashed-light {
  border: 1px dashed var(--color-border);
}

.max-h-80vh {
  max-height: 80vh;
}

.spinner-sm {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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

.modal-overlay.second-level {
  z-index: 3000;
  justify-content: center;
  align-items: center;
}

.animate-slide-in {
  animation: slideInRight 0.3s ease-out;
}

.animate-scale-in {
  animation: scaleIn 0.3s ease-out;
}

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

@keyframes scaleIn {
  from {
    transform: scale(0.95);
    opacity: 0;
  }

  to {
    transform: scale(1);
    opacity: 1;
  }
}

.modal-panel {
  background: var(--color-bg-primary);
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.2);
}

.modal-panel.side-panel {
  width: 100%;
  max-width: 500px;
  height: 100vh;
}

.modal-header-premium {
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body-premium {
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-actions-premium {
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}
</style>
