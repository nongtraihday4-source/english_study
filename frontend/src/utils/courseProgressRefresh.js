const COURSE_REFRESH_KEY = 'course-detail-refresh'

export function writeCourseRefreshMarker(payload = {}) {
  const courseId = payload?.courseId ?? payload?.course_id
  if (!courseId) return
  const normalized = {
    courseId,
    chapterId: payload?.chapterId ?? payload?.chapter_id ?? null,
    nextLessonId: payload?.nextLessonId ?? payload?.next_lesson_id ?? null,
    courseCompleted: !!(payload?.courseCompleted ?? payload?.course_completed),
    chapterCompleted: !!(payload?.chapterCompleted ?? payload?.chapter_completed),
    chapterTitle: payload?.chapterTitle ?? payload?.chapter_title ?? '',
    chapterAvgScore: payload?.chapterAvgScore ?? payload?.chapter_avg_score ?? null,
    timestamp: Date.now(),
  }
  sessionStorage.setItem(COURSE_REFRESH_KEY, JSON.stringify(normalized))
}

export function readCourseRefreshMarker() {
  try {
    const raw = sessionStorage.getItem(COURSE_REFRESH_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function clearCourseRefreshMarker() {
  sessionStorage.removeItem(COURSE_REFRESH_KEY)
}

export { COURSE_REFRESH_KEY }