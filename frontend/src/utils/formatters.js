/**
 * Vietnamese date/number/currency formatters.
 * Matches Django backend's Asia/Ho_Chi_Minh timezone output.
 */

const VN_DATE = new Intl.DateTimeFormat('vi-VN', {
  day: '2-digit', month: '2-digit', year: 'numeric',
  timeZone: 'Asia/Ho_Chi_Minh',
})

const VN_DATETIME = new Intl.DateTimeFormat('vi-VN', {
  day: '2-digit', month: '2-digit', year: 'numeric',
  hour: '2-digit', minute: '2-digit',
  timeZone: 'Asia/Ho_Chi_Minh',
})

const VN_CURRENCY = new Intl.NumberFormat('vi-VN', {
  style: 'currency', currency: 'VND',
})

const VN_NUMBER = new Intl.NumberFormat('vi-VN')

/**
 * "2026-03-24T09:00:00+07:00" → "24/03/2026"
 */
export function fmtDate(isoString) {
  if (!isoString) return '—'
  return VN_DATE.format(new Date(isoString))
}

/**
 * "2026-03-24T09:00:00+07:00" → "24/03/2026, 09:00"
 */
export function fmtDatetime(isoString) {
  if (!isoString) return '—'
  return VN_DATETIME.format(new Date(isoString))
}

/**
 * 199000 → "199.000 ₫"
 */
export function fmtCurrency(amount) {
  if (amount == null) return '—'
  return VN_CURRENCY.format(amount)
}

/**
 * 1200 → "1.200"
 */
export function fmtNumber(n) {
  if (n == null) return '0'
  return VN_NUMBER.format(n)
}

/**
 * 85.5 → "85,50"
 */
export function fmtScore(score) {
  if (score == null) return '—'
  return Number(score).toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

/**
 * 66.67 → "66,67%"
 */
export function fmtPercent(value) {
  if (value == null) return '0%'
  return Number(value).toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%'
}

/**
 * "2026-03-24T09:00:00+07:00" → "5 phút trước" / "2 giờ trước" / "24/03/2026"
 */
export function fmtRelative(isoString) {
  if (!isoString) return '—'
  const diff = Date.now() - new Date(isoString).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Vừa xong'
  if (mins < 60) return `${mins} phút trước`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} giờ trước`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} ngày trước`
  return fmtDate(isoString)
}
