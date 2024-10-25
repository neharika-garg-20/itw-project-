from django.urls import path

from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
   

    path('',views.home,name="home"),

    path('login/',views.login_view,name='login'),

    path('register/',views.register, name='register'),

    path('profile/',views.profile,name='profile'),

    # path('user_profile',views.user_profile,name='user_profile'),

    path('courses/',views.courses,name='courses'),

    path('course_details/',views.course_details,name='course_details'),

    path('admin_view/',views.admin_view,name='admin_view'),

    path('home_unregistered/',views.home_unregistered,name='home_unregistered'),

    # path('discussion/',views.discussion,name='discussion'),

    path('student_enrollments/',views.student_enrollments,name='student_enrollments'),

    # path('certificates/',views.certificates,name='certificates')

]