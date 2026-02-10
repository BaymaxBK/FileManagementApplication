
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
    path('create_task/',views.create_custom_Tasktable,name="create_task"),
    
    path('create_dashboard/',views.create_statusCount_dashboard,name='create_statuscount_dashboard'),
    path("dashboards/", views.dashboard_list, name="dashboard_list"),
    path("dashboard/<int:dashboard_id>/", views.dashboard_view, name="view_dashboard"),
    path("statusdashboard/<int:dashboard_id>/", views.dashboard_viewdata, name="view_dashboard_data"),
    path('statusdashboard/<int:table_id>/data/', views.fetch_dashboard_data, name='fetch_dashboard_data'),
    path("statusdashboard/<int:dashboard_id>/delete/", views.delete_dashboard, name="dashboard_delete"),


    path('view_tables/', views.view_staff_created_models, name='view_tables'),
    path('assigned_tasks/<int:table_id>/',views.list_assigned_tabletasks_for_admin,name="list_assigned_table_task_admin"),
    path('get_table_fields/<int:table_id>/',views.get_table_fields,name='get_table_fields'),
    
    path('table_data/<str:table_name>/', views.view_table_data, name='view_table_data'),
    path('table_data_datatable/<int:table_id>/', views.view_table_data_updated, name='view_table_data_updated'),
    path('table_data_datatable/<int:table_id>/data/', views.fetch_Table_data, name='fetch_table_data'),
    path("table/update_cell/", views.update_table_cell, name="update_table_cell"),

    path('update/<str:table_name>/', views.update_table_data, name='update_table_data'),
    path('delete_tasktable/<int:tasktable_id>/',views.drop_tasktable,name='drop_tasktable'),
    
    path('delete_table/<int:table_id>/',views.drop_table,name='drop_table'),
    path('update-table/<int:table_id>/', views.update_excel_data, name='update_excel_data'),
    
    path('table_data/view_row_data/<str:table_name>/<str:row_id>/',views.view_row_data,name="view_row_data"),
    path('delete_data/<str:table_name>/',views.delete_table_row,name="delete_table_row"),
    path('delete-rows/<str:table_name>',views.adminViewdata_deleteSeleted_rows,name='adminViewdata_deleteSeleted_rows'),
    path('download_table/<int:table_id>/',views.download_table_as_excel,name="download_table_as_excel"),
    
    # USER ROUTES
    path('user_profile/',views.user_profile,name="user_profile"),
    path('upload_file/', views.upload_file, name='upload_file'),
    #path('choose_table/',views.choose_table,name="choose_table"),

    path('task_table/<int:tasktable_id>/', views.view_taskTable_data, name='view_taskTable_data'),
    path('task_table/<int:tasktable_id>/data/', views.fetch_taskTable_data, name='fetch_table_data'),
    path("task_table/update_cell/", views.update_taskTable_cell, name="update_taskTable_cell"),


    path('user_choose_table/',views.list_tables_for_user,name="user_view_table"),
    path('choose_table/',views.choose_table_and_upload,name="choose_table"), # AJAX URL
    path('my_tasks/', views.user_assigned_tasks, name='user_assigned_tasks'),
    path('update_my_task/<int:tasktable_id>',views.user_update_task_excel_data,name='user_update_taskdata'),
    path('download_task/<int:task_id>/',views.download_Tasktable_as_excel,name="download_Tasktable_as_excel"),
    path('update_status/',views.user_task_update_status,name="user_task_update_status"),
    path('get_sheet_names/',views.get_sheet_names,name='get_sheet_names') # AJAX URL

]



