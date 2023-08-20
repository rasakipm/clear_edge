from django.urls import path
from . import views

urlpatterns = [
    # Admin Panel URLs
    path('', views.home, name='home'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('student-record/',views.student_record, name='student_record'),
    path('register-student/',views.register_student, name='register_student'),
    path('register-department/',views.register_department, name='register_department'),
    path('admin-login/',views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('status/', views.status, name='status'),
    path('department_dashboard/<uuid:user_id>/', views.department_dashboard, name='department_dashboard'),
    path('approve_clearance_request/<int:request_id>/', views.approve_clearance_request, name='approve_clearance_request'),
    path('decline_clearance_request/<int:request_id>/', views.decline_clearance_request, name='decline_clearance_request'),
    path('view-student-profile/<uuid:student_id>/', views.view_student_profile, name='view_student_profile'),

    # Student Panel URLs
    path('student-dashboard/<uuid:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('student-login/',views.student_login, name='student_login'),
    path('std-logout/', views.std_logout, name='std_logout'),
    path('download_clearance_slip/', views.download_clearance_slip, name='download_clearance_slip')

    ]
