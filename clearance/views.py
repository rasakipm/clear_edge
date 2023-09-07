from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from school_clearance.settings import BASE_DIR
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.http import HttpResponse
from django.core.files.temp import NamedTemporaryFile
from datetime import datetime



# Admin Panel Views
def home(request):
    return render(request, 'home.html')


@login_required(login_url='admin_login')
@staff_member_required
def admin_panel(request):
    students = Student.objects.filter(is_staff=0, is_department=0)
    cleared_students = len(Student.objects.filter(status=True))
    return render(request, 'admin_panel.html', {'total_students': len(students), 'cleared':cleared_students})


@login_required(login_url='admin_login')
def department_dashboard(request, user_id):
    user = Student.objects.get(id=user_id, )
    department = Department.objects.get(user=user)
    if not department:
        raise PermissionDenied

    clearance_requests = ClearanceRequest.objects.filter(department=department)

    if request.method == 'POST':
        request_id = request.POST['request_id']
        response = request.POST['response']  # 'approve' or 'decline'
        clearance_request = ClearanceRequest.objects.get(id=request_id)

        if response == 'approve':
            clearance_request.is_approved = True
            clearance_request.save()
        elif response == 'decline':
            clearance_request.is_approved = False
            clearance_request.decline_reason = request.POST['decline_reason']
            clearance_request.save()

    return render(request, 'department_dashboard.html', {'clearance_requests': clearance_requests, 'student_id': user_id})

    

@login_required(login_url='admin_login')
@staff_member_required
def status(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        student = Student.objects.get(id=student_id)
        clearance_requests = ClearanceRequest.objects.filter(student=student)

        if all(request.is_approved for request in clearance_requests):
            student.status = True
            student.save()
            messages.success(request, 'Student approved successfully')
        else:
            messages.error(request, 'The student\'s clearance request has not been approved by all departments')

        return redirect('student_record')

def register_student(request):
    if request.method == 'POST':
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        mat_num = request.POST.get('matric_number')
        phone = request.POST.get('phone')
        session = request.POST.get('session')
        dept = request.POST.get('department')
        faculty = request.POST.get('faculty')
        gender = request.POST['gender']
        level = request.POST['level']
        hostel_room_number = request.POST['hostel_room_number']
        contact_address = request.POST['contact_address']
        
        student = Student(first_name=fname,
                            last_name=lname,
                            matric_number=mat_num,
                            phone=phone,
                            session=session,
                            course=dept,
                            faculty=faculty,
                            gender=gender,
                            level=level,
                            hostel_room_number=hostel_room_number,
                            contact_address=contact_address,
                            username=mat_num,
                            password=lname)
        student.set_password(lname.lower())
        student.save()
        
        # Create clearance requests for all departments
        departments = Department.objects.all()
        for department in departments:
            clearance_request = ClearanceRequest.objects.create(student=student, department=department)
        
        messages.error(request, 'Request made Successfuly! Login to view status')
        return redirect('home')
    return render(request, 'register_student.html')

@login_required(login_url='admin_login')
@staff_member_required
def register_department(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = Student(username=username, password=password, is_department=True)
        user.set_password(password.lower())
        user.save()
        
        department = Department(name=name, user=user)
        department.save()

        # Add clearance entries for all existing students in the new department
        students = Student.objects.filter(department=department)
        for student in students:
            ClearanceRequest.objects.create(student=student, department=department)

        messages.success(request, 'Department Registered Successfully')
        return redirect('admin_panel')
    return render(request, 'register_department.html')


@login_required(login_url='admin_login')
@staff_member_required
def student_record(request):
    students = Student.objects.filter(is_staff=0, is_department=0)
    return render(request, 'student_record.html', {'students':students})

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        try:
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin_panel') 
            elif user.is_department:
                login(request, user)
                return redirect('department_dashboard', user_id=user.id)
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('admin_login')
        except AttributeError:
            messages.error(request, 'Invalid username or password.')
            return redirect('admin_login')

    else:
        return render(request, 'admin_login.html')

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username , password)
        user = authenticate(request, username=username, password=password)
        if user is not None and not user.is_staff and not user.is_department:
            login(request, user)
            print('welcome')
            return redirect('student_dashboard', student_id=user.id) 
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('student_login')

    else:
        return render(request, 'student_login.html')


@login_required
def approve_clearance_request(request, request_id):
    department =  Department.objects.get(user=request.user)
    if not department:
        raise PermissionDenied
    clearance_request = ClearanceRequest.objects.get(pk=request_id, department=department)
    clearance_request.is_approved = True
    clearance_request.decline_reason = ''
    clearance_request.save()
    return redirect('department_dashboard', user_id=request.user.id)


@login_required
def decline_clearance_request(request, request_id):
    if request.method == 'POST':
        department =  Department.objects.get(user=request.user)
        if not department:
            raise PermissionDenied
        clearance_request = ClearanceRequest.objects.get(pk=request_id, department=department)
        clearance_request.is_approved = False
        clearance_request.decline_reason = request.POST['decline_reason']
        clearance_request.save()
        return redirect('department_dashboard', user_id=request.user.id)
    return render(request, 'decline_clearance_request.html', {'request_id': request_id})    
    


def logout_view(request):
    logout(request)
    return redirect('home')




# Student-Side Views
@login_required(login_url='student_login')
def student_dashboard(request, student_id):
    user = Student.objects.get(id=student_id)
    return render(request, 'student_dashboard.html', {'student':user})


def view_student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    clearance_requests = ClearanceRequest.objects.filter(student=student)
    for clearance in clearance_requests:
        print(clearance.department.name)
    return render(request, 'student_profile.html', {'student': student})

def std_logout(request):
    logout(request)
    return redirect('home')

@login_required
def download_clearance_slip(request):
    student = request.user
    if not isinstance(student, Student):
        raise PermissionDenied

    # Generate the PDF
    # Define the clearance slip content
    if student.status:
        clearance_slip_content = [
            ['NUHU BAMALI POLYTECHNIC'],
            ['Student Clearance Slip'],
            ['Student Name:', student.get_full_name()],
            ['Registration Number:', student.matric_number],
            ['Department:', student.course],
            ['School:', student.faculty],
            ['Session:', student.session],
            ['Clearance Status:', 'Approved'],
            ['Date of Clearance:', datetime.today().date()],
            [''],
            ['This is to certify that {} has successfully completed all necessary clearance requirements and is cleared for graduation.'.format(student.get_full_name())],
            [''],
            ['Please present this clearance slip to the appropriate authorities for further processing.'],
            [''],
            ['Dean of Student Affairs:', '_______________________'],
            ['Signature:', '_______________________'],
            ['Date:', '_______________________'],
        ]

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{student.matric_number}.pdf"'

        pdf_temp = NamedTemporaryFile()
        doc = SimpleDocTemplate(pdf_temp, pagesize=landscape(letter), leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
        elements = []

        # Add the title as a paragraph
        styles = getSampleStyleSheet()
        title_paragraph = Paragraph('<b>NUHU BAMALI POLYTECHNIC</b>', styles['Title'])
        elements.append(title_paragraph)
        elements.append(Spacer(0, 10))  # Add some space after the title

        table = Table(clearance_slip_content)
        table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.green),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ]))
        elements.append(table)
        elements.append(Spacer(0, 20))  # Add some space between table and footer

        doc.build(elements)
        pdf_temp.seek(0)
        response.write(pdf_temp.read())

        return response
    else:
        messages.error(request, 'You are yet to be cleared')
        return redirect('student_dashboard', student.id)
