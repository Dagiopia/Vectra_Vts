from __future__ import unicode_literals

from django.db import models
from django import forms
from django.contrib.auth.models import User

class Person(models.Model):
	GENDER_CHOICES = (
		(u'M', u'Male'),
		(u'F', u'Female'),
	)
	first_name   = models.CharField(max_length=50)
	middle_name  = models.CharField(max_length=50)
	last_name    = models.CharField(max_length=50)
 	sex	     = models.CharField(max_length=2)
	birthday     = models.DateField(blank=True)
        tel	     = models.CharField(max_length=14)
	address	     = models.TextField()
	photo        = models.ImageField(upload_to ='profile_images',blank = True)
	reg_date     = models.DateField(auto_now_add=True)


	def __unicode__(self):
		return u'%s' '%s' % (self.first_name, self.last_name)

class Users(models.Model):
	
        person   = models.ForeignKey(Person,null=True)
	username = models.CharField(max_length=30,unique=True,null = True)
	email    = models.EmailField(blank=False,unique=True)
	password = models.CharField(max_length=30)
	salt     = models.CharField(max_length=10)
	question = models.TextField()
	answer	 = models.TextField()
	created_date = models.DateField(auto_now_add=True)
	update_date  = models.DateField(auto_now_add=True)

	 	
	
class Driver(models.Model):
	DRIVER_STATUS      = (('A','assigned'),('D','not assigned'),)
	person               = models.ForeignKey(Person,null=True)
	agent_agreement_file = models.FileField(upload_to = 'agreement_files',blank = True) 
	user 		     = models.ForeignKey(Users,null=True)
	status		     = models.CharField(max_length=2,choices=DRIVER_STATUS)
	assigned_date	     = models.DateField(null=True) 
	def __str__(self):
        	return self.person.first_name	
	def deassign(self):
		self.status = self.DRIVER_STATUS[1][0];
	def assign(self):
		self.status = self.DRIVER_STATUS[0][0];
	


	
class GpsDevice(models.Model):
	GPS_STATUS      = (('A','active'),('D','not active'),)
	GPS_BEING_USED  = (('Y','yes'),('N','no'),)
	device_id	= models.CharField(max_length=20,primary_key=True,default="123456789")
	status          = models.CharField(max_length=2,choices=GPS_STATUS)
	being_used      = models.CharField(max_length=2,choices=GPS_BEING_USED)
	activated_date  = models.DateField(auto_now_add=True)
        
	def deactivate(self):
		self.status = self.GPS_STATUS[1][0];
	def activate(self):
		self.status = self.GPS_STATUS[0][0];
	def set_being_used_yes(self):
		self.being_used = self.GPS_BEING_USED[0][0]
	def set_being_used_no(self):
		self.being_used = self.GPS_BEING_USED[1][0]
		
class Vehicle(models.Model):
	VEHICLE_STATUS  =(('A','active'),('D','not active'),)
	user 		= models.ForeignKey(Users,null=True)
	gps     	= models.ForeignKey(GpsDevice,null=True)
	driver          = models.ForeignKey(Driver,null=True)
	plate_number    = models.CharField(max_length = 20,unique=True)
	name    	= models.CharField(max_length=50,default="")

	brand_name   	= models.CharField(max_length=50,default="")
	#maker   	= models.CharField(max_length=50,default="")
	v_model 	= models.CharField(max_length=50,default="")
	engine_cc  	= models.CharField(max_length=50,default="")
	color   	= models.CharField(max_length=50,default="")
	image   	= models.ImageField(upload_to="Vehicle_images",blank=True)
	status  	= models.CharField(max_length=2,choices=VEHICLE_STATUS)	
	
	#net_weight   	= models.FloatField(default  = 0.0)
	#fuel_type    	= models.CharField(max_length = 100)
	
	#made_year       = models.DateField()
        
	def __str__(self):
        	return self.name
	def deactivate(self):
		self.status = self.VEHICLE_STATUS[1][0];
	def activate(self):
		self.status = self.VEHICLE_STATUS[0][0];
	def update_info(self):
		pass

	
class GpsData(models.Model):
	gps 	        = models.ForeignKey(GpsDevice,unique=True)
	latituide_pos   = models.FloatField(default  = 0.0)#TODO change to appropriat field
	longtuide_pos   = models.FloatField(default  = 0.0)#TODO change to appropriat field
	bearing		    = models.FloatField(default  = 0.0)
	time_stamp      = models.DateField(auto_now_add = True)#TODO add this field on the report


