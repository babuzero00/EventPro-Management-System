

# Register your models here.
from django.contrib import admin
from .models import User, Event, Booking

from django.contrib import admin
from .models import Event  # This import is correct ONLY in admin.py

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # What you see in the main list
    list_display = ('title', 'owner', 'venue_name', 'city', 'country', 'date')
    
    # Sidebar filters for easy navigation
    list_filter = ('city', 'country', 'date')
    
    # Search bar to find specific events
    search_fields = ('title', 'venue_name', 'city')
    
    # Grouping fields in the Edit/Create view
    fieldsets = (
        ('Event Overview', {
            'fields': ('title', 'owner', 'description', 'image')
        }),
        ('Location Info', {
            'fields': ('venue_name', 'address', 'city', 'state', 'country')
        }),
        ('Details', {
            'fields': ('date', 'capacity')
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'created_at')
    list_filter = ('status',)

# Keep this for your Custom User model
admin.site.register(User)

# DELETE THE SECOND @admin.register(Booking) BLOCK BELOW THIS