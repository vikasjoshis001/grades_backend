from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Departments, Semesters, Subjects
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
    subjects = Subjects.objects.filter(department=department_id, semester=semester_id)
    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def user_grades_create(request):
    serializer = UserGradesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



