---
trigger: always_on
---

# Frontend Development Rules

## Tài khoản tester frontend:
- email: admin@gmail.com
- password: TestPass@123

## Tech Stack
- Framework: Vue.js 3 + Vite
- API Style: Composition API (sử dụng `<script setup>`)
- Ngôn ngữ: Vanilla JavaScript (JS thuần), **KHÔNG SỬ DỤNG TypeScript**.
- CSS Framework: **TailwindCSS 3** (utility-first, mobile-first responsive)
- State Management: **Pinia** stores
- Routing: **Vue Router 4** (hash mode hoặc history mode)
- HTTP Client: **Axios** với interceptors cho JWT auth
- Charts: **Chart.js** + **vue-chartjs** (Radar Chart 4 kỹ năng, Progress charts)

## Architecture Patterns

### Component Structure
```
src/
├── api/            # Axios modules: auth.js, courses.js, exercises.js, ...
├── assets/         # Static assets (images, fonts)
├── components/     # Reusable components
│   ├── common/     # Button, Modal, Toast, LoadingSpinner
│   ├── exercise/   # MCQuestion, GapFill, DragDrop, SplitPane
│   ├── audio/      # AudioPlayer, WaveformRecorder, KaraokeText
│   └── layout/     # Navbar, Sidebar, Footer
├── composables/    # Composition API hooks: useAuth, useExercise, useSpeaking, ...
├── stores/         # Pinia: auth.js, course.js, progress.js, notification.js
├── views/          # Page-level: DashboardView, LessonView, ExerciseView, ...
├── router/         # Route definitions + navigation guards
└── utils/          # formatDate, formatNumber (vi-VN), scoreCalculator
```

### Naming Conventions
- Components: **PascalCase** (`AudioPlayer.vue`, `ExerciseCard.vue`)
- Composables: **camelCase** với prefix `use` (`useAuth.js`, `useExercise.js`)
- Stores: **camelCase** (`auth.js`, `courseProgress.js`)
- API modules: **camelCase** (`auth.js`, `exercises.js`)
- Views: **PascalCase** với suffix `View` (`DashboardView.vue`, `LessonView.vue`)

### State Management (Pinia)
- Mỗi domain 1 store: `useAuthStore`, `useCourseStore`, `useProgressStore`
- Store chỉ chứa state + actions gọi API. Không chứa business logic phức tạp.
- Composables wrap store actions khi cần logic UI phức tạp.

### API Layer
- Mỗi module API (auth.js, courses.js) export các hàm async gọi axios.
- Axios instance chung với baseURL, JWT interceptor (auto-refresh token).
- Error handling: axios response interceptor → redirect login khi 401.

## Constraints & Anti-patterns (Tuyệt đối tuân thủ)
1. **KHÔNG BAO GIỜ** sử dụng React, JSX, hoặc các pattern của React trong dự án này.
2. **KHÔNG BAO GIỜ** sử dụng TypeScript (`.ts`, `.tsx`) hoặc viết các interface/type định nghĩa của TS. Chỉ sử dụng `.js` và `.vue`.
3. Luôn sử dụng Composition API cho các component mới thay vì Options API của Vue 2.
4. Ưu tiên sử dụng `ref` và `reactive` cho state management trong component, `Pinia` cho global state.
5. **KHÔNG** sử dụng Bootstrap 5. Project dùng **TailwindCSS** làm CSS framework chính.
6. Mọi datetime hiển thị phải format theo timezone `Asia/Ho_Chi_Minh`.
7. Mọi số hiển thị phải format theo locale `vi-VN` (dấu chấm phân cách hàng nghìn).

## Backend Context
- Backend sử dụng Django + DRF. Frontend giao tiếp hoàn toàn qua REST API.
- Auth: JWT (access + refresh token) lưu trong localStorage hoặc httpOnly cookie.
- API Base URL: cấu hình qua Vite env variable `VITE_API_BASE_URL`.