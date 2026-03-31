from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- 1. AUTHENTICATION ---
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('check-user-role/', views.smart_redirect, name='smart_redirect'),

    # --- 2. ADMIN MODULE (HUGE GLOBAL CONTROL) ---
    # Main Dashboard Stats
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # SEPARATE PAGE: Searchable User List
    path('admin-dashboard/users/', views.global_manage_users, name='manage_users'),
    
    # SEPARATE PAGE: Searchable Global Event List
    # Ensure this points ONLY to global_events_manage
    path('admin-dashboard/events/', views.global_events_manage, name='manage_global_events'),
    path('admin-dashboard/users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    # --- 3. USER MODULE (PERSONAL) ---
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('', views.discover_events, name='discover'),
    path('book/<int:event_id>/', views.book_event, name='book_event'),

    # --- 4. HOST MODULE (MANAGING OWN EVENTS) ---
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    
    # This is the "Host Your Events" link - it MUST stay separate
    path('manage/', views.manage_events, name='manage_events'),
    
    path('event/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('event/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    
    # --- 5. BOOKING & REQUEST LOGIC ---
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    path('requests/update/<int:booking_id>/<str:action>/', 
         views.update_booking_status, name='update_booking_status'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

]
