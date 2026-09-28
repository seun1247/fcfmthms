from django.urls import path
from . import views

urlpatterns = [

    # ================= MAIN =================
    path("", views.home, name="home"),
    path("register/", views.register_student, name="register"),
    path("login/", views.login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_student, name="logout"),
    path("download/", views.download_pdf, name="download_pdf"),

    # ================= APPOINTMENTS =================
    path("appointment/", views.book_appointment, name="appointment"),

    # ================= ADMIN =================
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    path(
        "delete-student/<int:id>/",
        views.delete_student,
        name="delete_student"
    ),

    path(
        "delete-appointment/<int:id>/",
        views.delete_appointment,
        name="delete_appointment"
    ),

    path(
        "mark-arrived/<int:id>/",
        views.mark_arrived,
        name="mark_arrived"
    ),

    # ================= DOCTORS =================
    path(
        "add-doctor/",
        views.add_doctor,
        name="add_doctor"
    ),

    path(
        "delete-doctor/<int:id>/",
        views.delete_doctor,
        name="delete_doctor"
    ),

    # ================= AVAILABILITY =================
    path(
        "add-availability/",
        views.add_availability,
        name="add_availability"
    ),
    path(
    "approve-appointment/<int:id>/",
    views.approve_appointment,
    name="approve_appointment"
    ),

    path(
        "cancel-appointment/<int:id>/",
        views.cancel_appointment,
        name="cancel_appointment"
    ),

    path(
        "admin-cancel-appointment/<int:id>/",
        views.admin_cancel_appointment,
        name="admin_cancel_appointment"
    ),
    path(
        'download-appointment/<int:id>/',
        views.download_appointment_pdf,
        name='download_appointment_pdf'
    ),
    path(
        'edit-student/<int:id>/',
        views.edit_student,
        name='edit_student'
    ),

    path(
        "admin-student-card/<int:id>/",
        views.admin_student_card,
        name="admin_student_card"
    ),
    path(
        'medical-record/<int:id>/',
        views.add_medical_record,
        name='add_medical_record'
    ),
    path(
        'doctor-login/',
        views.doctor_login,
        name='doctor_login'
    ),

    path(
        'doctor-dashboard/',
        views.doctor_dashboard,
        name='doctor_dashboard'
    ),
    path(
        'doctor-logout/',
        views.doctor_logout,
        name='doctor_logout'
    ),
    path(
        'upload-record/', 
        views.upload_record, 
        name='upload_record'
    ),
    path(
        'edit-doctor/<int:doctor_id>/',
        views.edit_doctor,
        name='edit_doctor'
    ),
]