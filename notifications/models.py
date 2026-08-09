from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        REMINDER = "reminder", "تذكير"
        DUE_SOON = "due_soon", "موعد قريب"
        OVERDUE = "overdue", "مهمة متأخرة"
        GENERAL = "general", "تنبيه عام"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="المستخدم",
    )

    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
        verbose_name="المهمة",
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.REMINDER,
        verbose_name="نوع التنبيه",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان التنبيه",
    )

    message = models.TextField(
        verbose_name="نص التنبيه",
    )

    scheduled_for = models.DateTimeField(
        default=timezone.now,
        verbose_name="موعد إرسال التنبيه",
    )

    is_sent = models.BooleanField(
        default=False,
        verbose_name="تم الإرسال",
    )

    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="وقت الإرسال الفعلي",
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name="تمت القراءة",
    )

    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="وقت القراءة",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء",
    )

    class Meta:
        verbose_name = "تنبيه"
        verbose_name_plural = "التنبيهات"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "is_read"],
                name="notify_user_read_idx",
            ),
            models.Index(
                fields=["is_sent", "scheduled_for"],
                name="notify_send_time_idx",
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if self.task_id and self.user_id:
            if self.task.user_id != self.user_id:
                raise ValidationError(
                    {
                        "task": (
                            "لا يمكن إنشاء تنبيه لمهمة "
                            "تخص مستخدمًا آخر."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.is_read:
            if self.read_at is None:
                self.read_at = timezone.now()
        else:
            self.read_at = None

        if self.is_sent:
            if self.sent_at is None:
                self.sent_at = timezone.now()
        else:
            self.sent_at = None

        super().save(*args, **kwargs)

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(
                update_fields=["is_read", "read_at"]
            )

    def mark_as_sent(self):
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(
                update_fields=["is_sent", "sent_at"]
            )

    @classmethod
    def create_task_reminder(cls, task, hours_before=24):
        if hours_before < 0:
            raise ValueError(
                "عدد الساعات قبل المهمة يجب ألا يكون سالبًا."
            )

        scheduled_time = task.due_date - timedelta(
            hours=hours_before
        )

        return cls.objects.create(
            user=task.user,
            task=task,
            notification_type=cls.NotificationType.REMINDER,
            title=f"تذكير: {task.title}",
            message=(
                f"اقترب موعد تسليم المهمة «{task.title}» "
                f"في مادة «{task.course.name}»."
            ),
            scheduled_for=scheduled_time,
        )