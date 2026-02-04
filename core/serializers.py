from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ('trust_score', 'created_at', 'updated_at')

        def get_trust_score(self, obj):
            return obj.calculate_trust_score()

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

    def validate(self, data):
        if data['driver'] == data['passenger']:
            raise serializers.ValidationError("راننده و مسافر نمی‌توانند یک نفر باشند")
        return data

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id','trip','from_user','to_user','score','created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        from_user = data['from_user']
        to_user = data['to_user']
        trip = data['trip']
        if Rating.objects.filter(trip=trip, from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("You have already rated this user on this trip.")
        if from_user == to_user:
            raise ValidationError("User cannot rate themselves.")
        if trip.driver != from_user and trip.passenger != from_user:
            raise ValidationError("The rater did not participate in this trip.")
        if trip.driver != to_user and trip.passenger != to_user:
            raise ValidationError("The award recipient did not participate in this trip.")
        if not (1 <= data['score'] <= 5):
            raise ValidationError("The score must be between 1 and 5.")
        return data

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
