from django.db import models

from signup.models import Signup

from django.conf import settings

from django.core.files.storage import FileSystemStorage

import os


class Departments(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Semesters(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Subjects(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semesters, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserGrades(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        Signup, on_delete=models.CASCADE, related_name="grades_given")
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semesters, on_delete=models.CASCADE)
    grades = models.CharField(max_length=100)
    reviewer = models.ForeignKey(
        Signup, on_delete=models.CASCADE, related_name="approved_by")

    def __str__(self):
        return self.user.name

    class Meta:
        unique_together = [['user', 'department', 'semester', 'subject']]


class SavePdf(models.Model):
    filename = models.CharField(max_length=120)
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True)


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class ResultFiles(models.Model):
    xlsx_files = models.FileField(storage=OverwriteStorage())
