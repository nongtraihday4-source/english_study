from django.contrib import admin

from apps.support.models import PublicSupportRequest, RefundRequest, SupportTicket, TicketMessage


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ["id", "subject", "category", "priority", "status", "user", "assigned_to", "created_at"]
    list_filter = ["status", "category", "priority"]
    search_fields = ["subject", "user__email"]
    raw_id_fields = ["user", "assigned_to", "created_by"]


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "ticket", "author", "is_internal", "created_at"]
    list_filter = ["is_internal"]
    raw_id_fields = ["ticket", "author"]


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "transaction", "amount_vnd", "status", "requested_by", "reviewed_by", "created_at"]
    list_filter = ["status"]
    raw_id_fields = ["transaction", "requested_by", "reviewed_by"]


@admin.register(PublicSupportRequest)
class PublicSupportRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "full_name",
        "issue_type",
        "status",
        "linked_user",
        "linked_ticket",
        "created_at",
    ]
    list_filter = ["issue_type", "status", "is_authenticated_submission"]
    search_fields = ["full_name", "email", "phone", "subject"]
    raw_id_fields = ["linked_user", "linked_ticket", "triaged_by"]
