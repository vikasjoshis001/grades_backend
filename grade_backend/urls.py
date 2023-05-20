"""grade_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import settings


from signup.views import signup_view, login_view, admin_list
from grades.views import department_list, semester_list, subject_list, user_grades_create, get_students_by_reviewer, get_user_grades, generate_pdf

from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/signup/', signup_view,
         name='signup_view'),
    path('api/login/', login_view, name='login-view'),
    path('api/admins/', admin_list, name='admin_list'),
    path('api/departments/', department_list, name='department-list'),
    path('api/semesters/', semester_list, name='semester-list'),
    path('api/grades/', user_grades_create, name='user-grades-create'),
    path('api/department/<int:department_id>/semester/<int:semester_id>/subjects/',
         subject_list, name='subject-list'),
    path('api/students/<int:reviewer_id>/', get_students_by_reviewer,
         name='get_students_by_reviewer'),
    path('api/student_grades/<int:user_id>/', get_user_grades,
         name='get_user_grades'),
    path('api/pdf/<int:user_id>/', generate_pdf,
         name='generate_pdf')
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
