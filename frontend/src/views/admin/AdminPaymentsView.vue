<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Thanh toán</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Quản lý gói, coupon, giao dịch và đăng ký</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl w-fit" style="background-color: var(--color-surface-02)">
      <button
        v-for="tab in TABS"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="px-4 py-2 text-sm rounded-lg font-medium transition-all"
        :style="activeTab === tab.key
          ? 'background-color: var(--color-primary-500); color: #fff'
          : 'color: var(--color-text-muted)'"
      >{{ tab.label }}</button>
    </div>

    <!-- ── Plans ─────────────────────────────────────────────────────── -->
    <section v-if="activeTab === 'plans'">
      <div class="flex items-center justify-between mb-4">
        <span class="text-sm font-semibold" style="color: var(--color-text-base)">Gói đăng ký</span>
        <button @click="openPlanModal(null)" class="btn-primary text-sm px-4 py-2 rounded-lg">+ Thêm gói</button>
      </div>
      <div v-if="plansLoading" class="space-y-3">
        <div v-for="n in 3" :key="n" class="h-16 animate-pulse rounded-xl" style="background-color: var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border); color:var(--color-text-muted)">
              <th class="px-4 py-3">Tên</th>
              <th class="px-4 py-3">Giá (VND)</th>
              <th class="px-4 py-3">Thời hạn</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="plan in plans" :key="plan.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 font-medium" style="color:var(--color-text-base)">{{ plan.name }}</td>
              <td class="px-4 py-3" style="color:var(--color-text-base)">{{ formatVND(plan.price_vnd) }}</td>
              <td class="px-4 py-3" style="color:var(--color-text-muted)">{{ plan.duration_days }} ngày</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :style="plan.is_active ? 'background:#dcfce7;color:#166534' : 'background:#fee2e2;color:#991b1b'">
                  {{ plan.is_active ? 'Hoạt động' : 'Ẩn' }}
                </span>
              </td>
              <td class="px-4 py-3 flex gap-2">
                <button @click="openPlanModal(plan)" class="text-xs px-3 py-1 rounded-lg" style="background-color:var(--color-surface-03);color:var(--color-text-base)">Sửa</button>
                <button @click="deletePlan(plan)" class="text-xs px-3 py-1 rounded-lg text-red-500" style="background-color:var(--color-surface-03)">Xoá</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ── Coupons ────────────────────────────────────────────────────── -->
    <section v-if="activeTab === 'coupons'">
      <div class="flex items-center justify-between mb-4">
        <div class="flex gap-2">
          <input v-model="couponSearch" @input="loadCoupons" placeholder="Tìm mã coupon..." class="input-sm" />
        </div>
        <button @click="openCouponModal(null)" class="btn-primary text-sm px-4 py-2 rounded-lg">+ Thêm coupon</button>
      </div>
      <div v-if="couponsLoading" class="space-y-3">
        <div v-for="n in 4" :key="n" class="h-14 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Mã</th>
              <th class="px-4 py-3">Giảm</th>
              <th class="px-4 py-3">Đã dùng / Tối đa</th>
              <th class="px-4 py-3">Hết hạn</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in coupons" :key="c.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 font-mono font-bold" style="color:var(--color-primary-500)">{{ c.code }}</td>
              <td class="px-4 py-3" style="color:var(--color-text-base)">
                {{ c.discount_type === 'percent' ? c.discount_value + '%' : formatVND(c.discount_value) }}
              </td>
              <td class="px-4 py-3" style="color:var(--color-text-muted)">{{ c.used_count }} / {{ c.max_uses ?? '∞' }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ c.expires_at ? fmtDate(c.expires_at) : '—' }}</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :style="c.is_active ? 'background:#dcfce7;color:#166534' : 'background:#fee2e2;color:#991b1b'">
                  {{ c.is_active ? 'Hoạt động' : 'Vô hiệu' }}
                </span>
              </td>
              <td class="px-4 py-3 flex gap-2">
                <button @click="openCouponModal(c)" class="text-xs px-3 py-1 rounded-lg" style="background-color:var(--color-surface-03);color:var(--color-text-base)">Sửa</button>
                <button @click="deleteCoupon(c)" class="text-xs px-3 py-1 rounded-lg text-red-500" style="background-color:var(--color-surface-03)">Xoá</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ── Transactions ───────────────────────────────────────────────── -->
    <section v-if="activeTab === 'transactions'">
      <div class="flex flex-wrap gap-3 mb-4">
        <input v-model="txSearch" @input="loadTransactions" placeholder="Email / mã GD..." class="input-sm" />
        <select v-model="txStatus" @change="loadTransactions" class="input-sm">
          <option value="">Tất cả trạng thái</option>
          <option v-for="s in TX_STATUSES" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
      </div>
      <div v-if="txLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-x-auto" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm min-w-[640px]">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Người dùng</th>
              <th class="px-4 py-3">Gói</th>
              <th class="px-4 py-3">Số tiền</th>
              <th class="px-4 py-3">Cổng TT</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3">Thời gian</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tx in transactions" :key="tx.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ tx.user_email }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ tx.plan_name }}</td>
              <td class="px-4 py-3 font-medium" style="color:var(--color-text-base)">{{ formatVND(tx.amount_vnd) }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ tx.gateway }}</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium" :style="txStatusStyle(tx.status)">{{ tx.status }}</span>
              </td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ fmtDate(tx.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :pagination="txPagination" @change="loadTransactionPage" />
      </div>
    </section>

    <!-- ── Subscriptions ─────────────────────────────────────────────── -->
    <section v-if="activeTab === 'subscriptions'">
      <div class="flex flex-wrap gap-3 mb-4">
        <input v-model="subSearch" @input="loadSubscriptions" placeholder="Email người dùng..." class="input-sm" />
        <select v-model="subStatus" @change="loadSubscriptions" class="input-sm">
          <option value="">Tất cả</option>
          <option v-for="s in SUB_STATUSES" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
      </div>
      <div v-if="subLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-x-auto" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm min-w-[600px]">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Người dùng</th>
              <th class="px-4 py-3">Gói</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3">Hết hạn</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sub in subscriptions" :key="sub.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ sub.user_email }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ sub.plan_name }}</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium" :style="subStatusStyle(sub.status)">{{ sub.status }}</span>
              </td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ sub.expires_at ? fmtDate(sub.expires_at) : '—' }}</td>
              <td class="px-4 py-3">
                <button @click="openExtendModal(sub)" class="text-xs px-3 py-1 rounded-lg" style="background-color:var(--color-surface-03);color:var(--color-text-base)">Gia hạn</button>
              </td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :pagination="subPagination" @change="loadSubscriptionPage" />
      </div>
    </section>

    <!-- ── Plan Modal ─────────────────────────────────────────────────── -->
    <div v-if="planModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="w-full max-w-md rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="text-base font-bold" style="color:var(--color-text-base)">{{ planModal.item ? 'Sửa gói' : 'Thêm gói mới' }}</h3>
        <div class="space-y-3">
          <input v-model="planForm.name" placeholder="Tên gói*" class="input-base w-full" />
          <input v-model.number="planForm.price_vnd" type="number" placeholder="Giá (VND)*" class="input-base w-full" />
          <input v-model.number="planForm.duration_days" type="number" placeholder="Số ngày*" class="input-base w-full" />
          <textarea v-model="planForm.description" placeholder="Mô tả" rows="2" class="input-base w-full resize-none" />
          <label class="flex items-center gap-2 text-sm" style="color:var(--color-text-muted)">
            <input type="checkbox" v-model="planForm.is_active" />
            Hiển thị / Hoạt động
          </label>
        </div>
        <div class="flex gap-3 justify-end">
          <button @click="planModal.open = false" class="text-sm px-4 py-2 rounded-lg" style="background-color:var(--color-surface-02);color:var(--color-text-base)">Huỷ</button>
          <button @click="savePlan" :disabled="planSaving" class="btn-primary text-sm px-4 py-2 rounded-lg">
            {{ planSaving ? '...' : 'Lưu' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Coupon Modal ───────────────────────────────────────────────── -->
    <div v-if="couponModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="w-full max-w-md rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="text-base font-bold" style="color:var(--color-text-base)">{{ couponModal.item ? 'Sửa coupon' : 'Thêm coupon mới' }}</h3>
        <div class="space-y-3">
          <input v-model="couponForm.code" placeholder="Mã coupon (VD: SUMMER30)*" class="input-base w-full font-mono" />
          <select v-model="couponForm.discount_type" class="input-base w-full">
            <option value="percent">Giảm %</option>
            <option value="fixed_vnd">Giảm số tiền cố định</option>
          </select>
          <input v-model.number="couponForm.discount_value" type="number" placeholder="Giá trị giảm*" class="input-base w-full" />
          <input v-model.number="couponForm.max_uses" type="number" placeholder="Số lần dùng tối đa (bỏ trống = không giới hạn)" class="input-base w-full" />
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs mb-1 block" style="color:var(--color-text-muted)">Từ ngày</label>
              <input v-model="couponForm.valid_from" type="date" class="input-base w-full" />
            </div>
            <div>
              <label class="text-xs mb-1 block" style="color:var(--color-text-muted)">Hết hạn</label>
              <input v-model="couponForm.expires_at" type="date" class="input-base w-full" />
            </div>
          </div>
          <label class="flex items-center gap-2 text-sm" style="color:var(--color-text-muted)">
            <input type="checkbox" v-model="couponForm.is_active" />
            Kích hoạt coupon
          </label>
        </div>
        <div class="flex gap-3 justify-end">
          <button @click="couponModal.open = false" class="text-sm px-4 py-2 rounded-lg" style="background-color:var(--color-surface-02);color:var(--color-text-base)">Huỷ</button>
          <button @click="saveCoupon" :disabled="couponSaving" class="btn-primary text-sm px-4 py-2 rounded-lg">
            {{ couponSaving ? '...' : 'Lưu' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Extend Subscription Modal ─────────────────────────────────── -->
    <div v-if="extendModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="w-full max-w-sm rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="text-base font-bold" style="color:var(--color-text-base)">Gia hạn đăng ký</h3>
        <p class="text-sm" style="color:var(--color-text-muted)">{{ extendModal.sub?.user_email }}</p>
        <div>
          <label class="text-xs mb-1 block" style="color:var(--color-text-muted)">Số ngày gia hạn</label>
          <input v-model.number="extendDays" type="number" min="1" max="3650" class="input-base w-full" />
        </div>
        <div class="flex gap-3 justify-end">
          <button @click="extendModal.open = false" class="text-sm px-4 py-2 rounded-lg" style="background-color:var(--color-surface-02);color:var(--color-text-base)">Huỷ</button>
          <button @click="doExtend" :disabled="extendSaving" class="btn-primary text-sm px-4 py-2 rounded-lg">
            {{ extendSaving ? '...' : 'Gia hạn' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Refund Requests ──────────────────────────────────────────── -->
    <section v-if="activeTab === 'refunds'">
      <div class="flex items-center gap-3 mb-4 flex-wrap">
        <select v-model="refundStatusFilter" @change="loadRefunds" class="input-sm">
          <option value="">Mọi trạng thái</option>
          <option value="pending">Chờ duyệt</option>
          <option value="approved">Đã duyệt</option>
          <option value="rejected">Từ chối</option>
          <option value="completed">Hoàn tất</option>
        </select>
        <span class="text-xs ml-auto" style="color:var(--color-text-muted)">{{ refunds.length }} yêu cầu</span>
      </div>
      <div v-if="refundsLoading" class="space-y-3">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">#</th>
              <th class="px-4 py-3">Người dùng</th>
              <th class="px-4 py-3">Mã GD</th>
              <th class="px-4 py-3">Số tiền</th>
              <th class="px-4 py-3">Lý do</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3">Ngày tạo</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in refunds" :key="r.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 font-mono text-xs" style="color:var(--color-text-muted)">#{{ r.id }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ r.requested_by_email }}</td>
              <td class="px-4 py-3 font-mono text-xs" style="color:var(--color-text-muted)">{{ r.transaction_id }}</td>
              <td class="px-4 py-3 text-xs font-semibold" style="color:var(--color-text-base)">{{ formatVND(r.amount_vnd) }}</td>
              <td class="px-4 py-3 text-xs max-w-xs truncate" style="color:var(--color-text-muted)">{{ r.reason }}</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :style="{ pending: 'background:#fef9c3;color:#854d0e', approved: 'background:#dcfce7;color:#166534', rejected: 'background:#fee2e2;color:#991b1b', completed: 'background:#dbeafe;color:#1e40af' }[r.status] ?? ''">
                  {{ { pending: 'Chờ duyệt', approved: 'Đã duyệt', rejected: 'Từ chối', completed: 'Hoàn tất' }[r.status] ?? r.status }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ fmtDate(r.created_at) }}</td>
              <td class="px-4 py-3">
                <button v-if="r.status === 'pending'" class="text-xs px-3 py-1.5 rounded-lg hover:opacity-80"
                  style="background-color:var(--color-surface-03);color:var(--color-text-base)"
                  @click="Object.assign(refundModal, { open: true, item: r, action: 'approve', notes: '' })">Xử lý</button>
              </td>
            </tr>
            <tr v-if="!refunds.length">
              <td colspan="8" class="px-4 py-8 text-center text-sm" style="color:var(--color-text-muted)">Không có yêu cầu hoàn tiền nào.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Refund review modal -->
    <div v-if="refundModal.open" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,.5)">
      <div class="w-full max-w-md rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="font-bold text-base" style="color:var(--color-text-base)">Xử lý yêu cầu #{{ refundModal.item?.id }}</h3>
        <p class="text-sm" style="color:var(--color-text-muted)">Lý do: {{ refundModal.item?.reason }}</p>
        <p class="text-sm font-semibold" style="color:var(--color-text-base)">Số tiền: {{ formatVND(refundModal.item?.amount_vnd) }}</p>
        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Quyết định</label>
          <select v-model="refundModal.action" class="w-full text-sm rounded-xl px-3 py-2 border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)">
            <option value="approve">Duyệt (approve)</option>
            <option value="reject">Từ chối (reject)</option>
          </select>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Ghi chú (tuỳ chọn)</label>
          <textarea v-model="refundModal.notes" rows="2" class="w-full text-sm rounded-xl px-3 py-2 border resize-none" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" />
        </div>
        <div class="flex gap-2 justify-end">
          <button class="text-sm px-4 py-2 rounded-xl" style="background-color:var(--color-surface-02);color:var(--color-text-base)" @click="refundModal.open = false">Huỷ</button>
          <button :disabled="refundSaving" class="text-sm font-semibold px-4 py-2 rounded-xl hover:opacity-80 disabled:opacity-50"
            :style="refundModal.action === 'approve' ? 'background:#16a34a;color:#fff' : 'background:#dc2626;color:#fff'"
            @click="doReviewRefund">{{ refundSaving ? '...' : (refundModal.action === 'approve' ? 'Duyệt' : 'Từ chối') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { adminApi } from '@/api/admin.js'
import PaginationBar from '@/components/PaginationBar.vue'

const TABS = [
  { key: 'plans', label: 'Gói đăng ký' },
  { key: 'coupons', label: 'Coupon' },
  { key: 'transactions', label: 'Giao dịch' },
  { key: 'subscriptions', label: 'Đăng ký' },
  { key: 'refunds', label: 'Hoàn tiền' },
]
const TX_STATUSES = [
  { value: 'pending', label: 'Chờ xử lý' },
  { value: 'success', label: 'Thành công' },
  { value: 'failed', label: 'Thất bại' },
  { value: 'cancelled', label: 'Đã huỷ' },
  { value: 'refunded', label: 'Hoàn tiền' },
]
const SUB_STATUSES = [
  { value: 'trial', label: 'Dùng thử' },
  { value: 'active', label: 'Hoạt động' },
  { value: 'expired', label: 'Hết hạn' },
  { value: 'cancelled', label: 'Đã huỷ' },
  { value: 'paused', label: 'Tạm dừng' },
]

const activeTab = ref('plans')

// Plans
const plans = ref([])
const plansLoading = ref(false)
const planModal = reactive({ open: false, item: null })
const planForm = reactive({ name: '', price_vnd: 0, duration_days: 30, description: '', is_active: true })
const planSaving = ref(false)

// Coupons
const coupons = ref([])
const couponsLoading = ref(false)
const couponSearch = ref('')
const couponModal = reactive({ open: false, item: null })
const couponForm = reactive({ code: '', discount_type: 'percent', discount_value: 0, max_uses: null, valid_from: '', expires_at: '', is_active: true })
const couponSaving = ref(false)

// Transactions
const transactions = ref([])
const txLoading = ref(false)
const txSearch = ref('')
const txStatus = ref('')
const txPagination = reactive({ count: 0, next: null, previous: null, page: 1 })

// Subscriptions
const subscriptions = ref([])
const subLoading = ref(false)
const subSearch = ref('')
const subStatus = ref('')
const subPagination = reactive({ count: 0, next: null, previous: null, page: 1 })
const extendModal = reactive({ open: false, sub: null })
const extendDays = ref(30)
const extendSaving = ref(false)

// Refunds
const refunds = ref([])
const refundsLoading = ref(false)
const refundStatusFilter = ref('')
const refundModal = reactive({ open: false, item: null, action: 'approve', notes: '' })
const refundSaving = ref(false)

watch(activeTab, (tab) => {
  if (tab === 'plans' && plans.value.length === 0) loadPlans()
  if (tab === 'coupons' && coupons.value.length === 0) loadCoupons()
  if (tab === 'transactions' && transactions.value.length === 0) loadTransactions()
  if (tab === 'subscriptions' && subscriptions.value.length === 0) loadSubscriptions()
  if (tab === 'refunds' && refunds.value.length === 0) loadRefunds()
})

onMounted(() => loadPlans())

async function loadPlans() {
  plansLoading.value = true
  try { const r = await adminApi.getPlans(); plans.value = r.data.results ?? r.data }
  finally { plansLoading.value = false }
}
async function loadCoupons() {
  couponsLoading.value = true
  try { const r = await adminApi.getCoupons({ search: couponSearch.value }); coupons.value = r.data.results ?? r.data }
  finally { couponsLoading.value = false }
}
async function loadTransactions(page = 1) {
  txLoading.value = true
  try {
    const r = await adminApi.getTransactions({ search: txSearch.value, status: txStatus.value || undefined, page })
    transactions.value = r.data.results ?? r.data
    Object.assign(txPagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { txLoading.value = false }
}
async function loadSubscriptions(page = 1) {
  subLoading.value = true
  try {
    const r = await adminApi.getSubscriptions({ search: subSearch.value, status: subStatus.value || undefined, page })
    subscriptions.value = r.data.results ?? r.data
    Object.assign(subPagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { subLoading.value = false }
}
function loadTransactionPage(page) { loadTransactions(page) }
function loadSubscriptionPage(page) { loadSubscriptions(page) }

function openPlanModal(item) {
  planModal.item = item
  if (item) Object.assign(planForm, { name: item.name, price_vnd: item.price_vnd, duration_days: item.duration_days, description: item.description ?? '', is_active: item.is_active })
  else Object.assign(planForm, { name: '', price_vnd: 0, duration_days: 30, description: '', is_active: true })
  planModal.open = true
}
async function savePlan() {
  planSaving.value = true
  try {
    if (planModal.item) await adminApi.updatePlan(planModal.item.id, planForm)
    else await adminApi.createPlan(planForm)
    planModal.open = false
    await loadPlans()
  } finally { planSaving.value = false }
}
async function deletePlan(plan) {
  if (!confirm(`Xoá gói "${plan.name}"?`)) return
  await adminApi.deletePlan(plan.id)
  await loadPlans()
}

function openCouponModal(item) {
  couponModal.item = item
  if (item) Object.assign(couponForm, { code: item.code, discount_type: item.discount_type, discount_value: item.discount_value, max_uses: item.max_uses, valid_from: item.valid_from?.slice(0, 10) ?? '', expires_at: item.expires_at?.slice(0, 10) ?? '', is_active: item.is_active })
  else Object.assign(couponForm, { code: '', discount_type: 'percent', discount_value: 0, max_uses: null, valid_from: '', expires_at: '', is_active: true })
  couponModal.open = true
}
async function saveCoupon() {
  couponSaving.value = true
  try {
    const payload = { ...couponForm }
    if (!payload.max_uses) payload.max_uses = null
    if (!payload.valid_from) delete payload.valid_from
    if (!payload.expires_at) delete payload.expires_at
    if (couponModal.item) await adminApi.updateCoupon(couponModal.item.id, payload)
    else await adminApi.createCoupon(payload)
    couponModal.open = false
    await loadCoupons()
  } finally { couponSaving.value = false }
}
async function deleteCoupon(c) {
  if (!confirm(`Xoá coupon "${c.code}"?`)) return
  await adminApi.deleteCoupon(c.id)
  await loadCoupons()
}

function openExtendModal(sub) {
  extendModal.sub = sub
  extendDays.value = 30
  extendModal.open = true
}
async function doExtend() {
  extendSaving.value = true
  try {
    await adminApi.extendSubscription(extendModal.sub.id, extendDays.value)
    extendModal.open = false
    await loadSubscriptions()
  } finally { extendSaving.value = false }
}

async function loadRefunds() {
  refundsLoading.value = true
  try {
    const params = {}
    if (refundStatusFilter.value) params.status = refundStatusFilter.value
    const { data } = await adminApi.getRefundRequests(params)
    const payload = data.data ?? data
    refunds.value = payload.results ?? payload
  } catch { refunds.value = [] }
  finally { refundsLoading.value = false }
}

async function doReviewRefund() {
  refundSaving.value = true
  try {
    await adminApi.reviewRefund(refundModal.item.id, { action: refundModal.action, notes: refundModal.notes })
    refundModal.open = false
    await loadRefunds()
  } catch (e) {
    alert(e?.response?.data?.detail ?? 'Thao tác thất bại.')
  } finally { refundSaving.value = false }
}

function formatVND(n) { return Number(n).toLocaleString('vi-VN') + 'đ' }
function fmtDate(d) { return new Date(d).toLocaleDateString('vi-VN') }
function txStatusStyle(s) {
  const map = { success: 'background:#dcfce7;color:#166534', failed: 'background:#fee2e2;color:#991b1b', pending: 'background:#fef9c3;color:#854d0e', cancelled: 'background:#f3f4f6;color:#374151', refunded: 'background:#ede9fe;color:#5b21b6' }
  return map[s] ?? ''
}
function subStatusStyle(s) {
  const map = { active: 'background:#dcfce7;color:#166534', expired: 'background:#fee2e2;color:#991b1b', trial: 'background:#dbeafe;color:#1e40af', cancelled: 'background:#f3f4f6;color:#374151', paused: 'background:#fef9c3;color:#854d0e' }
  return map[s] ?? ''
}
</script>
