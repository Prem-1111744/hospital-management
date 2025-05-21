from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from hospitalapp.models import Appointment,Doctor,Patient,CustomUser
from django.contrib.auth.decorators import login_required
from hospitalapp.form import AppoinmentForm,Forgot_password_form,ReseteForgotPassword
from django.http import HttpResponse,JsonResponse,HttpResponseBadRequest,HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import secrets
from .models import PasswordResetToken


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email=request.POST.get('email')
        password = request.POST.get('password')
        conform_password=request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')
        
        if password != conform_password:
            messages.error(request,"This password is too short")
            return redirect('register')
        try:
            validate_password(password)
        except ValidationError as e:
            for error in e:
                messages.error(request,error)
            return redirect('register')

        user = CustomUser(
            username=username,
            email=email,
            user_type=user_type,
            password=make_password(password)
        )
        user.save()

        if user_type == 'doctor':
            Doctor.objects.create(user=user, specialization='Not set')
        elif user_type == 'patient':
            Patient.objects.create(user=user, age=0, address='')

        login(request, user)
        messages.success(request, 'Registration successful.')
        return redirect('login')

    return render(request, 'hospitalapp/register.html')

@login_required
def creat_appoinment(request):
    # Check if the logged-in user is a patient
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return HttpResponseBadRequest('<h1>You are not registered as a patient.</h1>')

    if request.method == "POST":
        form = AppoinmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient  # Set the patient
            appointment.doctor=form.cleaned_data['doctor']
            appointment.save()  # Save appointment
            messages.success(request, "Appointment created successfully.")
            return redirect('patient_dashboard')
    else:
        form = AppoinmentForm()

    return render(request, 'hospitalapp/createappoinment.html', {'form': form})

def admin_dashboard(request):
    return render(request,'hospitalapp/admindashboard.html')

def logout_view(request):
    try:
        logout(request)
    except:
        return HttpResponse('you are loged out ')
    return redirect('login')



@login_required
def appoinment_calendar(request):
    return render(request,'hospitalapp/calendar.html')

@login_required
def appointment_details(request,appointment_id):
    appointment=get_object_or_404(Appointment,id=appointment_id)
    return render(request,'hospitalapp/appointment_details.html',{'appointment':appointment})

@login_required
def calendar_data(request):
    appoinment=Appointment.objects.all()
    data=[]

    for app in appoinment:
        data.append({
           'title': f"{app.patient.user.username} with Dr. {app.doctor.user.username}",
           'start': f"{app.date} t {app.time}",
           'description':app.description,
           'url': reverse('appointment_details',args=[app.id]),
           'color':'#28a745',
           })
    return JsonResponse(data,safe=False)

@login_required
def edit_appoinment(request,appointment_id):
    appointment=get_object_or_404(Appointment,id=appointment_id)
    try:
        patient=Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return HttpResponseForbidden('<h1>only patients can edit appointments</h1>')
    if appointment.patient != patient:
        return HttpResponseForbidden('<h1>you are not authorized to edit this appointment</h1>')

    if request.method=="POST":
        form=AppoinmentForm(request.POST,instance=appointment)
        if form.is_valid():
            appointment=form.save(commit=False)
            appointment.patient=Patient.objects.get(user=request.user)
            appointment.save()
            messages.success('appointment updated successfuly')
            # If user is patient, set patient explicitly
            
            return redirect('patient_dashboard')
    else:
        form=AppoinmentForm(instance=appointment)
    return render(request,'hospitalapp/editappoinment.html',{'form':form,'appointment':appointment})

@login_required
def delete_appoinment(request,appointment_id):

    appoinment=get_object_or_404(Appointment,id=appointment_id)

    if request.method=='POST':
        appoinment.delete()
        messages.success(request,'Appoinment deleted')
        return redirect('patient_dashboard')
    return render(request,'hospitalapp/deleteappoinment.html',{'appoinment':appoinment})
    
    



def home(request):
    return render(request,'hospitalapp/home.html')

@login_required
def doctordashboard(request):
    try:
        doctor=Doctor.objects.get(user=request.user)
        appointment= Appointment.objects.filter(doctor=doctor)
    except Doctor.DoesNotExist:
        appointment=[]

    return render(request,'hospitalapp/doctordashboard.html',{'appointments':appointment})

@login_required
def patientdashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
        appointments = Appointment.objects.filter(patient=patient)
    except Patient.DoesNotExist:
        appointments = []

    return render(request, 'hospitalapp/patientdashboard.html', {'appointments': appointments})

def login_views(request):
    error = None  # default: no error

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # ✅ called only if user is valid
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.user_type == 'doctor':
                return redirect('doctor_dashboard')
            elif user.user_type == 'patient':
                return redirect('patient_dashboard')
        else:
            messages.error(request,"Invalid username or password")

    # ✅ for GET request, just render the form — no login() called here
    return render(request, 'hospitalapp/login.html', {'error': error})

User=get_user_model()
reset_token={}
def forgot_password(request):
    if request.method == 'POST':
        form=Forgot_password_form(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            try:
                user=User.objects.get(email=email)
                token=secrets.token_urlsafe(20)
                #reset_token[token]=user.username
                PasswordResetToken.objects.create(user=user,token=token)
                reset_link=request.build_absolute_uri(f'/resete-password/{token}/')
                send_mail(
                    'password_resete_link',
                    f'Click here to resete your password:{reset_link}',
                    'noreply@yourapp.com',
                    recipient_list=[user.email]
                )
                messages.success(request,'A password resete link has been sent to your email')
            except User.DoesNotExist:
                messages.error(request,'no user with this email found')
    else:
        form=Forgot_password_form()
    return render(request,'hospitalapp/forgot_password.html',{'form':form})


def resete_password(request,token):
    token_obj=get_object_or_404(PasswordResetToken,token=token)
    if not token_obj.is_valid():
        token_obj.delete()
        return render(request,'hospitalapp/reset_password_invalid.html')
    if request.method == 'POST':
        form=ReseteForgotPassword(request.POST)
        if form.is_valid():
            user=token_obj.user
            user.password=make_password(form.cleaned_data['new_password'])
            user.save()
            token_obj.delete()
            messages.success(request,'password resete successfully plese log in')
            return redirect('login')
    else:
        form=ReseteForgotPassword()
    return redirect(request,'hospitalapp/resete_password.html',{'form':form})
    

