from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Event, Booking
from .forms import EventForm, RegisterForm
from django.utils import timezone

# This ensures we use your custom User model
User = get_user_model()

# --- 1. AUTHENTICATION MODULE ---

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('smart_redirect') 
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('smart_redirect')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def smart_redirect(request):
    """Decides if the user goes to Admin Panel or User Dashboard"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    return redirect('dashboard')


# --- 2. ADMIN MODULE (FULL SYSTEM CONTROL) ---

@login_required
def admin_dashboard(request):
    """The 'Huge' main overview page"""
    if not request.user.is_staff:
        return redirect('dashboard')

    # Using your specific related_names: events_owned and my_bookings
    creators = User.objects.filter(events_owned__isnull=False).distinct()
    bookers = User.objects.filter(my_bookings__isnull=False).distinct()
    
    context = {
        'creators_count': creators.count(),
        'bookers_count': bookers.count(),
        'top_creators': creators[:10],
        'recent_bookers': bookers[:10],
        'total_bookings': Booking.objects.count(),
        'total_users_count': User.objects.count(),
        'events': Event.objects.all().order_by('-created_at')[:5], # Just a preview
        'active_users_preview': User.objects.all().order_by('-last_login')[:12],
    }
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def global_manage_users(request):
    """Separate page for Admin to search and manage all users"""
    if not request.user.is_staff: return redirect('dashboard')
    
    query = request.GET.get('q')
    users = User.objects.all().order_by('-date_joined')
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    return render(request, 'admin/manage_users.html', {'users': users})

@login_required
def global_events_manage(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    query = request.GET.get('q')
    # Use 'date' to match your model choice from the error log
    events = Event.objects.all().order_by('-date')
    
    if query:
        events = events.filter(
            Q(title__icontains=query) | 
            Q(city__icontains=query) |
            Q(owner__username__icontains=query)
        )
    
    return render(request, 'admin/manage_global _events.html', {'events': events})



@login_required
def toggle_user_status(request, user_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    target_user = get_object_or_404(User, id=user_id)
    
    # Prevent admin from suspending themselves
    if target_user == request.user:
        messages.error(request, "You cannot suspend your own administrative account.")
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status = "activated" if target_user.is_active else "suspended"
        messages.success(request, f"User {target_user.username} has been {status}.")
        
    return redirect('manage_users')


# --- 3. USER & HOST MODULES ---

def dashboard(request):
    # Do NOT use @login_required here if you want guests to see the preview
    if request.user.is_authenticated:
        # Fetch real data for logged-in users
        hosted_events = Event.objects.filter(owner=request.user)
        user_bookings = Booking.objects.filter(user=request.user)
    else:
        # Guests get empty lists (the HTML handle the 'Preview' look)
        hosted_events = []
        user_bookings = []
        
    context = {
        'hosted_events': hosted_events,
        'user_bookings': user_bookings,
    }
    return render(request, 'dashboard.html', context)

@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.owner = request.user
            event.save()
            return redirect('manage_events')
    else:
        form = EventForm()
    return render(request, 'user/create_event.html', {'form': form})

def event_detail(request, event_id):
    # This finds the specific event or shows a 404 error if it doesn't exist
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'user/event_detail.html', {'event': event})

@login_required
def manage_events(request):
    """Normal users manage ONLY their own created events"""
    events = Event.objects.filter(owner=request.user)
    return render(request, 'user/manage_event.html', {'events': events})

@login_required
def edit_event(request, event_id):
    # Admin can edit anything, User only their own
    if request.user.is_staff:
        event = get_object_or_404(Event, id=event_id)
    else:
        event = get_object_or_404(Event, id=event_id, owner=request.user)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard' if request.user.is_staff else 'manage_events')
    else:
        form = EventForm(instance=event)
    return render(request, 'user/create_event.html', {'form': form, 'edit_mode': True})

@login_required
def delete_event(request, event_id):
    if request.user.is_staff:
        event = get_object_or_404(Event, id=event_id)
    else:
        event = get_object_or_404(Event, id=event_id, owner=request.user)
    event.delete()
    return redirect('admin_dashboard' if request.user.is_staff else 'manage_events')


# --- 4. DISCOVERY & BOOKING LOGIC ---

def discover_events(request):
    query = request.GET.get('q')
    category = request.GET.get('cat')
    country = request.GET.get('country')
    show_archive = request.GET.get('archive') == 'true' # Toggle for past events
    
    now = timezone.now()

    # 1. Base Filter: Separate Upcoming vs Past
    if show_archive:
        # Show only past events (Archived)
        events = Event.objects.filter(date__lt=now).order_by('-date')
    else:
        # Show only upcoming events (Active)
        events = Event.objects.filter(date__gte=now).order_by('date')

    # 2. Search Logic (Title or City)
    if query:
        events = events.filter(
            Q(title__icontains=query) | 
            Q(city__icontains=query) |
            Q(description__icontains=query)
        )

    # 3. Category Filter
    if category and category != 'all':
        events = events.filter(category__iexact=category)

    # 4. Country Filter (Matches your new slider)
    if country:
        events = events.filter(country__iexact=country)

    context = {
        'events': events,
        'show_archive': show_archive,
        'now': now,
        'current_country': country,
        'current_cat': category
    }
    
    return render(request, 'user/discover.html', context)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_booking = None
    
    if request.user.is_authenticated:
        user_booking = Booking.objects.filter(user=request.user, event=event).first()
    
    return render(request, 'user/event_detail.html', {
        'event': event,
        'user_booking': user_booking
    })

@login_required
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # --- THE HARD BLOCK: Prevent booking if event is in the past ---
    if event.date < timezone.now():
        messages.error(request, "CRITICAL: Cannot book an expired event signal.")
        return redirect('event_detail', event_id=event.id)
    # -------------------------------------------------------------

    # Logic to create booking (Only runs if event is NOT expired)
    booking, created = Booking.objects.get_or_create(user=request.user, event=event)
    
    if created:
        messages.success(request, "Booking request sent!")
    else:
        messages.info(request, "Signal already active.")

    return redirect('event_detail', event_id=event.id)

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    event_id = booking.event.id
    booking.delete()
    messages.success(request, "Booking request cancelled.")
    return redirect('event_detail', event_id=event_id)

# --- 5. GUEST APPROVAL LOGIC ---

@login_required
def manage_requests(request):
    """Hosts see who wants to join their events"""
    requests = Booking.objects.filter(event__owner=request.user).order_by('-created_at')
    return render(request, 'user/manage_request.html', {'requests': requests})

@login_required
def update_booking_status(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security: Only the event owner can touch this
    if booking.event.owner != request.user:
        return redirect('dashboard')

    if action == 'approve':
        booking.status = 'approved'
        booking.save()
    elif action == 'reject':
        booking.status = 'rejected'
        booking.save()
    elif action == 'reset':
        booking.status = 'pending'
        booking.save()
    elif action == 'delete':
        print(f"DELETING BOOKING {booking_id}") # Check your terminal for this!
        booking.delete() 
        messages.success(request, "SIGNAL_PURGED: Record removed from system.")
        return redirect('manage_requests') 

    return redirect('manage_requests')