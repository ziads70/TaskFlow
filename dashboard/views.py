from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Sum

from courses.forms import CourseForm
from courses.models import Course
from courses.models import GradeComponent
from tasks.models import Task
from .forms import CourseTaskForm, GradeComponentForm


@login_required
def dashboard(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            messages.success(request, 'تمت إضافة المادة بنجاح')
            return redirect('dashboard:dashboard')
    else:
        form = CourseForm()

    now = timezone.now()
    courses = Course.objects.filter(user=request.user, is_active=True)
    student_tasks = Task.objects.filter(user=request.user).select_related('course')
    upcoming_tasks = student_tasks.filter(
        due_date__gte=now,
    ).exclude(status=Task.Status.CANCELLED).order_by('due_date')[:8]
    past_tasks = student_tasks.filter(due_date__lt=now).order_by('-due_date')[:8]

    context = {
        'form': form,
        'courses': courses,
        'active_courses_count': courses.count(),
        'upcoming_tasks': upcoming_tasks,
        'past_tasks': past_tasks,
        'upcoming_tasks_count': student_tasks.filter(
            due_date__gte=now,
        ).exclude(status=Task.Status.CANCELLED).count(),
        'completed_tasks_count': student_tasks.filter(
            status=Task.Status.COMPLETED,
        ).count(),
        'today': timezone.localdate(),
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id, user=request.user)
    task_form = CourseTaskForm(prefix='task')
    grade_form = GradeComponentForm(prefix='grade', course=course)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_task':
            task_form = CourseTaskForm(request.POST, prefix='task')
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.user = request.user
                task.course = course
                task.save()
                messages.success(request, 'تمت إضافة الموعد بنجاح')
                return redirect('dashboard:course_detail', course_id=course.id)
        elif action == 'add_grade':
            grade_form = GradeComponentForm(request.POST, prefix='grade', course=course)
            if grade_form.is_valid():
                component = grade_form.save(commit=False)
                component.course = course
                component.save()
                messages.success(request, 'تمت إضافة بند الدرجات بنجاح')
                return redirect('dashboard:course_detail', course_id=course.id)

    now = timezone.now()
    course_tasks = Task.objects.filter(user=request.user, course=course)
    upcoming_tasks = course_tasks.filter(due_date__gte=now).exclude(
        status=Task.Status.CANCELLED,
    ).order_by('due_date')
    past_tasks = course_tasks.filter(due_date__lt=now).order_by('-due_date')
    grade_components = course.grade_components.all()
    grade_totals = grade_components.aggregate(
        allocated=Sum('weight'),
        earned=Sum('earned_score'),
    )
    allocated_grade = grade_totals['allocated'] or 0
    earned_grade = grade_totals['earned'] or 0

    context = {
        'course': course,
        'task_form': task_form,
        'grade_form': grade_form,
        'upcoming_tasks': upcoming_tasks,
        'past_tasks': past_tasks,
        'grade_components': grade_components,
        'allocated_grade': allocated_grade,
        'remaining_grade': 100 - allocated_grade,
        'earned_grade': earned_grade,
    }
    return render(request, 'dashboard/course_detail.html', context)
