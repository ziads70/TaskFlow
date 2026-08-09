from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "university",
        "major",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
        "date_joined",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "university",
        "major",
    )

    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "معلومات TaskFlow",
            {
                "fields": (
                    "university",
                    "major",
                    "profile_image",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "معلومات إضافية",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "university",
                    "major",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )