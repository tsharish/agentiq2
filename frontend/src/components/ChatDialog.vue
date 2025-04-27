<!-- eslint-disable @typescript-eslint/no-explicit-any -->
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { SSE } from 'sse.js'
import { getAccessToken } from '@/utils'
import ChatMessage from '@/components/ChatMessage.vue'

interface Message {
    role: string;
    content: string;
}

defineEmits(['close'])
const props = defineProps<{ visible: boolean }>()
const greeting = 'Hi, I am Agent IQ! How can I help you?'
const messages = ref<Message[]>([{ role: 'agent', content: greeting }])
const input = ref('')
const waiting = ref(false)
const session_id = ref<number | undefined>()
const chatContainer = ref<HTMLElement | null>(null)

async function send() {
    if (!input.value.trim()) return
    waiting.value = true
    const userInput = input.value
    input.value = ''
    messages.value.push({ role: 'user', content: userInput })

    const source = new SSE(import.meta.env.VITE_API_URL + '/chat', {
        headers: { 'Content-Type': 'application/json', 'Authorization': getAccessToken() },
        payload: JSON.stringify({ content: userInput, session_id: session_id.value })
    })

    source.addEventListener('message', (event: any) => {
        const response = JSON.parse(event.data)
        session_id.value = response.session_id
        messages.value.push({ role: 'agent', content: response.content })
    })

    source.addEventListener('readystatechange', (event: any) => {
        if (event.readyState === 2) {   // Connection is closed
            waiting.value = false
        }
    })

    source.addEventListener('error', (event: any) => {
        waiting.value = false
        console.log('Chat error:', event.data)
        messages.value.push({ role: 'agent', content: 'Sorry, something went wrong. Please try again.' })
    })
}

function newSession() {
    messages.value = [{ role: 'agent', content: greeting }]
    session_id.value = undefined
}

// Function to scroll to the bottom of the chat
function scrollToBottom() {
    nextTick(() => {
        if (chatContainer.value) {
            chatContainer.value.scrollTop = chatContainer.value.scrollHeight
        }
    })
}

// Watch messages and scroll when they change
watch(messages, scrollToBottom, { deep: true })
</script>

<template>
    <Dialog :visible="props.visible" position="bottomright" header="Agentiq Chat" :style="{ width: '25rem' }"
        @update:visible="$emit('close')">
        <div ref="chatContainer" class="chat-box">
            <ChatMessage v-for="message in messages" :role="message.role" :message="message.content.trim()"
                :key="message.content" />
            <div v-show="waiting" class="flex flex-row items-center rounded-md p-2 bg-blue-50 dark:bg-blue-950">
                <fa-icon icon="fa-solid fa-robot" class="text-blue-600 mr-4" />
                <Skeleton height="1.5rem" borderRadius="16px"></Skeleton>
            </div>
        </div>
        <template #footer>
            <div>
                <div class="flex items-end border-2 border-surface rounded-lg dark:bg-gray-950">
                    <Textarea v-model="input" rows="2" cols="40" autoResize fluid class="border-none outline-none" />
                    <Button rounded variant="text" @click="send" :disabled="waiting">
                        <fa-icon icon="fa-solid fa-arrow-up" />
                    </Button>
                </div>
                <Button label="New Session" variant="text" size="small" class="p-0 mt-3" @click="newSession" />
            </div>
        </template>
    </Dialog>
</template>

<style scoped>
.chat-box {
    max-height: 20rem;
    overflow-y: auto;
}
</style>
