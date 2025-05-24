from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Doctor, Patient, Appointment
from datetime import date, time

CustomUser = get_user_model()

class HospitalAppTests(TestCase):
    def setUp(self):
       
        self.doctor_user = CustomUser.objects.create_user(username='drjohn', password='Test@1234', user_type='doctor')
        self.patient_user = CustomUser.objects.create_user(username='patbob', password='Test@1234', user_type='patient')

       
        self.doctor = Doctor.objects.create(user=self.doctor_user, specialization='Cardiology')
        self.patient = Patient.objects.create(user=self.patient_user, age=30, address='Somewhere')

        self.client = Client()

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_and_dashboard_access(self):
        login = self.client.login(username='patbob', password='Test@1234')
        self.assertTrue(login)

        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_create_appointment(self):
        self.client.login(username='patbob', password='Test@1234')
        response = self.client.post(reverse('createappoinment'), {
            'doctor': self.doctor.id,
            'date': '2025-05-25',
            'time': '10:00',
            'description': 'Routine checkup'
        })
        self.assertEqual(response.status_code, 302)  

        appointment = Appointment.objects.get(patient=self.patient)
        self.assertEqual(appointment.description, 'Routine checkup')

    def test_appointment_shown_to_doctor(self):
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=date.today(),
            time=time(10, 0),
            description="Test appointment"
        )

        self.client.login(username='drjohn', password='Test@1234')
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertContains(response, "Test appointment")

    def test_password_validation_fail(self):
        response = self.client.post(reverse('register'), {
            'username': 'weakuser',
            'email': 'test@example.com',
            'password': '123',
            'user_type': 'patient'
        } ,follow=True)
        
        self.assertContains(response, "This password is too short")
