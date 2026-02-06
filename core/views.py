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
from .serializers import ProfileSerializer, TripSerializer, RatingSerializer, ReportSerializer, RegisterSerializer, \
    LoginSerializer, TripRequestSerializer, UserSerializer
import random
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

# Create your views here.

def home(request):
    return HttpResponse('<h1>Ride Rank</h1>')

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
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

class TripRequestAPIView(generics.CreateAPIView):
    serializer_class = TripRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Not logged in'}, status=401)

        try:
            passenger = User.objects.get(id=user_id, role='PASSENGER')
        except User.DoesNotExist:
            return Response({'error': 'Passenger not found'}, status=404)

        available_drivers = User.objects.filter(
            role='DRIVER'
        ).exclude(id=passenger.id)

        if not available_drivers.exists():
            return Response({'error': 'No available drivers'}, status=400)

        driver = random.choice(list(available_drivers))

        price = random.randint(10,100)

        end_time = timezone.now() + timedelta(minutes=random.randint(5, 30))

        trip = Trip.objects.create(
            start_location=serializer.validated_data['start_location'],
            destination=serializer.validated_data['destination'],
            driver=driver,
            passenger=passenger,
            price=price,
            ended_at=end_time,
        )

        return Response({
            'trip_id': trip.id,
            'driver': driver.full_name,
            'passenger': passenger.full_name,
            'start_location': trip.start_location,
            'destination': trip.destination,
            'price': price,
            'ended_at': trip.ended_at,
        }, status=201)


class TripListAPIView(APIView):
    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Not logged in'}, status=401)

        trips = Trip.objects.filter(Q(driver_id=user_id) | Q(passenger_id=user_id))

        if not trips.exists():
            return Response({'error': 'This User Does Not Have Any Trip'}, status=404)

        serializer = TripSerializer(trips,many=True)
        return Response(serializer.data, status=200)


class RatingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        if not user_id:
            return Rating.objects.none()
        return Rating.objects.filter(
            models.Q(from_user_id=user_id) | models.Q(to_user_id=user_id)
        )

    def perform_create(self, serializer):
        user_id = self.request.session.get('user_id')
        if not user_id:
            raise ValidationError('Not logged in')

        from_user = User.objects.get(id=user_id)
        trip = serializer.validated_data['trip']

        if trip.driver != from_user and trip.passenger != from_user:
            raise ValidationError('You can only rate trips you participated in.')

        to_user = trip.driver if trip.passenger == from_user else trip.passenger

        if Rating.objects.filter(trip=trip, from_user=from_user).exists():
            raise ValidationError('You have already rated this trip.')

        serializer.save(from_user=from_user, to_user=to_user)


class ReportListCreateAPIView(generics.ListCreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class ReportDetailAPIView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
