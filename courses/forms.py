from django import forms
from .models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'name',
            'code',
            'description',
            'semester',
            'academic_year',
            'color',
            'is_active',
        )
        labels = {
            'name': 'اسم المادة',
            'code': 'رمز المادة',
            'description': 'وصف المادة',
            'semester': 'الفصل الدراسي',
            'academic_year': 'السنة الدراسية',
            'color': 'لون المادة',
            'is_active': 'نشطة',
        }
