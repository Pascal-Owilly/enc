from django.db import models
from django.utils.text import slugify
from django.conf import settings
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


from .utils import unique_slug_generator
from django.utils import timezone

import requests
from django.http import JsonResponse


User = get_user_model()




# track vehicle

# MAPBOX_ACCESS_TOKEN = 'your_mapbox_access_token'

# def get_vehicle_location(request, vehicle_id):
#     try:
#         response = requests.get(f'https://api.mapbox.com/your-endpoint-here/{vehicle_id}.json', params={'access_token': MAPBOX_ACCESS_TOKEN})
#         data = response.json()
#         return JsonResponse(data)
#     except requests.exceptions.RequestException as e:
#         return JsonResponse({'error': str(e)}, status=500)

# booking

TYPE = (
    ('OWJ', 'One way journey'),
    ('TWJ', 'Two way journey')
)
    

def room_images_upload_path(instance, file_name):
    return f"{instance.place_slug}/room_cover/{file_name}"


def room_display_images_upload_path(instance, file_name):
    return f"{instance.room.room_slug}/room_display/{file_name}"
 
class Customer(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.customer
    
from django.contrib.auth.models import User  # If you want to associate bookings with users

class Room(models.Model):
    name = models.CharField(max_length=50)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=3)
    room_slug = models.SlugField()
    is_booked = models.BooleanField(default=False)
    capacity = models.IntegerField()
    room_size = models.CharField(max_length=5)
    cover_image = models.ImageField(upload_to=room_images_upload_path)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Place(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    cover_image = models.ImageField(upload_to='place_cover_images/')
    created_at = models.DateTimeField(auto_now=True)
    place_slug = models.SlugField(unique=True, blank=True, default='cover-image')

    def save(self, *args, **kwargs):
        self.place_slug = slugify(self.name)
        super(Place, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # associate bookings with users
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} just booked {self.place} for Ksh {self.place.price} from {self.checkin_date} to {self.checkout_date}'

    def save(self, *args, **kwargs):
        if not self.checkin_date:
            # If checkin_date is not provided, set it to the current date
            self.checkin_date = timezone.now().date()
        if not self.checkout_date:
            # If checkout_date is not provided, set it to 2 days after checkin_date
            self.checkout_date = self.checkin_date + timezone.timedelta(days=2)
        super(Booking, self).save(*args, **kwargs)
    
# payment

class Payment(models.Model):
    payment_id = models.CharField(max_length=255)  # Add this field to store the PayPal payment ID
    status = models.CharField(max_length=50, default="pending")

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,  # Cascade delete when the associated booking is deleted
        default=None,  # Specify a callable function as the default
        null=True,  # Allow the booking field to be NULL
    )
    is_complete = models.BooleanField(default=False)

    payment_date = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f'{self.booking},  Payment status, [{self.is_complete}]'
    
class ExtraCharge(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)  # e.g., 'Kids' or 'Adults'
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Extra charges for {self.booking} is {self.amount} for {self.type}'

        
class PlaceInfo(models.Model):
    destination = models.OneToOneField(Place, on_delete=models.CASCADE, related_name='more_information')
    pictures = models.ImageField(upload_to='place_info_pictures/')
    videos = models.FileField(upload_to='place_info_videos/', blank=True, null=True)
    weather_forecast = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Description for {self.destination.name}"




class CheckIn(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=14, null=True)
    email = models.EmailField(null=True)

    def __str__(self):
        return self.room.room_slug

class CheckOut(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    check_out_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer


class RoomDisplayImages(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    display_images = models.ImageField(upload_to=room_display_images_upload_path)

    def __str__(self):
        return self.room.room_slug
    

    
class About(models.Model):
    desc = models.TextField()
    mission=models.TextField()
    vision = models.TextField()

    def __str__(self):
        return self.desc
    


    


