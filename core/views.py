from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions

from .serializers import UserSerializer, TripSerializer, RatingSerializer,ReportSerializer

# Create your views here.

def home(request):
    return HttpResponse('<h1>Ride Rank</h1>')


class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TripListCreateAPIView(generics.ListCreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class TripDetailAPIView(generics.RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

class RatingListCreateAPIView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class RatingDetailAPIView(generics.RetrieveAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class ReportListCreateAPIView(generics.ListCreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class ReportDetailAPIView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
