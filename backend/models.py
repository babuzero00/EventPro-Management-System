from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    # ADD THESE TWO FIELDS TO FIX THE CLASH:
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='backend_user_set', # Unique name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='backend_user_permissions_set', # Unique name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class Event(models.Model):
    """
    The Event Entity: Owned by a user, with structured location details.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events_owned')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # --- UPGRADED LOCATION FIELDS ---
    venue_name = models.CharField(max_length=255, help_text="e.g. Grand Ballroom")
    address = models.TextField(help_text="Street address and building number")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    
    date = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='event_banners/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} at {self.venue_name}"
    
class Booking(models.Model):
    """
    The Relationship Entity: Connects Users to Events they want to attend.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user cannot request the same event twice
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} -> {self.event.title} ({self.status})"
