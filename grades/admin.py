from django.contrib import admin

# Register your models here.
from .models import Departments, Semesters, Subjects

admin.site.register(Departments)
admin.site.register(Semesters)
admin.site.register(Subjects)


