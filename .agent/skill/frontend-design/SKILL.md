---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

---

## English Study Project — Art Direction (Overrides above when working on this project)

Khi làm việc trên dự án **English Study LMS**, phải tuân thủ Art Direction cụ thể trong PRD. Đây không phải là creative freedom — đây là brand identity đã được định nghĩa:

### Design System

| Token | Giá trị |
|-------|---------|
| Background | Off-white `#F8F7F4` (light) / Deep Navy `#0F1724` (dark) |
| Primary Accent | Electric Blue `#3B82F6` |
| Secondary Accent | Warm Amber `#F59E0B` (success/pass), Red `#EF4444` (fail) |
| Surface | Glassmorphism card: `bg-white/60 backdrop-blur-md border border-white/20 shadow-soft` |
| Text Primary | `#1E293B` (light) / `#F1F5F9` (dark) |
| Border Radius | Cards: `rounded-2xl`. Buttons: `rounded-xl`. Inputs: `rounded-lg` |

### Typography
- **Display/Headings**: `Nunito` (rounded, approachable — học tiếng Anh phải friendly)
- **Body**: `Inter` (đọc trên màn hình lâu — readability trên hết)
- **Monospace** (code/phonetics): `JetBrains Mono`

> ⚠️ Đây là exception: dù guideline trên nói "avoid Inter", trong project này Inter là bắt buộc cho body text vì được chỉ định trong PRD.

### Component Patterns
- **Cards**: Glassmorphism — semi-transparent, backdrop blur, subtle border
- **Buttons**: Gradient fill cho CTA chính (`from-blue-500 to-blue-600`), hover scale `1.02`
- **Micro-animations**: `transition-all duration-200`. Progress bars animate on mount.
- **Dark Mode**: Tất cả component PHẢI hỗ trợ Dark Mode via Tailwind `dark:` classes
- **Exercise Split Pane**: Layout 6:4 (content : exercise panel), divider có thể drag

### Implementation Stack
- TailwindCSS 3 utility classes (không viết custom CSS trừ khi cần animation phức tạp)
- Vue 3 `<script setup>` + Composition API
- Không dùng Bootstrap, không dùng Vuetify, không dùng Element Plus