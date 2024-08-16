from django.urls import path
from .import views

urlpatterns = [
    path("", views.index,name ='index'),  
    path("login/", views.login_user,name ='login'), 
    path('logout/', views.logout_user, name='logout'),
    path("register/", views.register,name ='register'), 
    path('profile/<str:name>/',views.profile_view,name ='profile'),
    path('profile_edit/', views.profile_edit_view, name='profile_edit'),
    path('profile_delete/',views.profile_delete_view,name="profile_delete"),
    path('settings/',views.profile_settings_view,name="profile_settings"),
]