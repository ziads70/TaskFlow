from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    إعداد إدارة التنبيهات داخل لوحة تحكم Django.
    """

    list_display = (
        "title",
        "user",
        "task",
        "notification_type",
        "scheduled_for",
        "is_sent",
        "is_read",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "is_sent",
        "is_read",
        "scheduled_for",
        "created_at",
    )

    search_fields = (
        "title",
        "message",
        "user__username",
        "user__email",
        "task__title",
    )

    readonly_fields = (
        "created_at",
        "sent_at",
        "read_at",
    )

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "user",
        "task",
    )

    date_hierarchy = "created_at"