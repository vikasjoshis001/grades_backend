from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Departments, Semesters, Subjects, UserGrades, SavePdf
from signup.models import Signup
from .serializers import DepartmentSerializer, SemesterSerializer, SubjectSerializer, SavePdfSerializer

# PDF
from .utils import render_to_pdf
from io import BytesIO
from django.core.files import File
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# Email
from django.core.mail import EmailMessage

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


@api_view(['GET'])
def get_user_grades(request, user_id):
    try:
        user = Signup.objects.get(id=user_id)
    except Signup.DoesNotExist:
        return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve UserGrades objects for the given user_id
    user_grades = UserGrades.objects.filter(user=user)

    # Create the payload using UserGrades, Subjects, and related data
    grades = []
    for user_grade in user_grades:
        grade = {
            'id': user_grade.subject.id,
            'semester': user_grade.semester.name,
            'subject': user_grade.subject.name,
            'grades': user_grade.grades
        }
        grades.append(grade)

    payload = {
        'user_name': user.name,
        'department': user.department,
        'grades': grades
    }

    return Response(payload)


@api_view(['GET'])
def generate_pdf(request, user_id):
    # user_id = request.data.get('user_id')

    user = Signup.objects.get(id=user_id)
    user_grades = UserGrades.objects.filter(user_id=user_id)

    grades = []
    for user_grade in user_grades:
        grade = {
            'id': user_grade.subject.id,
            'semester': user_grade.semester.name,
            'subject': user_grade.subject.name,
            'grades': user_grade.grades
        }
        grades.append(grade)

    data = {
        'name': user.name,
        'registration_number': user.reg_no,
        'branch': user.department,
        'course': user.course,
        'results': grades
    }

    print(data)

    try:
        # Generating Pdf
        pdf = render_to_pdf('pdf/result.html', data)
        my_filename = "Hello.pdf"
        dic = {
            "filename": my_filename
        }
        print("PDF GENERATED")

        # Saving filename
        serializers = SavePdfSerializer(data=dic)
        if (serializers.is_valid()):
            serializers.save()
        my_pdf = SavePdf.objects.filter(filename=my_filename)[0]
        output_file = PdfFileWriter()
        input_file = PdfFileReader(File(BytesIO(pdf.content)))

        # Adding Page no, website name and greetings in file
        for page in range(input_file.getNumPages()):
            tmp = BytesIO()
            can = canvas.Canvas(tmp, pagesize=A4)
            can.setFont('Times-Roman', 10)
            can.drawString(25, 20, "gradify | devMonks")
            can.drawString(250, 20, "***Congratulations***")
            can.drawString(525, 20, "Page " + str(page + 1))
            can.save()
            tmp.seek(0)
            watermark = PdfFileReader(tmp)
            watermark_page = watermark.getPage(0)
            pdf_page = input_file.getPage(page)
            pdf_page.mergePage(watermark_page)
            output_file.addPage(pdf_page)
        tmp = BytesIO()
        output_file.write(tmp)

        # Saving Pdf
        my_pdf.pdf_file.save(my_filename, File(tmp))
        my_pdf = SavePdf.objects.filter(filename=my_filename)[0]
        serializer = SavePdfSerializer(my_pdf)
        user_result['pdf'] = serializer.data['pdf_file']
        dic = {
            "Type": "Success",
            "msg": "Pdf genereted successfully",
            "data": user_result
        }
        return Response(data=dic)
    except Exception as e:
        dic = {
            "Type": "Error",
            "msg": "Unable to Create pdf",
            "data": None
            # "error": /e
        }
        return Response(data=dic)
