from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('user/',views.UserListCreateAPIView.as_view(),name='UserListCreateAPI'),
    path('user/<int:pk>/',views.UserDetailAPIView.as_view(),name='UserDetailAPI'),
    path('trip/',views.TripListCreateAPIView.as_view(),name='TripListCreateAPI'),
    path('trip/<int:pk>/',views.TripDetailAPIView.as_view(),name='TripDetailAPI'),
    path('rating/',views.RatingListCreateAPIView.as_view(),name='RatingListCreateAPIView'),
    path('rating/<int:pk>/',views.RatingDetailAPIView.as_view(),name='RatingDetailAPIView'),
    path('report/',views.ReportListCreateAPIView.as_view(),name='ReportListCreateAPI'),
    path('report/<int:pk>/',views.ReportDetailAPIView.as_view(),name='ReportDetailAPI'),
]