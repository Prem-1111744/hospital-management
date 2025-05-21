from django import forms
from hospitalapp.models import Appointment,Doctor
'''class AppoinmentForm(forms.ModelForm):
    doctor=forms.CharField()
    patient=forms.CharField()
    class Meta():
        model=Appointment
        fields=['doctor','patient','date','time','description']
        widgets={'date':forms.DateInput(attrs={'type':'date'}),
                 'time':forms.TimeInput(attrs={'type':'time'})}'''
class AppoinmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.all()

class Forgot_password_form(forms.Form):
    email=forms.EmailField()

class ReseteForgotPassword(forms.Form):
    new_password=forms.CharField(widget=forms.PasswordInput)
    confirm_password=forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        clened_data= super().clean()
        if clened_data['new_password'] != clened_data['confirm_password']:
            raise forms.ValidationError('password do not match')
