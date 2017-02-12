from django.shortcuts import render,render_to_response
from django.template import RequestContext, loader
from django.template.loader import render_to_string

from django.http import HttpResponseRedirect,Http404,HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from .forms  import *
from .models import *

import hashlib
import random
import base64
import csv
import os
import math
import datetime

import pdfkit



def getDistance_between(loc_1,loc_2):
    # This uses the haversine formula, which remains a good numberical computation,
    # even at small distances, unlike the Shperical Law of Cosines.
    # This method has ~0.3% error built in.

    R = 6371 # Radius of Earth in km

    dLat = math.radians(loc_2[0] - loc_1[0])
    dLon = math.radians(loc_2[1] - loc_1[1])
    lat1 = math.radians(loc_1[0])
    lat2 = math.radians(loc_2[0])

    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(lat1) * math.cos(lat2) * math.sin(dLon/2) * math.sin(dLon/2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = R * c

    return d
def get_total_distance(locations):

	totaldistance = 0	
	for i in range(len(locations)):
		if i+1 >= len(locations):break
    		totaldistance += getDistance_between(locations[i], locations[i+1])
	return round(totaldistance,2)

def hashSSHA(password):
	salt = hashlib.sha1(str(random.getrandbits(32))).hexdigest()
	salt = salt[:10]
	encrypted  = base64.b64encode(hashlib.sha1(password+salt).hexdigest()+salt)
	my_hash = {"salt":salt,"encrypted":encrypted}
	return my_hash	

def checkhashSSHA(salt,password):
	my_hash =  base64.b64encode(hashlib.sha1(password+salt).hexdigest()+salt)		
	return my_hash

def authenticate_user(username,password):
	user  = Users.objects.get(email=username)
	if user == None:return None
	if(checkhashSSHA(user.salt,password)==user.password):return user
	else:return None

def convert_csv_to_list(csv_path):
	with open(csv_path,'r') as f:
		reader  = csv.reader(f)
		my_list = list(reader)
	return my_list


def pdf(request,user_id,vehicle_id):


	user    = Users.objects.get(id=user_id)
	vehicle = Vehicle.objects.get(id=vehicle_id)
	pdf = pdfkit.from_url('http://localhost:8000/report/vehicle/'+str(user_id)+'/'+str(vehicle_id)+'/', False)
	response = HttpResponse(pdf,content_type='application/pdf')
	#response['Content-Disposition'] = 'attachment; filename="report.pdf"'

	response['Content-Disposition'] = 'attachment; '+'filename='+'"'+vehicle.name+'report_'+'.pdf'+'"'

	return response

	
"""########################### ADMIN #######################"""


def admin_login(request):
	# Like before, obtain the context for the user's request.
	context = RequestContext(request)
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
	# Gather the username and password provided by the user.
		# This information is obtained from the login form.
		username = request.POST['username']
		password = request.POST['password']
		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)
	  	if user is not None:
			# Is the account active? It could have been disabled.
			if user.is_active:
				login(request, user)
			
				return HttpResponseRedirect('/admin_dashboard/dashboard/')
			else:
			
				return HttpResponse("Your Rango account is disabled.")
		else:

			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")

	else:
		return render(request,'signin.html',{})

@login_required
def admin_dashboard(request):
	return render(request, "admin_new_new.html", {})


@login_required
def admin_dashboard_add_user(request):
#TODO do the template properly
	context = RequestContext(request)
	registered = False
	
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		person_form = PersonForm(data=request.POST)
	
		if user_form.is_valid() and person_form.is_valid():
		
			user = user_form.save(commit=False)
			person = person_form.save(commit=False)
			if 'photo' in request.FILES:
				
				person.photo = request.FILES['photo']
			person.save()			
			user.person = person
			my_hash = hashSSHA(user.password)
			user.password = my_hash['encrypted']
			user.salt     = my_hash['salt']
			user.save()
			django_user = User.objects.create_user(username=user.username,
                                 email=user.email,
                                 password=user.password)
			django_user.save()
			registered = True
		else:
			
			print user_form.errors, person_form.errors
	else:
		user_form = UserForm()
		person_form = PersonForm()
# Render the template depending on the context.
	return render_to_response('admin_new_new.html',{'registered':registered},context)

"""########################### USER #######################"""

def myview(request):
    #Retrieve data or whatever you need
    results = {}
    return render_to_pdf(
            'test.html',
            {
                'pagesize':'A4',
                'mylist': results,
            }
        )



def user_login(request):
	# Like before, obtain the context for the user's request.

	context = RequestContext(request)
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
	        # Gather the username and password provided by the user.
		# This information is obtained from the login form.
		username = request.POST['username']
		password = request.POST['password']
		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate_user(username=username, password=password)
	  	if user is not None:
			# Is the account active? It could have been disabled.
			django_user = User.objects.get(username=user.username)
			if django_user.is_active:
				login(request,django_user)
				
				return HttpResponseRedirect('/dashboard/dashboard/'+str(user.id)+'/')
			else:
			
				return HttpResponse("Your account is disabled.")
		else:

			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")

	else:
		return render(request,'login.html',{})

def handle_gps(request,gps_id):
	gps = GpsDevice.objects.get(device_id=gps_id)
	
	f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)))+'/history/'+str(gps_id)+'.csv','a')
		
	if 'lat' in request.POST and 'long' in request.POST :

		
		try:
			data = GpsData.objects.create(gps=gps,latituide_pos=request.POST['lat'],longtuide_pos=request.POST['long'])
			data.save()
			f.write(str(request.POST['lat'])+','+str(request.POST['long'])+','+str(data.time_stamp)+'\n')
		except:
			data = GpsData.objects.get(gps = gps)
			data.latituide_pos = request.POST['lat']
			data.longtuide_pos = request.POST['long']
			data.save()		
			f.write(str(request.POST['lat'])+','+str(request.POST['long'])+','+str(data.time_stamp)+'\n')

	return HttpResponse('')
@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/home/')
@login_required
def admin_logout(request):
	logout(request)
	return HttpResponseRedirect('/admin_dashboard/dashboard/')

def home(request):
	return render(request, "index.html", {})

@login_required(login_url='/user_login/')
def about(request,user_id):

	user  = Users.objects.get(id=user_id)
	here  = "about"
	return render(request, "about.html", {'user':user,'here':here})

@login_required(login_url='/user_login/')
def help(request,user_id):
	
	user  = Users.objects.get(id=user_id)
	here  = "help" 
	return render(request, "help.html", {'user':user,'here':here})

@login_required(login_url='/user_login/')
def profile(request,user_id):

	user = Users.objects.get(id=user_id)
	MEDIA_URL = '/media/'
	here  = "profile"
	return render(request, "profile.html", {'user':user,'MEDIA_URL' : MEDIA_URL,'here':here})

@login_required(login_url='/user_login/')
def map_dashboard(request,user):
	loc_coords = []
	loc_data = csv.reader(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'history/1234.csv'), 'r'))
	
	for ld in loc_data:
		loc_coords.append([])
		loc_coords[-1].append(float(ld[0])) #insert the latitude
		loc_coords[-1].append(float(ld[1])) #insert the longitude
		#ignoring the altitude (2)
	user = Users.objects.get(id=user)
	MEDIA_URL = '/media/'

	return render(request, "map_with_map.html", {'user':user,'MEDIA_URL' : MEDIA_URL, 'locations' : loc_coords})

@login_required(login_url='/user_login/')
def dashboard(request,user):
	user = Users.objects.get(id=user)
	vehicle_location_pair = {}

	try:	
		vehicles = Vehicle.objects.filter(user=user,status = Vehicle.VEHICLE_STATUS[0][0])#get all the active vehicles	
		
		for vehicle in vehicles:
			try:
				gps_data = GpsData.objects.get(gps=vehicle.gps)
				vehicle_location_pair[vehicle]=gps_data
			except:
				print "error"
	except:
		vehicles = None	

	MEDIA_URL = '/media/'
	alert = False
	return render(request, "my_map_with_map.html", {'user':user,'MEDIA_URL' : MEDIA_URL,'vehicle_location_pair':vehicle_location_pair,'zoom_lat':8.98927635 ,'zoom_long':38.78795788,'alert':alert})


@login_required(login_url='/user_login/')
def edit_profile(request,user_id):
	user = Users.objects.get(id=user_id)
	context = RequestContext(request)
	edit_done = False

	if request.method == 'POST':
		changed = get_changed(request)
		print changed
		if('first_name' in changed):
			user.person.first_name = changed['first_name']
		if('middle_name' in changed):
			user.person.middle_name = changed['middle_name']
		if('last_name' in changed):
			user.person.last_name = changed['last_name']
		if('tel' in changed):
			user.person.tel = changed['tel']
		if('sex' in changed):
			user.person.sex = changed['sex']
		if('birthday' in changed):
			user.person.birthday = changed['birthday']
		if('address' in changed):
			user.person.address = changed['address']
		if 'photo' in request.FILES:
		
				user.person.photo = request.FILES['photo']
		
		user.person.save()
		return HttpResponseRedirect('/dashboard/dashboard/profile/'+str(user.id)+'/')	

	here  = "profile"			
	return render_to_response('edit_profile.html',{'edit_done':edit_done,'user':user,'here':here},context)
def get_changed(request):
	changed = {}
	for req in request.POST:
		if request.POST[req]!='':
			changed[req] = request.POST[req]
	return changed




@login_required(login_url='/user_login/')
def manage_vehicles(request,user):
	#TODO send driver info using a dict
	#TODO show some kind of sign when active and not active 
	user = Users.objects.get(id=user)
	alert =False
	try:
		vehicles = Vehicle.objects.filter(user=user)
		
	
	except:
		vehicles = None
	MEDIA_URL = '/media/'
	here  = "vehicle"
	return render(request, "vehicle.html", {'user':user,'MEDIA_URL' : MEDIA_URL,"vehicles":vehicles,'here':here,'alert':alert})

@login_required(login_url='/user_login/')
def manage_drivers(request,user):
	#TODO send vehicle info using a dict

	#TODO show some kind of sign when active and not active
	user = Users.objects.get(id=user)
	vehicle_driver_pair = {}

	try:
		drivers = Driver.objects.filter(user=user)
		for d in drivers:
			try:
				vehicle_driver_pair[d] = Vehicle.objects.get(driver=d)
#  
			except:
				vehicle_driver_pair[d] = None
#				print "vehicle not found !"
#		
	except:
		drivers = None
	here  = "driver"
	MEDIA_URL = '/media/'
	return render(request, "driver.html",  {'user':user,'MEDIA_URL' : MEDIA_URL,'vehicle_driver_pair':vehicle_driver_pair,'here':here})


@login_required(login_url='/user_login/')

def add_driver(request,user):
	context = RequestContext(request)
	registered = False
	user = Users.objects.get(id=user)
	
	if request.method == 'POST':
		driver_form = DriverForm(data=request.POST)
		person_form = PersonForm(data=request.POST)
	
		if driver_form.is_valid() and person_form.is_valid():
			
			driver = driver_form.save(commit=False)
			person = person_form.save(commit=False)
			driver.user = user
			if 'photo' in request.FILES:
				
				person.photo = request.FILES['photo']
			if 'agent_agreement_file' in request.FILES:
				
				driver.agent_agreement_file = request.FILES['agent_agreement_file']
			person.save()			
			driver.person = person
			driver.deassign()
			driver.save()
			registered = True
			return HttpResponseRedirect('/dashboard/manage_drivers/'+str(user.id)+'/')
			
		else:
			print driver_form.errors, person_form.errors
	else:
		driver_form = DriverForm()
		person_form = PersonForm()
# Render the template depending on the context.
	here  = "driver"
	return render_to_response('add_driver.html',{'driver_form': driver_form, 'person_form':person_form, 'registered':registered,'user':user,'here':here},context)

@login_required(login_url='/user_login/')
def remove_driver(request,user_id,driver_id):
	user   = Users.objects.get(id=user_id)
	driver = Driver.objects.get(id=driver_id)
	vehicle = Vehicle.objects.get(driver=driver)
	vehicle.driver = None
	vehicle.save()
	driver.delete()
	
	return HttpResponseRedirect('/dashboard/manage_drivers/'+str(user.id)+'/')

@login_required(login_url='/user_login/')
def edit_driver(request,user_id,driver_id):
	user   = Users.objects.get(id=user_id)
	driver = Driver.objects.get(id=driver_id)
	context = RequestContext(request)

	if request.method == 'POST':
		changed = get_changed(request)
		if('first_name' in changed):
			driver.person.first_name = changed['first_name']
		if('middle_name' in changed):
			driver.person.middle_name = changed['middle_name']
		if('last_name' in changed):
			driver.person.last_name = changed['last_name']
		if('tel' in changed):
			driver.person.tel = changed['tel']
		if('sex' in changed):
			driver.person.sex = changed['sex']
		if('birthday' in changed):
			driver.person.birthday = changed['birthday']
		if('address' in changed):
			driver.person.address = changed['address']
		if 'photo' in request.FILES:
		
				driver.person.photo = request.FILES['photo']
		if 'agent_agreement_file' in request.FILES:
				driver.agent_agreement_file = request.FILES['agent_agreement_file']
		driver.person.save()
		driver.save()

		return HttpResponseRedirect('/dashboard/manage_drivers/'+str(user.id)+'/')				
	here  = "driver"
	return render_to_response('edit_driver.html', {'user':user,'driver':driver,'here':here},context)




@login_required(login_url='/user_login/')
def add_vehicle(request,user_id):
#TODO proper error
	context = RequestContext(request)
	registered = False
	user = Users.objects.get(id=user_id)
	drivers = Driver.objects.filter(user=user,status=Driver.DRIVER_STATUS[1][0])
	gps = None
	errors = None
	if request.method == 'POST':
		vehicle_form = VehicleForm(data=request.POST)
	
		if vehicle_form.is_valid():
			
			
			if 'gps' in request.POST:
				try:
					gps  = GpsDevice.objects.get(device_id=request.POST['gps'], status = GpsDevice.GPS_STATUS[0][0],being_used=GpsDevice.GPS_BEING_USED[1][0])#active and not being used
					gps.set_being_used_yes()
					gps.save()
				except:
				
					return render_to_response('vehicle_error.html',{'user':user},context)
			if 'assign' in request.POST:
				if request.POST['assign']!='':
					try:
					
						driver  = Driver.objects.get(id=request.POST['assign'],status=Driver.DRIVER_STATUS[1][0])#if not assigned yet
						driver.assign()
						driver.save()
					except:
				
						return render_to_response('vehicle_error.html',{'user':user},context)

			vehicle = vehicle_form.save()
			if 'image' in request.FILES:
				vehicle.image = request.FILES['image']	
			vehicle.gps = gps
			try:
				vehicle.driver = driver
			except:
				print "driver not found!!"
			vehicle.user = user
			vehicle.save()

			return HttpResponseRedirect('/dashboard/manage_vehicles/'+str(user.id)+'/')
		else:
			errors=vehicle_form.errors
			print errors
	here  = "vehicle"
	return render_to_response('add_vehicle.html',{'user':user,'drivers':drivers,'errors':errors,'here':here},context)

@login_required(login_url='/user_login/')
def edit_vehicle(request,user_id,vehicle_id):
#TODO proper error
	user   = Users.objects.get(id=user_id)
	vehicle = Vehicle.objects.get(id=vehicle_id)
	
	context = RequestContext(request)
	try:

		drivers = Driver.objects.filter(user=user,status=Driver.DRIVER_STATUS[1][0])#get all drivers not assigned
	except:
		drivers = None


	errors = None
	current_driver = None

	try:
		current_driver = vehicle.driver
	except:
		print "no driver"
		
	if request.method == 'POST':
		changed = get_changed(request)
		
		if('name' in changed):
			vehicle.name = changed['name']
		if('plate_number' in changed):
			vehicle.plate_number = changed['plate_number']
		if('v_model' in changed):
			vehicle.v_model = changed['v_model']
		if('gps' in changed):
			vehicle.gps = GpsDevice.objects.get(device_id=changed['gps'])
		if('brand_name' in changed):
			vehicle.brand_name = changed['brand_name']
		if('engine_cc' in changed):
			vehicle.engine_cc = changed['engine_cc']
		if('color' in changed):
			vehicle.color = changed['color']
		if('status' in changed):
			vehicle.status = changed['status']
		if('assign' in changed):
				try:
					
					driver  = Driver.objects.get(id=request.POST['assign'],status=Driver.DRIVER_STATUS[1][0])#if not assigned yet

					try:
						vehicle.driver.deassign()
						vehicle.driver.save()
					except:
						print "errors"	 						 

					driver.assign()
					driver.save()	
				        vehicle.driver = driver				

				except:
				
					return render_to_response('vehicle_error.html',{'user':user},context)
		if 'image' in request.FILES:
			vehicle.image = request.FILES['image']
		vehicle.save()
		
		return HttpResponseRedirect('/dashboard/manage_vehicles/'+str(user.id)+'/')				
	here   = "vehicle"
	
	return render_to_response('edit_vehicle.html', {'user':user,'vehicle':vehicle,'drivers':drivers,'current_driver':current_driver,'here':here},context)


@login_required(login_url='/user_login/')
def remove_vehicle(request,user_id,vehicle_id):
	user    = Users.objects.get(id=user_id)
	vehicle = Vehicle.objects.get(id=vehicle_id)
	try:
		vehicle.gps.set_being_used_no()
		vehicle.gps.save()
	except:
		print "no gps"
	try:
		vehicle.driver.deassign()
		vehicle.driver.save()
	except:
		print "no driver"

	vehicle.delete()
	return HttpResponseRedirect('/dashboard/manage_vehicles/'+str(user.id)+'/')


@login_required(login_url='/user_login/')
def deactivate_vehicle(request,user_id,vehicle_id):
	user   = Users.objects.get(id=user_id)
	vehicle = Vehicle.objects.get(id=vehicle_id)
	if vehicle.driver is not None:
		vehicle.driver.deassign()
		vehicle.driver.save()
	vehicle.deactivate()
	vehicle.driver = None
	vehicle.save()
	return HttpResponseRedirect('/dashboard/manage_vehicles/'+str(user.id)+'/')

@login_required(login_url='/user_login/')
def activate_vehicle(request,user_id,vehicle_id):
	user   = Users.objects.get(id=user_id)
	vehicle = Vehicle.objects.get(id=vehicle_id)
	vehicle.activate()
	vehicle.save()
	return HttpResponseRedirect('/dashboard/manage_vehicles/'+str(user.id)+'/')
@login_required(login_url='/user_login/')
def search_vehicle_in_map(request,user_id):
#TODO do the search template properly
	user = Users.objects.get(id=user_id)
	
	zoom_lat  = 8.98927635 
	zoom_long = 38.78795788
	MEDIA_URL = '/media/'
	vehicle_location_pair = {}

	if request.method == 'POST':
	
		value  = str(request.POST['item'])
		try:	
			vehicles  = Vehicle.objects.filter(name__contains = value)
			z_vehicle = vehicles[0]#select the first one
			gps_data  = GpsData.objects.get(gps=z_vehicle.gps)
			zoom_lat  = gps_data.latituide_pos	
			zoom_long = gps_data.longtuide_pos
			vehicle_location_pair[z_vehicle]=gps_data

		except:
			try:	
				vehicles = Vehicle.objects.filter(user=user,status = Vehicle.VEHICLE_STATUS[0][0])#get all the active vehicl
				for vehicle in vehicles:
					try:
						gps_data = GpsData.objects.get(gps=vehicle.gps)
						vehicle_location_pair[vehicle]=gps_data
					except:
						print "error"
			except:
				vehicles = None	
		
			alert = True
			return render(request, "my_map_with_map.html", {'user':user,'MEDIA_URL' : MEDIA_URL,'vehicle_location_pair':vehicle_location_pair,'zoom_lat':8.98927635 ,'zoom_long':38.78795788,'alert':alert})		 
	
		return render(request, "my_map_with_map.html", {'user':user,'MEDIA_URL' : MEDIA_URL,'vehicle_location_pair':vehicle_location_pair,'zoom_lat':zoom_lat,'zoom_long':zoom_long})
@login_required(login_url='/user_login/')
def search_vehicle(request,user_id):
#TODO do the search template properly
	user  = Users.objects.get(id=user_id)
	alert = False
	if request.method == 'POST':

		value  = str(request.POST['item'])
			
		vehicles  = Vehicle.objects.filter(name__contains = value)
		
		if len(vehicles)== 0:
			alert = True

		here = 'vehicle'
		MEDIA_URL = '/media/'
		return render(request, "vehicle.html", {'user':user,'MEDIA_URL' : MEDIA_URL,"vehicles":vehicles,'here':here,'alert':alert,'error_vehicle':value})



@login_required(login_url='/user_login/')
def search_driver(request,user_id):

	user  = Users.objects.get(id=user_id)
	if request.method == 'POST':
		
		MEDIA_URL = '/media/'
		value   = str(request.POST['item'])
		persons = Person.objects.filter(first_name__contains = value)
		drivers=[]
		alert = False
		vehicle_driver_pair = {}
		for p in persons:
			      try:
					drivers.append(Driver.objects.get(person=p))
					for d in drivers:
							try:
								vehicle_driver_pair[d] = Vehicle.objects.get(driver=d)
							except:
								vehicle_driver_pair[d] = None			
			      except:
					print "not a driver"
		if len(drivers)==0:
				alert = True
		here = 'driver'		
		return render(request, "driver.html",  {'user':user,'MEDIA_URL' : MEDIA_URL,'vehicle_driver_pair':vehicle_driver_pair,'here':here,'alert':alert,'error_driver':value})

#@login_required(login_url='/user_login/')
def report(request,user_id,vehicle_id):

	user    = Users.objects.get(id=user_id)
	vehicle = Vehicle.objects.get(id=vehicle_id) 
	here    = 'vehicle'

	loc_coords = []
	try:
	
		loc_data = csv.reader(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'history/'+str(vehicle.gps.device_id)+'.csv'), 'r'))

		for ld in loc_data:
			loc_coords.append([])
			loc_coords[-1].append(float(ld[0])) #insert the latitude
			loc_coords[-1].append(float(ld[1])) #insert the longitude

			#ignoring the altitude (2)
	        
		points              = convert_list_to_map_point(loc_coords)
		MEDIA_URL           = '/media/'
		totaldistance       = get_total_distance(loc_coords)
		last_location_lat   = loc_coords[-1][0]
		last_location_long  = loc_coords[-1][1]
		now                 = datetime.datetime.now()
		 
		return render(request, "report.html", {'user':user,'MEDIA_URL' : MEDIA_URL, 'locations' : loc_coords,
											   'vehicle':vehicle,'points':points,'here':here,
											   'totaldistance':totaldistance,'last_location_lat':last_location_lat,
											   'last_location_long':last_location_long,'now':now})
	except:
		return HttpResponseRedirect("/dashboard/manage_vehicles/"+str(user.id)+"/")


def convert_list_to_map_point(my_list):
	points = []
	for i in range(len(my_list)):
		points.append(str(my_list[i][0])+','+str(my_list[i][1]))
	return tuple(points)

def general_report(request,user_id):
	user    = Users.objects.get(id=user_id)	
	here    = 'vehicle'
	return render(request,'report.html',{'user':user,'here':here})




