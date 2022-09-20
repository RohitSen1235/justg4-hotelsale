from django.urls import path,include

from app import views

urlpatterns = [
    path('',views.index,name="index"),
    path('download_file/',views.download_file,name="download_file"),
    path('signup/',views.signup,name="signup"),
    path('login',views.login,name="login"),
    path('registration_successful/',views.registration_successful,name="reg_success"),
]