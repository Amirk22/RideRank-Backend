from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('list-users/',views.UserListAPIView.as_view(),name='UserListAPIView'),
    path('profile/',views.ProfileAPIView.as_view(),name='profile'),
    path('register/',views.RegisterAPIView.as_view(),name='RegisterAPI'),
    path('login/',views.LoginAPIView.as_view(),name='LoginAPI'),
    path('logout/',views.LogoutAPIView.as_view(),name='LogoutAPI'),
    path('trip/',views.TripRequestAPIView.as_view(),name='TripRequestAPIView'),
    path('trip-list/',views.TripListAPIView.as_view(),name='TripListAPI'),
    path('rating/',views.RatingListAPIView.as_view(),name='RatingListAPIView'),
    path('report/',views.ReportListCreateAPIView.as_view(),name='ReportListCreateAPI'),
    path('report/<int:pk>/',views.ReportDetailAPIView.as_view(),name='ReportDetailAPI'),
]