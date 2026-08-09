from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from courses.models import Course
from courses.models import GradeComponent
from tasks.models import Task


class DashboardRouteTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)

    def test_dashboard_is_available_after_login(self):
        user = get_user_model().objects.create_user(
            username='dashuser',
            email='dash@example.com',
            password='StrongPass123'
        )
        self.client.force_login(user)
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_splits_upcoming_and_past_dates(self):
        user = get_user_model().objects.create_user(
            username='student', email='student-dashboard@example.com', password='StrongPass123'
        )
        course = Course.objects.create(user=user, name='الرياضيات')
        upcoming = Task.objects.create(
            user=user, course=course, title='اختبار قادم',
            due_date=timezone.now() + timedelta(days=2),
        )
        past = Task.objects.create(
            user=user, course=course, title='واجب سابق',
            due_date=timezone.now() - timedelta(days=2),
        )
        self.client.force_login(user)

        response = self.client.get('/dashboard/')

        self.assertContains(response, upcoming.title)
        self.assertContains(response, past.title)
        self.assertQuerySetEqual(response.context['upcoming_tasks'], [upcoming])
        self.assertQuerySetEqual(response.context['past_tasks'], [past])

    def test_student_can_add_course_date_and_grade_component(self):
        user = get_user_model().objects.create_user(
            username='courseowner', email='owner@example.com', password='StrongPass123'
        )
        course = Course.objects.create(user=user, name='الفيزياء')
        self.client.force_login(user)
        detail_url = f'/dashboard/course/{course.id}/'

        task_response = self.client.post(detail_url, {
            'action': 'add_task',
            'task-title': 'الميد الأول',
            'task-task_type': Task.TaskType.MIDTERM,
            'task-due_date': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M'),
            'task-priority': Task.Priority.HIGH,
            'task-description': '',
        })
        grade_response = self.client.post(detail_url, {
            'action': 'add_grade',
            'grade-name': 'الميد الأول',
            'grade-weight': '30',
            'grade-earned_score': '25',
        })

        self.assertEqual(task_response.status_code, 302)
        self.assertEqual(grade_response.status_code, 302)
        self.assertTrue(Task.objects.filter(course=course, title='الميد الأول').exists())
        self.assertTrue(GradeComponent.objects.filter(course=course, weight=30).exists())

    def test_grade_distribution_cannot_exceed_one_hundred(self):
        user = get_user_model().objects.create_user(
            username='gradesowner', email='grades@example.com', password='StrongPass123'
        )
        course = Course.objects.create(user=user, name='الكيمياء')
        GradeComponent.objects.create(course=course, name='النهائي', weight=70)
        self.client.force_login(user)

        response = self.client.post(f'/dashboard/course/{course.id}/', {
            'action': 'add_grade',
            'grade-name': 'الميد',
            'grade-weight': '40',
            'grade-earned_score': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(course.grade_components.count(), 1)
        self.assertContains(response, 'المتبقي من توزيع المادة هو 30 فقط')
