<template>
  <main class="page-shell">
    <section class="profile-board">
      <aside class="identity-panel">
        <label class="avatar-uploader" title="点击更换头像">
          <img :src="profile.avatar" alt="头像" />
          <input type="file" accept="image/*" @change="onAvatarChange" />
        </label>

        <div class="name-block">
          <input v-model="profile.name" class="name-input" aria-label="姓名" />
          <input v-model="profile.role" class="role-input" aria-label="身份介绍" />
        </div>

        <div class="social-row" aria-label="社交链接">
          <button v-for="item in socialItems" :key="item.label" type="button" :title="item.label">
            <component :is="item.icon" :size="18" />
          </button>
        </div>

        <div class="quick-actions">
          <a :href="`mailto:${profile.email}`"><Mail :size="17" /> Email me</a>
          <a :href="`tel:${profile.phone}`"><Phone :size="17" /> 联系我</a>
        </div>

        <div class="side-note">
          <Sparkles :size="18" />
          <span>{{ profile.slogan }}</span>
        </div>
      </aside>

      <section class="content-panel">
        <header class="topbar">
          <div>
            <p class="eyebrow">Personal Homepage</p>
            <h1>个人主页</h1>
          </div>
          <div class="top-actions">
            <button type="button" class="ghost-btn" @click="resetDemo"><RotateCcw :size="17" /> 重置</button>
            <button type="button" class="primary-btn" @click="isEditing = !isEditing">
              <component :is="isEditing ? Eye : PenLine" :size="17" />
              {{ isEditing ? '预览主页' : '编辑主页' }}
            </button>
          </div>
        </header>

        <div class="intro-grid">
          <div class="intro-copy">
            <textarea v-if="isEditing" v-model="profile.bio" rows="4" aria-label="简介"></textarea>
            <p v-else>{{ profile.bio }}</p>
          </div>
          <div class="stat-strip">
            <div v-for="stat in profile.stats" :key="stat.label">
              <strong>{{ stat.value }}</strong>
              <span>{{ stat.label }}</span>
            </div>
          </div>
        </div>

        <div v-if="isEditing" class="editor-panel">
          <div class="field-grid">
            <label>姓名 <input v-model="profile.name" /></label>
            <label>身份 <input v-model="profile.role" /></label>
            <label>邮箱 <input v-model="profile.email" /></label>
            <label>电话 <input v-model="profile.phone" /></label>
            <label class="wide">签名 <input v-model="profile.slogan" /></label>
          </div>
          <div class="add-actions">
            <button type="button" @click="addTextBlock"><FileText :size="17" /> 添加文字</button>
            <label class="upload-btn"><ImagePlus :size="17" /> 添加图片<input type="file" accept="image/*" @change="addImageBlock" /></label>
          </div>
        </div>

        <section class="block-list" aria-label="主页内容">
          <article v-for="block in blocks" :key="block.id" class="content-card" :class="block.type">
            <div class="card-tools" v-if="isEditing">
              <button type="button" @click="moveBlock(block.id, -1)" title="上移"><ChevronUp :size="16" /></button>
              <button type="button" @click="moveBlock(block.id, 1)" title="下移"><ChevronDown :size="16" /></button>
              <button type="button" @click="removeBlock(block.id)" title="删除"><Trash2 :size="16" /></button>
            </div>

            <template v-if="block.type === 'text'">
              <input v-if="isEditing" v-model="block.title" class="block-title-input" aria-label="标题" />
              <h2 v-else>{{ block.title }}</h2>
              <textarea v-if="isEditing" v-model="block.text" rows="4" aria-label="内容"></textarea>
              <p v-else>{{ block.text }}</p>
            </template>

            <template v-else>
              <img :src="block.src" :alt="block.title" />
              <div class="image-caption">
                <input v-if="isEditing" v-model="block.title" aria-label="图片标题" />
                <h2 v-else>{{ block.title }}</h2>
                <textarea v-if="isEditing" v-model="block.text" rows="3" aria-label="图片说明"></textarea>
                <p v-else>{{ block.text }}</p>
              </div>
            </template>
          </article>
        </section>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import {
  AtSign,
  Award,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Code2,
  Eye,
  FileText,
  ImagePlus,
  Mail,
  PenLine,
  Phone,
  RotateCcw,
  Sparkles,
  Trash2,
  UserRound,
} from '@lucide/vue'

const STORAGE_KEY = 'editable-personal-homepage-v1'

const defaultState = {
  profile: {
    name: '环己烷',
    role: '个人主页',
    email: 'hello@example.com',
    phone: '18297732366',
    slogan: '把每天的灵感记录下来。',
    avatar:
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180"><rect width="180" height="180" rx="48" fill="%23ffffff"/><text x="50%25" y="52%25" dominant-baseline="middle" text-anchor="middle" font-size="72" font-family="Arial" fill="%23252b36">弓</text></svg>',
    bio: '现在过的每一天，都是余生中最年轻的一天。所以趁着年轻，多去拥抱美好吧！这里可以自由编辑简介、添加文字和上传图片。',
    stats: [
      { value: '12', label: '作品' },
      { value: '38', label: '记录' },
      { value: '8', label: '证书' },
    ],
  },
  blocks: [
    {
      id: 1,
      type: 'text',
      title: '荣誉证书',
      text: '这里可以记录荣誉、证书、学习经历或项目成果。点击“编辑主页”后可以直接修改这段文字。',
    },
    {
      id: 2,
      type: 'text',
      title: '关于我',
      text: '热爱设计和前端开发，喜欢把想法做成真实可用的页面。这个主页不需要数据库，所有内容会保存在浏览器本地。',
    },
  ],
}

const saved = localStorage.getItem(STORAGE_KEY)
const initialState = saved ? JSON.parse(saved) : defaultState
const profile = ref(structuredClone(initialState.profile))
const blocks = ref(structuredClone(initialState.blocks))
const isEditing = ref(true)

const socialItems = computed(() => [
  { label: '社交', icon: AtSign },
  { label: '博客', icon: BookOpen },
  { label: '代码', icon: Code2 },
  { label: '荣誉', icon: Award },
])

watch(
  [profile, blocks],
  () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ profile: profile.value, blocks: blocks.value }),
    )
  },
  { deep: true },
)

function readImage(file, callback) {
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => callback(reader.result)
  reader.readAsDataURL(file)
}

function onAvatarChange(event) {
  readImage(event.target.files?.[0], (src) => {
    profile.value.avatar = src
    event.target.value = ''
  })
}

function addImageBlock(event) {
  readImage(event.target.files?.[0], (src) => {
    blocks.value.unshift({
      id: Date.now(),
      type: 'image',
      title: '新的图片',
      text: '写一点关于这张图片的介绍。',
      src,
    })
    event.target.value = ''
  })
}

function addTextBlock() {
  blocks.value.unshift({
    id: Date.now(),
    type: 'text',
    title: '新的文字模块',
    text: '在这里写下新的经历、想法或作品说明。',
  })
}

function removeBlock(id) {
  blocks.value = blocks.value.filter((block) => block.id !== id)
}

function moveBlock(id, direction) {
  const index = blocks.value.findIndex((block) => block.id === id)
  const target = index + direction
  if (target < 0 || target >= blocks.value.length) return
  const next = [...blocks.value]
  const [item] = next.splice(index, 1)
  next.splice(target, 0, item)
  blocks.value = next
}

function resetDemo() {
  profile.value = structuredClone(defaultState.profile)
  blocks.value = structuredClone(defaultState.blocks)
}
</script>




