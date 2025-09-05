
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    
    # Authentication routes
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # ADMIN ROUTES
    path('admin_dashboard/',views.user_admin,name='admin_dashboard'),
    path('create_table/',views.create_custom_table,name='create_table'),
    path('view_tables/', views.view_staff_created_models, name='view_tables'),
    path('get_table_fields/<int:table_id>/',views.get_table_fields,name='get_table_fields'),
    
    path('table_data/<str:table_name>/', views.view_table_data, name='view_table_data'),
    path('update/<str:table_name>/', views.update_table_data, name='update_table_data'),
    
    path('delete_table/<int:table_id>/',views.drop_table,name='drop_table'),
    path('table_data/view_row_data/<str:table_name>/<str:row_id>/',views.view_row_data,name="view_row_data"),
    path('delete_data/<str:table_name>/',views.delete_table_row,name="delete_table_row"), 
    
    # USER ROUTES
    path('user_profile/',views.user_profile,name="user_profile"),
    path('upload_file/', views.upload_file, name='upload_file'),
    #path('choose_table/',views.choose_table,name="choose_table"),
    path('choose_table/',views.choose_table_and_upload,name="choose_table"), # AJAX URL
    path('get_sheet_names/',views.get_sheet_names,name='get_sheet_names') # AJAX URL

]



