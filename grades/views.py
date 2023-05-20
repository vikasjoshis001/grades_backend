from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
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
                'reviewer_id': reviewer_id
            }
        )
        user_grades_list.append(user_grade)

    return Response({'message': 'User grades created/updated successfully.'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_students_by_reviewer(request, reviewer_id):
    # Retrieve the UserGrades objects for the given reviewer_id
    user_grades = UserGrades.objects.filter(
        reviewer_id=reviewer_id)
    print(user_grades)

    # Create the payload using Signup and UserGrades data
    students = []
    for user_grade in user_grades:
        print(user_grade)
        student = {
            'id': user_grade.user.id,
            'name': user_grade.user.name,
            'reg_no': user_grade.user.reg_no
        }
        students.append(student)

    payload = {'students': students}

    return Response(payload)


@require_GET
def get_user_grades(request, user_id):
    user = get_object_or_404(Signup, id=user_id)

    payload = {
        "user_name": user.name,
        "department": user.department,
        "grades": {}
    }

    user_grades = UserGrades.objects.filter(user=user)

    for grade in user_grades:
        semester_name = grade.semester.name
        subject_name = grade.subject.name
        grade_value = grade.grades

        if semester_name not in payload["grades"]:
            payload["grades"][semester_name] = []

        payload["grades"][semester_name].append({
            "subject": subject_name,
            "grades": grade_value
        })

    return JsonResponse(payload)
