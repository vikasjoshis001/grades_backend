from django.db import models

from signup.models import Signup


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
