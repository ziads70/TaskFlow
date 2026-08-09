from decimal import Decimal

from django import forms
from django.db.models import Sum

from courses.models import GradeComponent
from tasks.models import Task
     

class CourseTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "task_type", "due_date", "priority", "description")
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }
   

class GradeComponentForm(forms.ModelForm):
    class Meta:
        model = GradeComponent
        fields = ("name", "weight", "earned_score")
        widgets = {
            "weight": forms.NumberInput(attrs={"min": "0.01", "max": "100", "step": "0.01"}),
            "earned_score": forms.NumberInput(attrs={"min": "0", "max": "100", "step": "0.01"}),
        }

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.course = course

    def clean_weight(self):
        weight = self.cleaned_data["weight"]
        allocated = self.course.grade_components.aggregate(total=Sum("weight"))["total"] or Decimal("0")
        if allocated + weight > Decimal("100"):
            remaining = Decimal("100") - allocated
            raise forms.ValidationError(f"المتبقي من توزيع المادة هو {remaining:g} فقط.")
        return weight
