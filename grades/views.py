from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Departments, Semesters, Subjects, UserGrades
from signup.models import Signup
from .serializers import DepartmentSerializer, SemesterSerializer, SubjectSerializer, UserGradesSerializer
# Create your views here.


@api_view(['GET'])
def department_list(request):
    departments = Departments.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def semester_list(request):
    semesters = Semesters.objects.all()
    serializer = SemesterSerializer(semesters, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def subject_list(request, department_id, semester_id):
    subjects = Subjects.objects.filter(
        department=department_id, semester=semester_id)
    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def user_grades_create(request):
    department_id = request.data.get('department_id')
    semester_id = request.data.get('semester_id')
    user_id = request.data.get('user_id')
    reviewer_id = request.data.get('reviewer_id')
    grades_data = request.data.get('grades')

    user_grades_list = []
    for grade_data in grades_data:
        subject_id = grade_data.get('subject')
        grade = grade_data.get('grade')

        # Check if the user grade already exists
        user_grade, _ = UserGrades.objects.update_or_create(
            user_id=user_id,
            department_id=department_id,
            semester_id=semester_id,
            subject_id=subject_id,
            defaults={
                'grades': grade,
                'reviewer': reviewer_id
            }
        )
        user_grades_list.append(user_grade)

    return Response({'message': 'User grades created/updated successfully.'}, status=status.HTTP_201_CREATED)
