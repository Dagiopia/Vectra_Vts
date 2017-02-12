from django.contrib.auth.models import User
from .models import *
from django import  forms

class PersonForm(forms.ModelForm):
	class Meta:
		model  = Person
		fields = ('first_name','middle_name','last_name','sex','birthday','tel','address','photo')
class UserForm(forms.ModelForm):
	class Meta:
		model  = Users
		fields = ('username','email','password','question','answer')	
class VehicleForm(forms.ModelForm):

	class Meta:
		model  = Vehicle
		fields = ('name','v_model','brand_name','engine_cc','color','image','status'
			 ,'plate_number')
class GpsDeviceForm(forms.ModelForm):
	
	class Meta:
		model  = GpsDevice
		fields = ('device_id','status','being_used')

class DriverForm(forms.ModelForm):

	class Meta:
		model  = Driver
		fields = ('agent_agreement_file',)



	
