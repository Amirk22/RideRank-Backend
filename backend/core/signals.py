from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Trip, Rating, Report, ScoreEvent

# =========================
# Rating -> ScoreEvent
# =========================
@receiver(post_save, sender=Rating)
def create_scoreevent_from_rating(sender, instance, created, **kwargs):
    if not created:
        return

    score_map = {5: 5, 4: 3, 3: 0, 2: -3, 1: -7}
    change = score_map.get(instance.score, 0)

    ScoreEvent.objects.create(
        user=instance.to_user,
        event_type="RATING",
        score_change=change,
        trip=instance.trip
    )


# =========================
# Report -> ScoreEvent
# =========================
@receiver(post_save, sender=Report)
def report_to_score_event(sender, instance, created, **kwargs):
    if not created:
        return

    report_type = instance.type

    score_map = {
        "RUDE_BEHAVIOR": -5,
        "NO_SHOW": -2,
        "LATE_ARRIVAL": -3,
        "DANGEROUS_DRIVING": -8,
        "ROUTE_MANIPULATION": -7,
        "PAYMENT_ISSUE": -8,
        "FAKE_LOCATION": -10,
        "VEHICLE_ISSUE": -3,
        "HARASSMENT": -10,
        "CANCEL_AFTER_ACCEPT": -10,
    }

    change = score_map.get(report_type, -4)

    ScoreEvent.objects.create(
        user=instance.reported_user,
        event_type="REPORT",
        score_change=change,
        trip=instance.trip
    )


# =========================
# Trip -> ScoreEvent
# =========================
@receiver(post_save, sender=Trip)
def create_scoreevent_from_trip(sender, instance, created, **kwargs):
    if instance.ended_at and not ScoreEvent.objects.filter(trip=instance, event_type='TRIP').exists():
        ScoreEvent.objects.create(
            user=instance.driver,
            event_type='TRIP',
            score_change=5,
            trip=instance
        )
        ScoreEvent.objects.create(
            user=instance.passenger,
            event_type='TRIP',
            score_change=4,
            trip=instance
        )

# =========================
# Update trust_score after any ScoreEvent
# =========================
@receiver(post_save, sender=ScoreEvent)
def update_user_trust_score(sender, instance, created, **kwargs):
    if created:
        ScoreEvent.recalculate_trust_score(instance.user)

