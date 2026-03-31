from django import forms
from .models import Event, User

class EventForm(forms.ModelForm):
    """
    Upgraded Form for Users to create/edit their events with structured location data.
    """
    class Meta:
        model = Event
        # Updated fields to match your upgraded Model
        fields = [
            'title', 'description', 'venue_name', 'address', 
            'city', 'state', 'country', 'date', 'capacity', 'image'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control rounded-pill', 
                'placeholder': 'Enter a catchy title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control rounded-4', 
                'rows': 3, 
                'placeholder': 'What is your event about?'
            }),
            # --- NEW LOCATION WIDGETS ---
            'venue_name': forms.TextInput(attrs={
                'class': 'form-control rounded-pill', 
                'placeholder': 'e.g. Grand Ballroom or Tech Hub'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control rounded-4', 
                'rows': 2, 
                'placeholder': 'Street address, Building, Suite...'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control rounded-pill', 
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control rounded-pill', 
                'placeholder': 'State/Province'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control rounded-pill', 
                'placeholder': 'Country'
            }),
            # --- END LOCATION WIDGETS ---
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control rounded-pill', 
                'type': 'datetime-local'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control rounded-pill', 
                'placeholder': 'Maximum guests'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

class RegisterForm(forms.ModelForm):
    """
    Standard registration with a password confirmation check.
    """
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control rounded-pill', 
        'placeholder': 'Create password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control rounded-pill', 
        'placeholder': 'Repeat password'
    }))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Email address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data