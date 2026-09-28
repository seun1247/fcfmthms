from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime, timedelta
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.hashers import (
    make_password,
    check_password
)

from .models import (
    Student,
    Appointment,
    Doctor,
    Availability
)

import re
import uuid
import os


# ================= HOME =================
def home(request):
    return render(request, 'index.html')


# ================= ADMIN HELPER =================
def get_admin(request):

    student_id = request.session.get('student_id')

    if not student_id:
        return None

    try:
        student = Student.objects.get(id=student_id)

        if student.reg_number == "ADMIN001":
            return student

    except Student.DoesNotExist:
        return None

    return None


# ================= PDF GENERATOR =================
def create_student_pdf(student):

    response = HttpResponse(content_type='application/pdf')

    response[
        'Content-Disposition'
    ] = f'attachment; filename="{student.reg_number}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)

    width, height = A4

    # ===== CARD BACKGROUND =====
    p.setFillColorRGB(0.95, 0.97, 1)

    p.roundRect(
        40,
        height - 500,
        width - 80,
        420,
        20,
        fill=1
    )

    # ===== HEADER =====
    p.setFillColorRGB(0, 0.3, 0.6)

    p.roundRect(
        40,
        height - 120,
        width - 80,
        60,
        20,
        fill=1
    )

    # ===== LOGO =====
    try:

        logo_path = os.path.join(
            settings.BASE_DIR,
            'static/images/logo.png'
        )

        logo = ImageReader(logo_path)

        p.drawImage(
            logo,
            60,
            height - 110,
            width=50,
            height=40,
            mask='auto'
        )

    except Exception as e:
        print("Logo Error:", e)

    # ===== TITLE =====
    p.setFillColor(colors.white)

    p.setFont("Helvetica-Bold", 18)

    p.drawString(
        160,
        height - 90,
        "FCFMT CLINIC"
    )

    p.setFont("Helvetica", 11)

    p.drawString(
        150,
        height - 105,
        "Student Registration Card"
    )

    # ===== PASSPORT =====
    photo_x = width - 150
    photo_y = height - 260

    p.setFillColorRGB(0.9, 0.9, 0.9)

    p.rect(
        photo_x,
        photo_y,
        100,
        120,
        fill=1
    )

    p.setStrokeColor(colors.black)

    p.rect(
        photo_x,
        photo_y,
        100,
        120
    )

    if student.photo:

        try:

            p.drawImage(
                student.photo.path,
                photo_x + 5,
                photo_y + 5,
                width=90,
                height=110,
                preserveAspectRatio=True
            )

        except Exception as e:
            print("Photo Error:", e)

    # ===== DETAILS =====
    y = height - 160

    details = [

        ("Full Name", student.full_name),

        ("Reg Number", student.reg_number),

        ("Department", student.department),

        ("Level", student.level),

        ("Date of Birth", student.date_of_birth),

        ("Phone", student.phone),
    ]

    for label, value in details:

        p.setFont("Helvetica-Bold", 10)

        p.setFillColor(colors.black)

        p.drawString(
            70,
            y,
            f"{label}:"
        )

        p.setFont("Helvetica", 10)

        p.drawString(
            170,
            y,
            str(value)
        )

        y -= 25

    # ===== SIGNATURE =====
    p.line(
        70,
        y - 20,
        220,
        y - 20
    )

    p.drawString(
        70,
        y - 35,
        "Student Signature"
    )

    p.line(
        300,
        y - 20,
        450,
        y - 20
    )

    p.drawString(
        300,
        y - 35,
        "Clinic Officer"
    )

    # ===== FOOTER =====
    p.setFont("Helvetica-Oblique", 9)

    p.setFillColor(colors.grey)

    p.drawCentredString(
        width / 2,
        80,
        "FCFMT Health Management System"
    )

    p.showPage()

    p.save()

    return response


# ================= REGISTER =================
def register_student(request):

    if request.method == "POST":

        full_name = request.POST.get('full_name')
        reg_number = request.POST.get('reg_number')
        department = request.POST.get('department')
        level = request.POST.get('level')
        dob = request.POST.get('date_of_birth')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        blood = request.POST.get('blood_group')
        genotype = request.POST.get('genotype')
        address = request.POST.get('address')
        emergency = request.POST.get('emergency_contact')
        photo = request.FILES.get('photo')

        # VALIDATION
        pattern = r"^FCFMT(ND|HND)\d{8}$"

        if not re.match(pattern, reg_number):

            return render(request, 'register.html', {

                'error': 'Invalid Registration Number Format'

            })
        
        # EMAIL DUPLICATE CHECK
        if Student.objects.filter(email=email).exists():

            return render(request, 'register.html', {

                'error': 'Email already registered'

            })

        # DUPLICATE CHECK
        if Student.objects.filter(
            reg_number=reg_number
        ).exists():

            return render(request, 'register.html', {

                'error': 'Student already registered'

            })

        # CREATE STUDENT
        student = Student.objects.create(

            full_name=full_name,
            reg_number=reg_number,
            email=email,
            department=department,
            level=level,
            date_of_birth=dob,
            phone=phone,
            blood_group=blood,
            genotype=genotype,
            address=address,
            emergency_contact=emergency,
            photo=photo
        )

        return create_student_pdf(student)

    return render(request, 'register.html')


# ================= LOGIN =================
def login(request):

    if request.method == "POST":

        reg_number = request.POST.get('reg_number')

        if not reg_number:

            return render(request, 'login.html', {

                'error': 'Please enter registration number'

            })

        try:

            student = Student.objects.get(
                reg_number=reg_number
            )

            request.session['student_id'] = student.id

            # ADMIN LOGIN
            if student.reg_number == "ADMIN001":

                return redirect('admin_dashboard')

            # NORMAL STUDENT LOGIN
            return redirect('dashboard')

        except Student.DoesNotExist:

            return render(request, 'login.html', {

                'error': 'Invalid Registration Number'

            })

    return render(request, 'login.html')


# ================= DASHBOARD =================
def dashboard(request):

    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('login')

    student = get_object_or_404(
        Student,
        id=student_id
    )

    appointments = Appointment.objects.filter(
        student=student
    ).order_by('-date', '-time')

    context = {

        "student": student,

        "appointments": appointments,
    }

    return render(
        request,
        'dashboard.html',
        context
    )


# ================= BOOK APPOINTMENT =================
def book_appointment(request):

    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('login')

    student = get_object_or_404(
        Student,
        id=student_id
    )

    available_slots = [

        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00"
    ]

    if request.method == "POST":

        appointment_type = request.POST.get(
            'appointment_type'
        )

        date = request.POST.get('date')

        time = request.POST.get('time')

        # DATE VALIDATION
        if not date:

            messages.error(
                request,
                "Please select a date."
            )

            return redirect('dashboard')

        try:

            selected_date = datetime.strptime(
                date,
                "%Y-%m-%d"
            )

        except ValueError:

            messages.error(
                request,
                "Invalid date format."
            )

            return redirect('dashboard')

        # WEEKEND BLOCK
        if selected_date.weekday() >= 5:

            messages.error(
                request,
                "Weekend bookings are unavailable."
            )

            return redirect('dashboard')

        # FRESHERS VALIDATION
        if appointment_type == "Freshers":

            allowed_levels = ["ND1", "HND1"]

            if student.level not in allowed_levels:

                messages.error(
                    request,
                    "Freshers Medical is only for ND1 and HND1 students."
                )

                return redirect('dashboard')

            if not time:

                messages.error(
                    request,
                    "Please select a time slot."
                )

                return redirect('dashboard')

            # MAXIMUM 4 STUDENTS
            slot_count = Appointment.objects.filter(

                appointment_type="Freshers",
                date=date,
                time=time

            ).count()

            if slot_count >= 4:

                next_slot = None

                # CHECK SAME DAY
                for slot in available_slots:

                    count = Appointment.objects.filter(

                        appointment_type="Freshers",
                        date=date,
                        time=slot

                    ).count()

                    if count < 4:

                        next_slot = f"{date} at {slot}"

                        break

                # CHECK NEXT DAYS
                if not next_slot:

                    check_date = selected_date

                    max_days = 30
                    days_checked = 0

                    while (
                        not next_slot and
                        days_checked < max_days
                    ):

                        check_date += timedelta(days=1)

                        days_checked += 1

                        # SKIP WEEKENDS
                        if check_date.weekday() >= 5:
                            continue

                        formatted_date = check_date.strftime(
                            "%Y-%m-%d"
                        )

                        for slot in available_slots:

                            count = Appointment.objects.filter(

                                appointment_type="Freshers",
                                date=formatted_date,
                                time=slot

                            ).count()

                            if count < 4:

                                next_slot = (
                                    f"{formatted_date} at {slot}"
                                )

                                break

                if not next_slot:

                    messages.error(
                        request,
                        "No available appointment slots found."
                    )

                    return redirect('dashboard')

                messages.error(
                    request,
                    f"This time slot is already full. "
                    f"Next available slot is {next_slot}."
                )

                return redirect('dashboard')

        else:

            # REGULAR + EMERGENCY
            # ADMIN WILL ASSIGN TIME
            time = None

        # CREATE APPOINTMENT
        Appointment.objects.create(

            student=student,

            appointment_type=appointment_type,

            date=date,

            time=time,

            status='PENDING',

            appointment_id=str(
                uuid.uuid4()
            )[:8].upper()
        )

        messages.success(
            request,
            "Appointment booked successfully."
        )

        return redirect('dashboard')

    appointments = Appointment.objects.filter(
        student=student
    ).order_by('-created_at')

    context = {

        "student": student,

        "appointments": appointments,

        "available_slots": available_slots,
    }

    return render(
        request,
        'dashboard.html',
        context
    )


# ================= DOWNLOAD PDF =================
def download_pdf(request):

    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('login')

    student = get_object_or_404(
        Student,
        id=student_id
    )

    return create_student_pdf(student)


# ================= LOGOUT =================
def logout_student(request):

    request.session.flush()

    return redirect('login')


# ================= ADMIN DASHBOARD =================
def admin_dashboard(request):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    tab = request.GET.get('tab', 'overview')

    students = Student.objects.all().order_by('-id')

    appointments = Appointment.objects.select_related(
        'student',
        'doctor'
    ).order_by('-date', '-time')

    doctors = Doctor.objects.all().order_by('name')

    availability = Availability.objects.select_related(
        'doctor'
    ).order_by('-date', '-time')

    # COUNTS
    total_students = students.count()

    total_appointments = appointments.count()

    total_doctors = doctors.count()

    pending_appointments = appointments.filter(
        status='PENDING'
    ).count()

    arrived_appointments = appointments.filter(
        status='ARRIVED'
    ).count()

    completed_appointments = appointments.filter(
        status='COMPLETED'
    ).count()

    context = {

        "admin": admin,

        "students": students,

        "appointments": appointments,

        "doctors": doctors,

        "availability": availability,

        "total_students": total_students,

        "total_appointments": total_appointments,

        "total_doctors": total_doctors,

        "pending_appointments": pending_appointments,

        "arrived_appointments": arrived_appointments,

        "completed_appointments": completed_appointments,

        "active_tab": tab,
    }

    return render(
        request,
        'admin/admin-dashboard.html',
        context
    )


def add_doctor(request):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    if request.method == "POST":

        name = request.POST.get('name')
        department = request.POST.get('department')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        photo = request.FILES.get('photo')

        if name and department:

            doctor_id = "DOC" + str(uuid.uuid4())[:5].upper()

            # DEFAULT PASSWORD
            password = "doctor123"

            Doctor.objects.create(

                name=name,
                department=department,
                phone=phone,
                email=email,
                photo=photo,
                doctor_id=doctor_id,
                password=make_password(password)
            )

            messages.success(
                request,
                f"Doctor added successfully. Doctor ID: {doctor_id}"
            )

    return redirect('/admin-dashboard/?tab=doctors')


def delete_doctor(request, id):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    doctor = get_object_or_404(
        Doctor,
        id=id
    )

    doctor.delete()

    return redirect('/admin-dashboard/?tab=doctors')


def add_availability(request):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    if request.method == "POST":

        doctor_id = request.POST.get('doctor')

        date = request.POST.get('date')

        time = request.POST.get('time')

        doctor = get_object_or_404(
            Doctor,
            id=doctor_id
        )

        Availability.objects.create(

            doctor=doctor,

            date=date,

            time=time,

            is_booked=False
        )

    return redirect('/admin-dashboard/?tab=availability')


def delete_student(request, id):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    student = get_object_or_404(
        Student,
        id=id
    )

    student.delete()

    return redirect('/admin-dashboard/?tab=students')


def delete_appointment(request, id):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    appointment.delete()

    return redirect('/admin-dashboard/?tab=appointments')


def mark_arrived(request, id):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    appointment.status = "ARRIVED"

    appointment.save()

    return redirect('/admin-dashboard/?tab=appointments')


# ================= APPROVE APPOINTMENT =================
def approve_appointment(request, id):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    if request.method == "POST":

        doctor_id = request.POST.get('doctor')

        time = request.POST.get('time')

        doctor = get_object_or_404(
            Doctor,
            id=doctor_id
        )

        appointment.doctor = doctor

        # ONLY ADMIN ASSIGNS TIME
        if appointment.appointment_type != "Freshers":
            appointment.time = time

        appointment.status = "APPROVED"

        appointment.save()

        send_appointment_email(
            appointment,
            "APPROVED"
        )

        return redirect('/admin-dashboard/?tab=appointments')
    
    return redirect('/admin-dashboard/?tab=appointments')

def send_appointment_email(appointment, status):

    if status == "APPROVED":
        message = "Good news! Your appointment has been approved."
        color = "green"
        line1 = "green"
        line2 = "#ccc"

    elif status == "COMPLETED":
        message = "Your appointment has been completed."
        color = "#0d47a1"
        line1 = "green"
        line2 = "green"

    elif status == "CANCELLED":
        message = "Your appointment has been cancelled."
        color = "red"
        line1 = "red"
        line2 = "red"

    else:  # Booked
        message = "Your appointment has been booked and is awaiting approval."
        color = "black"
        line1 = "#ccc"
        line2 = "#ccc"

    
    
    extra_note = ""

    if status == "APPROVED":
        extra_note = "Please arrive at least 15 minutes early."

    elif status == "COMPLETED":
        extra_note = "Your medical consultation has been completed successfully."

    elif status == "CANCELLED":
        extra_note = "Please contact the clinic if you need another appointment."


    context = {
        "name": appointment.student.full_name,

        "doctor": appointment.doctor.name if appointment.doctor else "Pending Assignment",

        "date": appointment.date,
        "time": appointment.time,
        "status": status,
        "status_title": status,
        "appointment_type": appointment.appointment_type,
        "message": message,
        "extra_note": extra_note,
        "logo_url": "https://yourdomain.com/static/images/logo.png",

        "status_color": color,
        "line1_color": line1 or "#ccc",
        "line2_color": line2 or "#ccc",
    }

    html_content = render_to_string(
    'emails/appointment_status.html',
    context
    )

    email = EmailMultiAlternatives(
        subject=f'Appointment {status}',
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[appointment.student.email]
    )

    email.attach_alternative(html_content, "text/html")

    email.send()
    


# ================= CANCEL APPOINTMENT =================
def cancel_appointment(request, id):

    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('login')

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    # STUDENT CAN ONLY CANCEL OWN APPOINTMENT
    if appointment.student.id != student_id:
        return redirect('dashboard')

    appointment.status = "CANCELLED"

    appointment.save()

    return redirect('dashboard')


# ================= ADMIN CANCEL APPOINTMENT =================
def admin_cancel_appointment(request, id):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    appointment.status = "CANCELLED"

    appointment.save()

    send_appointment_email(
    appointment,
    "CANCELLED"
    )

    return redirect('/admin-dashboard/?tab=appointments')


# ================= DOWNLOAD APPOINTMENT PDF =================
def download_appointment_pdf(request, id):

    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('login')

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    # SECURITY
    if appointment.student.id != student_id:
        return redirect('dashboard')

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="appointment_{appointment.appointment_id}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)

    width, height = A4

    # BACKGROUND
    p.setFillColorRGB(0.95, 0.97, 1)

    p.roundRect(
        40,
        height - 650,
        width - 80,
        560,
        20,
        fill=1
    )

    # HEADER
    p.setFillColorRGB(0, 0.3, 0.6)

    p.roundRect(
        40,
        height - 120,
        width - 80,
        60,
        20,
        fill=1
    )

    # LOGO
    try:

        logo_path = os.path.join(
            settings.BASE_DIR,
            'static/images/logo.png'
        )

        logo = ImageReader(logo_path)

        p.drawImage(
            logo,
            60,
            height - 110,
            width=50,
            height=40,
            mask='auto'
        )

    except Exception as e:
        print("Logo Error:", e)

    # TITLE
    p.setFillColor(colors.white)

    p.setFont("Helvetica-Bold", 20)

    p.drawString(
        160,
        height - 90,
        "FCFMT CLINIC"
    )

    p.setFont("Helvetica", 11)

    p.drawString(
        160,
        height - 105,
        "Official Appointment Slip"
    )

    # STATUS BADGE
    status_color = colors.green

    if appointment.status == "PENDING":
        status_color = colors.orange

    elif appointment.status == "CANCELLED":
        status_color = colors.red

    elif appointment.status == "ARRIVED":
        status_color = colors.blue

    p.setFillColor(status_color)

    p.roundRect(
        width - 170,
        height - 180,
        90,
        30,
        10,
        fill=1
    )

    p.setFillColor(colors.white)

    p.setFont("Helvetica-Bold", 12)

    p.drawCentredString(
        width - 125,
        height - 162,
        appointment.status
    )

    # DETAILS
    y = height - 200

    details = [

        ("Appointment ID", appointment.appointment_id),

        ("Student Name", appointment.student.full_name),

        ("Registration Number", appointment.student.reg_number),

        ("Appointment Type", appointment.appointment_type),

        (
            "Assigned Doctor",
            f"Dr. {appointment.doctor.name}"
            if appointment.doctor
            else "Pending Assignment"
        ),

        ("Appointment Date", appointment.date),

        (
            "Appointment Time",
            appointment.time
            if appointment.time
            else "Awaiting Schedule"
        ),
    ]

    for label, value in details:

        p.setFillColorRGB(0, 0.25, 0.5)

        p.setFont("Helvetica-Bold", 11)

        p.drawString(
            80,
            y,
            f"{label}:"
        )

        p.setFillColor(colors.black)

        p.setFont("Helvetica", 11)

        p.drawString(
            260,
            y,
            str(value)
        )

        p.setStrokeColorRGB(0.85, 0.85, 0.85)

        p.line(
            80,
            y - 10,
            width - 80,
            y - 10
        )

        y -= 45

    # IMPORTANT NOTICE
    p.setFillColorRGB(1, 0.96, 0.85)

    p.roundRect(
        70,
        y - 60,
        width - 140,
        70,
        10,
        fill=1
    )

    p.setFillColor(colors.black)

    p.setFont("Helvetica-Bold", 10)

    p.drawString(
        90,
        y - 20,
        "IMPORTANT:"
    )

    p.setFont("Helvetica", 10)

    p.drawString(
        90,
        y - 40,
        "Please arrive at least 15 minutes before your appointment."
    )

    # SIGNATURES
    y -= 120

    p.setStrokeColor(colors.black)

    p.line(
        80,
        y,
        240,
        y
    )

    p.drawString(
        100,
        y - 20,
        "Student Signature"
    )

    p.line(
        330,
        y,
        500,
        y
    )

    p.drawString(
        360,
        y - 20,
        "Clinic Officer"
    )

    # FOOTER
    p.setFont("Helvetica-Oblique", 9)

    p.setFillColor(colors.grey)

    p.drawCentredString(
        width / 2,
        60,
        "FCFMT Health Management System"
    )

    p.drawCentredString(
        width / 2,
        45,
        "Generated Appointment Document"
    )

    p.showPage()

    p.save()

    return response


# ================= EDIT STUDENT =================
def edit_student(request, id):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    student = get_object_or_404(
        Student,
        id=id
    )

    if request.method == "POST":

        student.full_name = request.POST.get(
            'full_name'
        )

        student.reg_number = request.POST.get(
            'reg_number'
        )

        student.department = request.POST.get(
            'department'
        )

        student.level = request.POST.get(
            'level'
        )

        student.date_of_birth = request.POST.get(
            'date_of_birth'
        )

        student.phone = request.POST.get(
            'phone'
        )

        student.email = request.POST.get(
            'email'
        )

        student.blood_group = request.POST.get(
            'blood_group'
        )

        student.genotype = request.POST.get(
            'genotype'
        )

        student.address = request.POST.get(
            'address'
        )

        student.emergency_contact = request.POST.get(
            'emergency_contact'
        )

        # PHOTO UPDATE
        if request.FILES.get('photo'):

            student.photo = request.FILES.get(
                'photo'
            )

        student.save()

        messages.success(
            request,
            "Student updated successfully."
        )

        return redirect(
            '/admin-dashboard/?tab=students'
        )

    return render(
        request,
        'admin/edit-student.html',
        {
            'student': student
        }
    )


# ================= ADMIN STUDENT CARD =================
def admin_student_card(request, id):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    student = get_object_or_404(
        Student,
        id=id
    )

    return create_student_pdf(student)

# ================= ADD MEDICAL RECORD =================
def add_medical_record(request, id):

    admin = get_admin(request)

    if not admin:
        return redirect('dashboard')

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    if request.method == "POST":

        appointment.diagnosis = request.POST.get(
            'diagnosis'
        )

        appointment.prescription = request.POST.get(
            'prescription'
        )

        appointment.clinic_notes = request.POST.get(
            'clinic_notes'
        )

        appointment.treated_at = timezone.now()

        appointment.status = "COMPLETED"

        appointment.save()

        messages.success(
            request,
            "Medical record updated successfully."
        )

        send_appointment_email(
        appointment,
        "COMPLETED"
        )

    return redirect(
        '/admin-dashboard/?tab=appointments'
    )

# ================= DOCTOR HELPER =================
def get_doctor(request):

    doctor_id = request.session.get('doctor_id')

    if not doctor_id:
        return None

    try:

        return Doctor.objects.get(
            id=doctor_id
        )

    except Doctor.DoesNotExist:

        return None
    

# ================= DOCTOR DASHBOARD =================
def doctor_dashboard(request):

    doctor = get_doctor(request)

    if not doctor:
        return redirect('doctor_login')

    assigned_appointments = Appointment.objects.filter(
        doctor=doctor,
        status__in=["APPROVED", "ARRIVED"]
    ).select_related('student').order_by('-date')

    completed_appointments = Appointment.objects.filter(
        doctor=doctor,
        status="COMPLETED"
    ).select_related('student').order_by('-date')

    return render(request, 'doctor/dashboard.html', {
        "doctor": doctor,
        "appointments": assigned_appointments,
        "completed_appointments": completed_appointments
    })

def doctor_login(request):

    # ✅ Already logged in
    if request.session.get('doctor_id'):
        return redirect('doctor_dashboard')

    if request.method == "POST":

        doctor_id = request.POST.get('doctor_id')
        password = request.POST.get('password')

        if not doctor_id or not password:
            messages.error(request, "Enter ID and password")
            return redirect('doctor_login')

        try:
            doctor = Doctor.objects.get(doctor_id=doctor_id)

            if not check_password(password, doctor.password):

                messages.error(request, "Invalid credentials")

                return redirect('doctor_login')

            request.session['doctor_id'] = doctor.id

            return redirect('doctor_dashboard')

        except Doctor.DoesNotExist:

            messages.error(request, "Invalid credentials")

            return redirect('doctor_login')

    return render(request, 'doctor/login.html')

def doctor_logout(request):

    if request.session.get('doctor_id'):

        del request.session['doctor_id']

        messages.success(
            request,
            "Logged out successfully."
        )

    return redirect('doctor_login')

def upload_record(request):

    doctor = get_doctor(request)

    if not doctor:
        return redirect('doctor_login')

    if request.method == "POST":

        appointment_id = request.POST.get('appointment_id')

        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            doctor=doctor
        )

        appointment.diagnosis = request.POST.get('diagnosis')
        appointment.prescription = request.POST.get('prescription')
        appointment.clinic_notes = request.POST.get('clinic_notes')

        appointment.status = "COMPLETED"
        appointment.treated_at = timezone.now()

        appointment.save()

        messages.success(request, "Medical record uploaded successfully")

        send_appointment_email(
        appointment,
        "COMPLETED"
        )

    return redirect('doctor_dashboard')

def edit_doctor(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)

    if request.method == "POST":
        doctor.name = request.POST.get("name")
        doctor.department = request.POST.get("department")
        doctor.phone = request.POST.get("phone")
        doctor.email = request.POST.get("email")

        if request.FILES.get("photo"):
            doctor.photo = request.FILES["photo"]

        doctor.save()

    return redirect("/admin-dashboard/?tab=doctors")