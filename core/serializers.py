from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'role','trust_score']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ('trust_score', 'created_at', 'updated_at')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'role']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This user has already registered.")
        return value

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()


class TripRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['start_location', 'destination']

class TripSerializer(serializers.ModelSerializer):
    driver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='DRIVER')
    )
    passenger = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='PASSENGER')
    )

    driver_name = serializers.CharField(source='driver.full_name', read_only=True)
    passenger_name = serializers.CharField(source='passenger.full_name', read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'start_location', 'destination', 'price',
            'driver', 'driver_name', 'passenger', 'passenger_name', 'created_at', 'ended_at'
        ]
        read_only_fields = ['created_at', 'driver_name', 'passenger_name']


class RatingSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(read_only=True)

    trip = serializers.PrimaryKeyRelatedField(
        queryset=Trip.objects.none()
    )

    class Meta:
        model = Rating
        fields = ['id', 'trip', 'from_user', 'to_user', 'score', 'created_at']
        read_only_fields = ['id', 'created_at', 'from_user', 'to_user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_id = self.context['request'].session.get('user_id')
        if user_id:
            self.fields['trip'].queryset = Trip.objects.filter(
                models.Q(driver_id=user_id) | models.Q(passenger_id=user_id)
            )

    def validate_score(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("The score must be between 1 and 5.")
        return value



class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.PrimaryKeyRelatedField(read_only=True)
    reported_user = serializers.PrimaryKeyRelatedField(read_only=True)

    trip = serializers.PrimaryKeyRelatedField(
        queryset=Trip.objects.none()
    )
    class Meta:
        model = Report
        fields = ['trip','reporter','reported_user','type','description','created_at']
        read_only_fields = ['created_at']

    PASSENGER_REPORT_TYPES = [
        ('RUDE_BEHAVIOR', 'Rude behavior'),
        ('NO_SHOW', 'No show'),
        ('LATE_ARRIVAL', 'Late arrival'),
        ('DANGEROUS_DRIVING', 'Dangerous driving'),
        ('ROUTE_MANIPULATION', 'Route manipulation'),
        ('VEHICLE_ISSUE', 'Vehicle issue'),
        ('HARASSMENT', 'Harassment'),
        ('CANCEL_AFTER_ACCEPT', 'Cancel after accept'),
        ('MORE', 'More'),
    ]

    DRIVER_REPORT_TYPES = [
        ('RUDE_BEHAVIOR', 'Rude behavior'),
        ('NO_SHOW', 'No show'),
        ('LATE_ARRIVAL', 'Late arrival'),
        ('PAYMENT_ISSUE', 'Payment issue'),
        ('FAKE_LOCATION', 'Fake location'),
        ('HARASSMENT', 'Harassment'),
        ('CANCEL_AFTER_ACCEPT', 'Cancel after accept'),
        ('MORE', 'More'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_id = self.context['request'].session.get('user_id')
        if user_id:
            self.fields['trip'].queryset = Trip.objects.filter(
                models.Q(driver_id=user_id) | models.Q(passenger_id=user_id)
            )
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user = None
            if user.role == 'DRIVER':
                self.fields['type'].choices = self.DRIVER_REPORT_TYPES
            elif user.role == 'PASSENGER':
                self.fields['type'].choices = self.PASSENGER_REPORT_TYPES




