from django.db import models
from django.utils.crypto import get_random_string


class Student(models.Model):

    full_name = models.CharField(max_length=200)
    reg_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=200 , null=True, blank=True)
    department = models.CharField(max_length=200)
    level = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=5)
    genotype = models.CharField(max_length=5)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15)

    # STUDENT PHOTO
    photo = models.ImageField(upload_to='students/', null=True, blank=True)

    # STUDENT CARD FILE
    card = models.FileField(
        upload_to='student_cards/',
        null=True,
        blank=True
    )

    # AUTO TIMESTAMP
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.reg_number}"
    
    
class MedicalRecord(models.Model):

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    treatment = models.TextField()
    doctor = models.CharField(max_length=100)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student.full_name

class Doctor(models.Model):

    name = models.CharField(max_length=100)

    department = models.CharField(max_length=100)

    doctor_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    password = models.CharField(
        max_length=100,
        default="doctor123"
    )

    photo = models.ImageField(
    upload_to='doctors/',
    blank=True,
    null=True
    )

    phone = models.CharField(
    max_length=20,
    blank=True,
    null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

class Availability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor.name} - {self.date} {self.time}"

class Appointment(models.Model):

    APPOINTMENT_TYPES = [
        ('Regular', 'Regular Check-up'),
        ('Emergency', 'Emergency'),
        ('Freshers', 'Freshers Medical'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('ARRIVED', 'Arrived'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    

    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE
    )

    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPES
    )

    date = models.DateField()

    # Optional for Regular/Emergency
    time = models.TimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    diagnosis = models.TextField(
    blank=True,
    null=True
    )

    prescription = models.TextField(
        blank=True,
        null=True
    )

    clinic_notes = models.TextField(
        blank=True,
        null=True
    )

    treated_at = models.DateTimeField(
        blank=True,
        null=True
    )

    appointment_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    cancellation_reason = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.appointment_id:

            self.appointment_id = (
                "APT-" +
                get_random_string(8).upper()
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.appointment_id} - {self.student.full_name}"