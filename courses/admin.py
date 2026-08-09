from django.contrib import admin

from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "user",
        "semester",
        "academic_year",
        "is_active",
        "created_at",
    )

    list_filter = (
        "semester",
        "academic_year",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("name",)

    list_select_related = ("user",)