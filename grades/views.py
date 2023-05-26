from django.shortcuts import render
from django.conf import settings

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
from reportlab.lib.pagesizes import letter

# from io import BytesIO
# from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
# from PyPDF2 import PdfFileWriter, PdfFileReader
from django.http import FileResponse


# Email
from django.core.mail import EmailMessage
from django.core.mail import send_mail


# Create your views here.

from google.oauth2 import service_account
from google.auth.transport.requests import Request


def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=['https://www.googleapis.com/auth/gmail.send'])
    if credentials.expired:
        credentials.refresh(Request())
    return credentials.token


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
        reviewer_id=reviewer_id).select_related('user')

    unique_reg_nos = set(ug.user.reg_no for ug in user_grades)

    print(user_grades)

    # Create the payload using Signup and UserGrades data
    students = []
    for reg_no in unique_reg_nos:
        user_grade = user_grades.filter(user__reg_no=reg_no).first()
        print(user_grade)
        student = {
            'id': user_grade.user.id,
            'name': user_grade.user.name,
            'reg_no': reg_no
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
def generate_pdf(request, user_id, is_approved):
    is_approved = is_approved.lower() == 'true'
    user = Signup.objects.get(id=user_id)
    user_grades = UserGrades.objects.filter(user_id=user_id)

    print(user_grades, "USER GRADES")

    email = user.email

    payload = {
        'name': user.name,
        'registration_number': user.reg_no,
        'branch': user.department,
        'course': user.course,
        'semister': '',
        'email': user.email,
        'results': {}
    }
    if is_approved:

        for grade in user_grades:
            print(grade, "GRADE")
            semester_name = grade.semester.name
            subject_name = grade.subject.name
            grade_value = grade.grades
            print(semester_name, "SEMESTER NAME")

            if semester_name not in payload["results"]:
                payload["results"][semester_name] = []

            payload["results"][semester_name].append({
                "subject": subject_name,
                "grade": grade_value
            })

        print(payload)

        my_filename = payload['registration_number']+"-" + \
            payload['branch']+"-" + \
            datetime.now().strftime("%d%m%Y%H%M%S")+".pdf"
        dic = {
            "filename": my_filename
        }

        # Saving filename
        serializers = SavePdfSerializer(data=dic)
        if (serializers.is_valid()):
            serializers.save()
        my_pdf = SavePdf.objects.filter(filename=my_filename)[0]

        # Iterate over each semester and its results
        output_file = PdfFileWriter()

        for semester, results in payload["results"].items():
            payload['results'] = results
            payload['semister'] = semester
            pdf = render_to_pdf('pdf/result.html', payload)
            input_file = PdfFileReader(File(BytesIO(pdf.content)))

            # Adding Page no, website name and greetings in file
            for page in range(input_file.getNumPages()):
                tmp = BytesIO()
                can = canvas.Canvas(tmp, pagesize=A4)
                can.setFont('Times-Roman', 10)
                can.drawString(25, 20, "SGGSIE&T")
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

        # # Saving Pdf
        my_pdf.pdf_file.save(my_filename, File(tmp))
        my_pdf = SavePdf.objects.filter(filename=my_filename)[0]
        serializer = SavePdfSerializer(my_pdf)
        payload['pdf'] = serializer.data['pdf_file']
        dic = {
            "Type": "Success",
            "msg": "Pdf genereted successfully",
            "data": payload
        }
        try:
            print(payload['registration_number'].lower()+"@sggs.ac.in")
            subject = "Youe request for GradeCard is Approved"
            message = "Congratulations! Your request for gradecard has been approved. The gradecard is attached with mail"
            recipient_list = [email]
            email = EmailMessage(
                subject, message, "crunchbase.io@gmail.com", recipient_list)
            email.attach_file(payload['pdf'][1:])
            email.send()

            dic = {
                "Type": "Success",
                "msg": "Mail Sent Succesfully",
            }
            return Response(data=dic)
        except:
            dic = {
                "Type": "Error",
                "msg": "Sorry!Mail not Sent...",
            }
            return Response(data=dic)
    else:
        try:
            # print(payload, "In else")
            subject = "Your Request for GradeCard is Rejected"
            message = "Sorry! Your request for gradecard has been rejected due to some reasons"
            recipient_list = [email]
            email = EmailMessage(
                subject, message, "crunchbase.io@gmail.com", recipient_list)
            email.send()

            dic = {
                "Type": "Success",
                "msg": "Mail Sent Succesfully",
            }
            return Response(data=dic)
        except Exception as e:
            dic = {
                "Type": "Error",
                "msg": "Sorry!Mail not Sent...",
                "error": e,
            }
            return Response(data=dic)
            # return Response(data=dic)

        # filename = "result.pdf"  # Specify the desired filename
        # save_pdf = SavePdf(filename=filename)
        # save_pdf.pdf_file.save(filename, File(output_buffer))
        # save_pdf.save()

        # # Return the generated PDF as a FileResponse
        # response = FileResponse(
        #     output_buffer.getvalue(), as_attachment=True, filename="result.pdf")
        # return response
