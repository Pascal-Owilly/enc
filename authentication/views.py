from django.shortcuts import render

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404


from rest_framework import generics, permissions, status, viewsets
from authentication.models import  About, Room, CheckIn, Place, PlaceInfo, Booking, Payment, ExtraCharge
from .serializers import (AboutSerializer,
                            CheckinSerializer,
                            PlaceSerializer,
                            PlaceInfoSerializer,
                            BookingSerializer, 
                            PaymentSerializer,
                         )


from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status, filters
from rest_framework.response import Response

from django.db.models import Q  # Import Q for complex lookups
from rest_framework.decorators import action  # Import the action decorator

from .permissions import IsAuthorOrReadOnly
from django.contrib.auth.decorators import login_required
import requests

import paypalrestsdk
from django.conf import settings

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

import os

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

import json
import base64

import paypalrestsdk

import logging  # Import the logging module

from datetime import datetime, timedelta

from authentication.utils import make_paypal_payment,verify_paypal_payment

import logging


# Create a logger
logger = logging.getLogger(__name__)


# booking
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def calculate_checkout_date(self, checkin_date):
        checkin_datetime = datetime.strptime(checkin_date, '%Y-%m-%d')
        checkout_datetime = checkin_datetime + timedelta(days=1)  # Adjust the number of days as needed
        return checkout_datetime.strftime('%Y-%m-%d')
    
    def calculate_extra_charges_for_kids(self):
        # Define the price per kid
        price_per_kid = 1000  # Adjust the price as needed

        # Extract the number of kids from the request data
        num_kids = self.request.data.get('numKids', 0)  # Default to 0 if not provided

        # Calculate extra charges for kids
        extra_charges_for_kids = num_kids * price_per_kid

        return extra_charges_for_kids

    def calculate_extra_charges_for_adults(self):
        # Define the price per adult
        price_per_adult = 3000  # Adjust the price as needed

        # Extract the number of adults from the request data
        num_adults = self.request.data.get('numAdults', 1)  # Default to 1 if not provided

        # Subtract 1 for the default adult (you can adjust this logic if needed)
        extra_charges_for_adults = (num_adults - 1) * price_per_adult

        return extra_charges_for_adults
    

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            if 'checkin_date' in data and 'checkout_date' not in data:
                # Calculate the checkout_date if it's missing
                data['checkout_date'] = self.calculate_checkout_date(data['checkin_date'])

            # Ensure the user is authenticated
            if not self.request.user.is_authenticated:
                return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)
            
                # Assign the user based on the currently logged-in user's ID
            data['user'] = self.request.user.id  # Use the currently logged-in user's ID
            # Extract the selected place ID from the request data

            place_id = data.get('place')
            # Check if the place with the given place_id exists
            try:
                 place = Place.objects.get(id=place_id)
            except Place.DoesNotExist:
                return Response({"error": "Selected place does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            
                # Assign the selected place to the booking
            data['place'] = place.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Log response data
            logging.debug(f"Response data: {serializer.data}")


            # Now, calculate extra charges and add them to the booking
            booking = serializer.instance  # Get the created booking instance

            # Calculate extra charges for different types (e.g., 'Kids' and 'Adults')
            extra_charges_for_kids = self.calculate_extra_charges_for_kids()
            extra_charges_for_adults = self.calculate_extra_charges_for_adults()

            # Create and save ExtraCharge instances for each type
            ExtraCharge.objects.create(booking=booking, type='Kids', amount=extra_charges_for_kids)
            ExtraCharge.objects.create(booking=booking, type='Adults', amount=extra_charges_for_adults)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

            logging.debug(f"Data being sent to the backend: {data}")

        
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating booking: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Existing view using the Payment model
class PaymentListView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Modify your create method as needed


class PlaceViewset(viewsets.ModelViewSet):
    queryset = Place.objects.all().order_by('-id')
    serializer_class = PlaceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name__icontains', 'price__icontains', 'description__icontains']

    @action(detail=False, methods=['GET'])
    def search(self, request):
        try:
            query = request.query_params.get('query', '')

            results = Place.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            ).order_by('-created_at')

            serializer = PlaceSerializer(results, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
            try:
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            except Exception as e:
                logger.error(f"Error updating place: {str(e)}")  # Log the error
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlaceInfoViewset(viewsets.ModelViewSet):
    queryset = PlaceInfo.objects.all().order_by('-id')
    serializer_class = PlaceInfoSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]



class CheckoutView(APIView):
    def post(self, request):
        room = get_object_or_404(Room, pk=request.data['pk'])
        checked_in_room = CheckIn.objects.get(room__pk=request.data['pk'])
        print(checked_in_room)
        room.is_booked = False
        room.save()
        
        return Response({"Checkout Successful"}, status=status.HTTP_200_OK)



class CheckedInView(generics.ListAPIView):
    # permission_classes = (IsAdminUser, )
    serializer_class = CheckinSerializer
    queryset = CheckIn.objects.order_by('-id')



def email_confirm_redirect(request, key):
    return HttpResponseRedirect(
        f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/"
    )


def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )

def booking_success(request):
    # Perform any necessary actions for a successful booking
    # For example, display a success message and render a template
        return Response({'message': 'Booking successfully'})
def booking_failure(request):
    # Perform any necessary actions for a failed booking
    # For example, display a failure message and render a template
        return Response({'message': 'Booking failed'})

# Paypal payment

def paypalToken(client_ID, client_Secret):

    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {
                "client_id":client_ID,
                "client_secret":client_Secret,
                "grant_type":"client_credentials"
            }
    headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Basic {0}".format(base64.b64encode((client_ID + ":" + client_Secret).encode()).decode())
            }

    token = requests.post(url, data, headers=headers)
    return token.json()['access_token']

clientID = getattr(settings, 'PAYPAL_SANDBOX_CLIENT_ID')
clientSecret = getattr(settings, 'PAYPAL_SANDBOX_CLIENT_SECRET')
    

class PaypalPaymentView(APIView):
    """
    Endpoint for creating a PayPal payment URL.
    """
    def post(self, request, *args, **kwargs):
        print("PaypalPaymentView is executed")
        print(request.data)
        # Fetch the relevant data from the request
        place_id = request.data.get("id")

        # Retrieve the associated Place object
        place = get_object_or_404(Place, id=place_id)

        # Extract the price from the Place object
        price = place.price

        formatted_price = "{:.2f}".format(price)
        print("Price from Place object:", price)

        # Perform PayPal payment request
        status, payment_id, approved_url = make_paypal_payment(
            formatted_price,
            currency="USD",
            return_url="https://enceptics.vercel.app//payment/status/success",
            cancel_url="https://enceptics.vercel.app//payment/status/cancel/"
        )

        print("PayPal API Response:")
        print(json.dumps({"status": status, "payment_id": payment_id, "approved_url": approved_url}, indent=2))

        if status:
            # Save payment information and set is_complete based on payment status
            payment, created = Payment.objects.get_or_create(payment_id=payment_id)
            payment.is_complete = True if payment.status == "approved" else False
            payment.save()

            # Return a response indicating success and the approved URL
            return Response({"success": True, "msg": "Payment link has been successfully created", "approved_url": approved_url}, status=201)
        else:
            return Response({"success": False, "msg": "Authentication or payment failed"}, status=400)

class PaypalValidatePaymentView(APIView):
    """
    endpoint for validate payment 
    """
    permission_classes=[permissions.IsAuthenticated,]
    def post(self, request, *args, **kwargs):
        payment_id=request.data.get("payment_id")
        payment_status=verify_paypal_payment(payment_id=payment_id)
        if payment_status:
                
            return Response({"success":True,"msg":"payment approved"},status=200)
        else:
            return Response({"success":False,"msg":"payment failed or cancelled"},status=200)        

# END EXAMPLE


'''
# Function to obtain PayPal access token

def PaypalToken(client_ID, client_Secret):
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {
        "client_id": client_ID,
        "client_secret": client_Secret,
        "grant_type": "client_credentials"
    }
    auth_string = f"{client_ID}:{client_Secret}".encode('utf-8')
    encoded_auth_string = base64.b64encode(auth_string).decode('utf-8')
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_auth_string}"
    }
    token = requests.post(url, data, headers=headers)
    return token.json().get('access_token')

# Define a ViewSet for creating PayPal orders
class CreateOrderViewSet(viewsets.ViewSet):

    def create(self, request):
      # Get PayPal credentials from Django settings
        clientID = getattr(settings, 'PAYPAL_SANDBOX_CLIENT_ID', None)
        clientSecret = getattr(settings, 'PAYPAL_SANDBOX_CLIENT_SECRET', None)
        
        # Check if the credentials are set
        if not clientID or not clientSecret:
            raise Exception("PayPal credentials not found in Django settings.")
        # Handle the creation of a PayPal order here
        try:
            # Example code for obtaining token and making API call:
            token = PaypalToken(clientID, clientSecret)
            if not token:
                raise Exception("Failed to obtain PayPal access token")
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
            }
            json_data = {
                "intent": "CAPTURE",
                "application_context": {
                   "notify_url": "https://www.sandbox.paypal.com/notify_url",
                   "return_url": "https://www.sandbox.paypal.com/return_url",
                   "cancel_url": "https://www.sandbox.paypal.com/cancel_url",

                    "brand_name": "PESAPEDIA SANDBOX",
                    "landing_page": "BILLING",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "CONTINUE"
                },
                "purchase_units": [
                    {
                        "reference_id": "71215417",
                        "description": "Enceptics Tours and Vacation",
                        "custom_id": "ENC-Vacay",
                        "soft_descriptor": "Enceptics",
                        "amount": {
                            "currency_code": "USD",
                            "value": "1"  # Update with the correct amount
                        },
                    }
                ]
            }
            response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', headers=headers, json=json_data)

            if response.status_code == 201:
                order_id = response.json().get('id')
                linkForPayment = response.json().get('links')[1].get('href')
                return Response({'order_id': order_id, 'linkForPayment': linkForPayment}, status=status.HTTP_201_CREATED)
            else:
                
                # Handle the case when PayPal order creation fails
                response_data = response.json()
                error_details = response_data.get('details', [])
                error_messages = [detail.get('description', 'Unknown error') for detail in error_details]
                error_message = response.json().get('message', 'Failed to create PayPal order')
                return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Handle other exceptions, such as network errors, here
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CaptureOrderView(viewsets.ViewSet):
    def get(self, request):
        token = request.data.get('token')
        captureurl = request.data.get('url')
        
        if captureurl is None:
            # Handle the case when 'url' key is missing or has a value of None
            # Return an appropriate response or raise an exception
            # For example:
            return Response({'error': 'Missing or invalid capture URL.'}, status=400)
        
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
        response = requests.post(captureurl, headers=headers)
        return Response(response.json())
        '''