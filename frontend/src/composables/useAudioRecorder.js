/**
 * useAudioRecorder
 * Wraps the MediaRecorder API for recording user speech.
 * Used by ShadowingPracticeView for self-recording.
 *
 * Usage:
 *   const { startRecording, stopRecording, isRecording, recordedUrl, recordDuration, reset } = useAudioRecorder()
 */
import { ref, onUnmounted } from 'vue'

export function useAudioRecorder() {
  const isRecording = ref(false)
  const recordedUrl = ref(null)
  const recordedBlob = ref(null)
  const recordDuration = ref(0)   // seconds elapsed
  const errorMessage = ref(null)

  let mediaRecorder = null
  let chunks = []
  let timerInterval = null
  let stream = null

  function _clearTimer() {
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }

  function _revokeUrl() {
    if (recordedUrl.value) {
      URL.revokeObjectURL(recordedUrl.value)
      recordedUrl.value = null
    }
  }

  async function startRecording() {
    errorMessage.value = null

    // Check browser support
    if (!navigator.mediaDevices?.getUserMedia) {
      errorMessage.value = 'Trình duyệt của bạn không hỗ trợ ghi âm.'
      return false
    }

    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      errorMessage.value = 'Không thể truy cập microphone. Vui lòng cấp quyền.'
      return false
    }

    _revokeUrl()
    chunks = []
    recordDuration.value = 0

    // Prefer opus/webm, fall back to browser default
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : ''

    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {})

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data)
    }

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: mediaRecorder.mimeType || 'audio/webm' })
      recordedBlob.value = blob
      recordedUrl.value = URL.createObjectURL(blob)
      // Stop all tracks to release the microphone
      stream?.getTracks().forEach((t) => t.stop())
      stream = null
    }

    mediaRecorder.start(100) // collect data every 100ms
    isRecording.value = true

    timerInterval = setInterval(() => {
      recordDuration.value += 1
    }, 1000)

    return true
  }

  function stopRecording() {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') return
    _clearTimer()
    mediaRecorder.stop()
    isRecording.value = false
  }

  function reset() {
    stopRecording()
    _revokeUrl()
    recordedBlob.value = null
    recordDuration.value = 0
    errorMessage.value = null
    chunks = []
  }

  onUnmounted(() => {
    reset()
  })

  return {
    startRecording,
    stopRecording,
    reset,
    isRecording,
    recordedUrl,
    recordedBlob,
    recordDuration,
    errorMessage,
  }
}
