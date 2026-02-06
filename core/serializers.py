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
    class Meta:
        model = Report
        fields = ['trip','reporter','reported_user','type','description','created_at']
        read_only_fields = ['created_at']
    def validate(self, data):
        reporter = data['reporter']
        reported_user = data['reported_user']
        trip = data['trip']
        if reporter == reported_user:
            raise serializers.ValidationError("You cannot report yourself.")
        if Report.objects.filter(trip=trip, reporter=reporter, reported_user=reported_user).exists():
            raise serializers.ValidationError("You have already reported this user for this trip.")
        if trip.driver != reported_user and trip.passenger != reported_user:
            raise serializers.ValidationError("The reported user did not participate in this trip.")
        if trip.driver != reporter and trip.passenger != reporter:
            raise serializers.ValidationError("The reporter did not participate in this trip.")
        return data
