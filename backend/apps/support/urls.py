from django.urls import path

from apps.support.views import (
    PublicSupportRequestCreateView,
    SupportCouponListView,
    SupportDashboardView,
    SupportPasswordResetView,
    SupportPublicRequestConvertView,
    SupportPublicRequestListView,
    SupportRefundRequestDetailView,
    SupportRefundRequestListView,
    SupportSubscriptionListView,
    SupportTicketAssignView,
    SupportTicketDetailView,
    SupportTicketListView,
    SupportTicketMessageView,
    SupportTransactionListView,
    SupportUserDetailView,
    SupportUserLookupView,
)

urlpatterns = [
    # Public support request (no login required)
    path("public/requests/", PublicSupportRequestCreateView.as_view(), name="public-support-request-create"),

    # Dashboard
    path("dashboard/", SupportDashboardView.as_view(), name="support-dashboard"),

    # Public request inbox for support staff
    path("public-requests/", SupportPublicRequestListView.as_view(), name="support-public-requests"),
    path("public-requests/<int:pk>/convert/", SupportPublicRequestConvertView.as_view(), name="support-public-request-convert"),

    # User lookup (read-only)
    path("users/", SupportUserLookupView.as_view(), name="support-users"),
    path("users/<int:pk>/", SupportUserDetailView.as_view(), name="support-user-detail"),
    path("users/<int:pk>/reset-password/", SupportPasswordResetView.as_view(), name="support-user-reset-password"),

    # Tickets
    path("tickets/", SupportTicketListView.as_view(), name="support-tickets"),
    path("tickets/<int:pk>/", SupportTicketDetailView.as_view(), name="support-ticket-detail"),
    path("tickets/<int:pk>/messages/", SupportTicketMessageView.as_view(), name="support-ticket-messages"),
    path("tickets/<int:pk>/assign/", SupportTicketAssignView.as_view(), name="support-ticket-assign"),

    # Payments (read-only)
    path("transactions/", SupportTransactionListView.as_view(), name="support-transactions"),
    path("subscriptions/", SupportSubscriptionListView.as_view(), name="support-subscriptions"),
    path("coupons/", SupportCouponListView.as_view(), name="support-coupons"),

    # Refund requests
    path("refund-requests/", SupportRefundRequestListView.as_view(), name="support-refund-requests"),
    path("refund-requests/<int:pk>/", SupportRefundRequestDetailView.as_view(), name="support-refund-request-detail"),
]
