from django.conf.urls import include, url
from . import views

urlpatterns = [
	url(r'^home/$' , views.home),
	url(r'^login/$' , views.admin_login),
	url(r'^logout/$' , views.admin_logout),

	url(r'^pdf/(?P<user_id>[0-9]+)/(?P<vehicle_id>[0-9]+)/' , views.pdf),

	url(r'^report/(?P<user_id>[0-9]+)/' , views.general_report),		
	#url(r'^charts/bar/', views.barchart),
	url(r'^report/vehicle/(?P<user_id>[0-9]+)/(?P<vehicle_id>[0-9]+)', views.report),
	url(r'^about/(?P<user_id>[0-9]+)/' , views.about),
	url(r'^help/(?P<user_id>[0-9]+)/' , views.help),
	url(r'^gps/(?P<gps_id>[0-9]+)/' , views.handle_gps),	
	url(r'^user_login/$' , views.user_login),
	url(r'^user_logout/$' , views.user_logout),
	url(r'^dashboard/dashboard/(?P<user>[0-9]+)/', views.dashboard, name='dashboard'),	
	url(r'^dashboard/dashboard_map/(?P<user>[0-9]+)/', views.map_dashboard, name='map_dashboard'),
	#url(r'^dashboard/my_dashboard_map/(?P<user>[0-9]+)/', views.my_map_dashboard, name='map_dashboard'),
	url(r'^dashboard/dashboard/profile/(?P<user_id>[0-9]+)/', views.profile, name='profile_dashboard'),
	url(r'^dashboard/dashboard/edit_profile/(?P<user_id>[0-9]+)/', views.edit_profile, name='profile_dashboard'),
	url(r'^dashboard/manage_vehicles/(?P<user>[0-9]+)/', views.manage_vehicles,  name='manage_vehicles'),	
	url(r'^dashboard/manage_drivers/(?P<user>[0-9]+)/', views.manage_drivers,  name='manage_drivers'),

	url(r'^dashboard/add_driver/(?P<user>[0-9]+)/', views.add_driver,  name='add_driver'),
	url(r'^dashboard/edit_driver/(?P<user_id>[0-9]+)/(?P<driver_id>[0-9]+)/', views.edit_driver,  name='edit_driver'),
	url(r'^dashboard/remove_driver/(?P<user_id>[0-9]+)/(?P<driver_id>[0-9]+)/', views.remove_driver,  name='remove_driver'),
	url(r'^dashboard/search_driver/(?P<user_id>[0-9]+)/', views.search_driver,  name='search_driver'),



	url(r'^dashboard/add_vehicle/(?P<user_id>[0-9]+)/', views.add_vehicle,  name='add_vehicle'),
	url(r'^dashboard/edit_vehicle/(?P<user_id>[0-9]+)/(?P<vehicle_id>[0-9]+)/', views.edit_vehicle,   name='edit_vehicle'),	
	url(r'^dashboard/deactivate_vehicle/(?P<user_id>[0-9]+)/(?P<vehicle_id>[0-9]+)/', views.deactivate_vehicle,  name='deactivate_vehicle'),
	url(r'^dashboard/activate_vehicle/(?P<user_id>[0-9]+)/(?P<vehicle_id>[0-9]+)/', views.activate_vehicle,  name='activate_vehicle'),
	url(r'^dashboard/remove_vehicle/(?P<user_id>[0-9]+)/(?P<vehicle_id>[0-9]+)/', views.remove_vehicle,  name='remove_vehicle'),
	url(r'^dashboard/search_vehicle_in_map/(?P<user_id>[0-9]+)/', views.search_vehicle_in_map,  name='search_vehicle'),
	url(r'^dashboard/search_vehicle/(?P<user_id>[0-9]+)/', views.search_vehicle,  name='search_vehicle'),



     	url(r'^admin_dashboard/dashboard/', views.admin_dashboard, name='admin_dashboard'),
	url(r'^admin_dashboard/add_user/',views.admin_dashboard_add_user,  name='add_user'),
	
]
