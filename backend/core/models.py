from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum


# Create your models here.


class User(models.Model):
    ROLE_CHOICES = (
        ('DRIVER', 'Driver'),
        ('PASSENGER', 'Passenger'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=200, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    trust_score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def number_trip(self):
        return self.trips_as_driver.count() + self.trips_as_passenger.count()

    def __str__(self):
        return f"{self.full_name} ({self.role})"

class Trip(models.Model):
    start_location = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips_as_driver')
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips_as_passenger')
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Trip {self.id}: {self.driver.full_name} → {self.passenger.full_name}"


class Rating(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='ratings')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'from_user')

    def __str__(self):
        return f"{self.from_user} → {self.to_user} | {self.score}⭐"

class Report(models.Model):
    TYPE_CHOICES = (
        ('RUDE_BEHAVIOR', 'Rude behavior'),
        ('NO_SHOW', 'No show'),
        ('LATE_ARRIVAL', 'late arrival'),
        ('DANGEROUS_DRIVING', 'Dangerous driving'),
        ('ROUTE_MANIPULATION', 'Route manipulation'),
        ('PAYMENT_ISSUE', 'Payment issue'),
        ('FAKE_LOCATION', 'Fake location'),
        ('VEHICLE_ISSUE', 'Vehicle issue'),
        ('HARASSMENT', 'Harassment'),
        ('CANCEL_AFTER_ACCEPT', 'Cancel after accept'),
        ('MORE', 'More'),
    )
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_given')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    type = models.CharField(max_length=40, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'reporter', 'reported_user', 'type')

    def __str__(self):
        return f"{self.reporter} reported {self.reported_user} for {self.type}"

class ScoreEvent(models.Model):
    EVENT_TYPES = (
        ('TRIP', 'Trip'),
        ('RATING', 'Rating'),
        ('REPORT', 'Report'),
        ('ADMIN', 'Admin'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='score_events')
    event_type = models.CharField(max_length=40, choices=EVENT_TYPES)
    score_change = models.SmallIntegerField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='score_events', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.event_type} ({self.score_change})"

    @staticmethod
    def recalculate_trust_score(user):
        total = user.score_events.aggregate(total=Sum('score_change'))['total'] or 0
        if total < 0:
            total = 0
        elif total > 100:
            total = 100
        user.trust_score = total
        user.save(update_fields=['trust_score'])




