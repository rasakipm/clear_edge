from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Student(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(null=True, max_length=255)
    matric_number = models.CharField(max_length=100, null=True)
    session = models.CharField(max_length=100, null=True)
    course = models.CharField(max_length=100, null=True)
    faculty = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)
    is_department = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, null=True)
    level = models.CharField(max_length=10, null=True)
    hostel_room_number = models.CharField(max_length=20, null=True)
    contact_address = models.TextField(null=True)
    
    def __str__(self):
        return self.username


class Department(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class ClearanceRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    decline_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        
        
class ClearanceSlip(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    approved_by_dean = models.BooleanField(default=False)
    clearance_slip_pdf = models.FileField(upload_to='clearance_slips/')
