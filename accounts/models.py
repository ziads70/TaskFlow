from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name="البريد الإلكتروني",
    )

    university = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="الجامعة",
    )

    major = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="التخصص",
    )

    profile_image = models.ImageField(
        upload_to="profiles/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="الصورة الشخصية",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ إنشاء الحساب",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث",
    )

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        return self.get_full_name() or self.username