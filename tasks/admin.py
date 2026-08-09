from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    إعداد عرض وإدارة المهام داخل لوحة تحكم Django.
    """

    list_display = (
        "title",
        "user",
        "course",
        "task_type",
        "priority",
        "status",
        "due_date",
        "display_is_overdue",
    )

    list_filter = (
        "status",
        "priority",
        "task_type",
        "course",
        "due_date",
    )

    search_fields = (
        "title",
        "description",
        "course__name",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "completed_at",
    )

    ordering = (
        "due_date",
    )

    list_select_related = (
        "user",
        "course",
    )

    date_hierarchy = "due_date"

    @admin.display(
        boolean=True,
        description="متأخرة؟",
    )
    def display_is_overdue(self, obj):
        """
        يعرض ما إذا كانت المهمة متأخرة أم لا.
        """
        return obj.is_overdue