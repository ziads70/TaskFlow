from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Task(models.Model):

    class TaskType(models.TextChoices):
        ASSIGNMENT = "assignment", "واجب"
        QUIZ = "quiz", "كويز"
        MIDTERM = "midterm", "اختبار نصفي"
        FINAL = "final", "اختبار نهائي"
        PROJECT = "project", "مشروع"
        PRESENTATION = "presentation", "عرض تقديمي"
        EXAM = "exam", "اختبار"
        REVIEW = "review", "مراجعة"
        OTHER = "other", "أخرى"

    class Priority(models.TextChoices):
        LOW = "low", "منخفضة"
        MEDIUM = "medium", "متوسطة"
        HIGH = "high", "مرتفعة"
        URGENT = "urgent", "عاجلة"

    class Status(models.TextChoices):
        TODO = "todo", "لم تبدأ"
        IN_PROGRESS = "in_progress", "قيد التنفيذ"
        COMPLETED = "completed", "مكتملة"
        CANCELLED = "cancelled", "ملغاة"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="المستخدم",
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="المادة الدراسية",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان المهمة",
    )

    description = models.TextField(
        blank=True,
        verbose_name="وصف المهمة",
    )

    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.ASSIGNMENT,
        verbose_name="نوع المهمة",
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="الأولوية",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name="حالة المهمة",
    )

    due_date = models.DateTimeField(
        verbose_name="موعد التسليم",
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="تاريخ إكمال المهمة",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث",
    )

    class Meta:
        verbose_name = "مهمة"
        verbose_name_plural = "المهام"
        ordering = ["due_date", "-priority"]

        indexes = [
            models.Index(
                fields=["user", "status"],
                name="task_user_status_idx",
            ),
            models.Index(
                fields=["user", "due_date"],
                name="task_user_due_idx",
            ),
            models.Index(
                fields=["course", "status"],
                name="task_course_status_idx",
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if self.course_id and self.user_id:
            if self.course.user_id != self.user_id:
                raise ValidationError(
                    {
                        "course": (
                            "لا يمكن ربط المهمة بمادة "
                            "لا تخص المستخدم نفسه."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.status == self.Status.COMPLETED:
            if self.completed_at is None:
                self.completed_at = timezone.now()
        else:
            self.completed_at = None

        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED

    @property
    def is_overdue(self):
        inactive_statuses = {
            self.Status.COMPLETED,
            self.Status.CANCELLED,
        }

        return (
            self.status not in inactive_statuses
            and self.due_date < timezone.now()
        )
