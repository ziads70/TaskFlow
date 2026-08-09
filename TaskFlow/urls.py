from django.contrib import admin
from django.urls import include, path
from accounts.views import register, user_login
from notifications.views import home

admin.site.site_header = "إدارة TaskFlow"
admin.site.site_title = "لوحة إدارة TaskFlow"
admin.site.index_title = "مرحبًا بك في لوحة التحكم"

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("courses/", include("courses.urls")),
    path("tasks/", include("tasks.urls")),
    path("notifications/", include("notifications.urls")),
    path("dashboard/", include("dashboard.urls")),
]