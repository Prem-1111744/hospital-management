from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
# Create your models here.
class CustomUser(AbstractUser):
    USER_TYPES=(('doctor','Doctor'),('patient','Patient'))
    user_type=models.CharField(max_length=10,choices=USER_TYPES)
    def __str__(self):
        return self.username

class Doctor(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    specialization=models.CharField(max_length=100)
    def __str__(self):
        return self.user.username

class Patient(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    age=models.IntegerField()
    address= models.TextField()
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Appointment(models.Model):
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE)
    patient=models.ForeignKey(Patient,on_delete=models.CASCADE)
    date=models.DateField()
    time=models.TimeField()
    description=models.TextField()
    def __str__(self):
        return  f"Appointment on {self.date} with {self.doctor.user.username} and {self.patient.user.username}"

User=get_user_model()   
class PasswordResetToken(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    token=models.CharField(max_length=100,unique=True)
    created_at=models.DateField(auto_now_add=True)
    def is_valid(self):
        return timezone.now()< self.created_at + datetime.timedelta(hours=1)
    def __str__(self):
         return f'reset token for{self.user.username}'