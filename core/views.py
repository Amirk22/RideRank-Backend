from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from rest_framework import generics, request
from rest_framework import status
from rest_framework import permissions
from .serializers import ProfileSerializer, TripSerializer, RatingSerializer,ReportSerializer ,RegisterSerializer,LoginSerializer

# Create your views here.

def home(request):
    return HttpResponse('<h1>Ride Rank</h1>')

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'error': 'This user does not exist.'}, status=400)
        request.session['user_id'] = user.id
        return Response({'message': 'Logged in', 'user': user.full_name}, status=200)

class LogoutAPIView(APIView):
    permission_classes = []

    def post(self, request):
        request.session.flush()
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)

class ProfileAPIView(APIView):
    def get(self , request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Not logged in'}, status=401)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        serializer = ProfileSerializer(user)
        return Response(serializer.data , status=200)

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
