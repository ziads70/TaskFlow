from django.conf import settings
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


hex_color_validator = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message="يجب إدخال اللون بصيغة صحيحة مثل #2563EB.",
)


class Course(models.Model):
    """
    يمثل مادة دراسية يملكها مستخدم واحد.
    """

    class Semester(models.TextChoices):
        FIRST = "first", "الفصل الأول"
        SECOND = "second", "الفصل الثاني"
        SUMMER = "summer", "الفصل الصيفي"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="المستخدم",
    )

    name = models.CharField(
        max_length=150,
        verbose_name="اسم المادة",
    )

    code = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="رمز المادة",
        help_text="مثال: CSCI-301",
    )

    description = models.TextField(
        blank=True,
        verbose_name="وصف المادة",
    )

    semester = models.CharField(
        max_length=20,
        choices=Semester.choices,
        default=Semester.FIRST,
        verbose_name="الفصل الدراسي",
    )

    academic_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="السنة الدراسية",
        help_text="مثال: 2026",
    )

    color = models.CharField(
        max_length=7,
        default="#2563EB",
        validators=[hex_color_validator],
        verbose_name="لون المادة",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="مادة نشطة",
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
        verbose_name = "مادة دراسية"
        verbose_name_plural = "المواد الدراسية"
        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "name",
                    "semester",
                    "academic_year",
                ],
                name="unique_course_per_user_semester_year",
            ),
        ]

        indexes = [
            models.Index(
                fields=["user", "is_active"],
                name="course_user_active_idx",
            ),
        ]

    def __str__(self):
        if self.code:
            return f"{self.name} ({self.code})"

        return self.name


class GradeComponent(models.Model):
    """جزء من توزيع درجات مادة، مثل الكويزات أو الاختبار النهائي."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="grade_components",
        verbose_name="المادة",
    )
    name = models.CharField(max_length=100, verbose_name="بند التقييم")
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100)],
        verbose_name="الدرجة المخصصة",
    )
    earned_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="درجتي",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "بند درجات"
        verbose_name_plural = "توزيع الدرجات"

    def __str__(self):
        return f"{self.name} ({self.weight})"

    def clean(self):
        super().clean()
        if self.earned_score is not None and self.earned_score > self.weight:
            from django.core.exceptions import ValidationError
            raise ValidationError({"earned_score": "لا يمكن أن تكون درجتك أكبر من الدرجة المخصصة."})
