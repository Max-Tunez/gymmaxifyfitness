from django.urls import path
from authapp import views

urlpatterns = [
    path('',views.HomeView,name="Home"),
    path('signup',views.signup,name="signup"),
    path('login',views.handlelogin,name="handlelogin"),
    path('logout',views.handleLogout,name="handleLogout"),
    path('contact',views.contact,name="contact"),
    path('enroll',views.Enroll,name="enroll"),
    path('profile',views.Profile,name="profile"),
    path('gallery',views.gallery_view,name="gallery"),
    path('attendance',views.attendance_view,name="attendance"),
    path('about',views.About,name="about"),
    path('services',views.Services,name="services"),
    path('checkout',views.Checkout,name="checkout"),
    path('dashboard',views.member_dashboard,name="dashboard"),
    path('pricing',views.Pricing,name="pricing"),
    path('payment',views.paystack_init,name="payment"),
    path('upload',views.trainer_upload,name="upload"),
    path('workouts',views.workout_library,name='workouts'),
    path('toggle-freeze', views.toggle_freeze, name='toggle-freeze'),
    
    #generate activation link
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    #resend email activation link
    path('resend-activation/', views.resend_activation, name='resend_activation'),
    #payment history
    path('payment-history/', views.payment_history, name='payment_history'),
]