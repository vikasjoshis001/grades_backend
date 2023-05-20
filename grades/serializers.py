from rest_framework import serializers
from .models import Departments, Semesters, Subjects, UserGrades


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = ['id', 'name', 'abbreviation']


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semesters
        fields = ['id', 'name', 'abbreviation']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['id', 'name', 'type', 'department', 'semester']


class UserGradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGrades
        fields = '__all__'
