from django.urls import path
from hospitalapp import views

urlpatterns=[
    path('',views.home,name='home'),
    path('login/',views.login_views,name='login'),
    path('admin/dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('doctor/dashboard/',views.doctordashboard,name='doctor_dashboard'),
    path('patient/dashboard/',views.patientdashboard,name='patient_dashboard'),
    path('appoinment/create/',views.creat_appoinment,name='createappoinment'),
    path('appoinment/edit/<int:appointment_id>/',views.edit_appoinment,name='editappoinment'),
    path('appoinment/delete/<int:appointment_id>/',views.delete_appoinment,name='deleteappoinment'),
    path('calendar/',views.appoinment_calendar,name='calendar'),
    path('calendar/data/',views.calendar_data,name='calendar_data'),
    path('logout/',views.logout_view,name='logout'),
    path('register/',views.register_view,name='register'),
    path('appointment/<int:appointment_id>/detail/',views.appointment_details,name='appointment_details'),
    path('forgot-password/',views.forgot_password,name='forgot_password'),
    path('resate-password/<str:token>/',views.resete_password,name='resate_password')
]