from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    VerifyEmailView,
)

from dj_rest_auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
)

from authentication.views import email_confirm_redirect, password_reset_confirm_redirect, booking_failure, booking_success   
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from django.urls import path, include
from authentication import views

from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static
from .views import CheckoutView, CheckedInView, PlaceViewset, PlaceInfoViewset, PaypalPaymentView,PaypalValidatePaymentView
# from .views import create_payment, payment_success, payment_cancel

# router = DefaultRouter()

urlpatterns = [

    # booking
    
    # path('get_a_room_detail/<str:room_slug>/', RoomDetailView.as_view(), name="single_room"),
    # path('book/', BookingCreateApiView.as_view(), name='book_room'),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('get_current_checked_in_rooms/', CheckedInView.as_view(), name="checked_in_rooms"),

    # path('get_place_list/', PlaceViewset.as_view(), name="place_list"),

    #  authentication

    path("register/", RegisterView.as_view(), name="rest_register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("register/verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path("register/resend-email/", ResendEmailVerificationView.as_view(), name="rest_resend_email"),
    path("account-confirm-email/<str:key>/", email_confirm_redirect, name="account_confirm_email"),
    path("account-confirm-email/", VerifyEmailView.as_view(), name="account_email_verification_sent"),
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path("password/reset/confirm/<str:uidb64>/<str:token>/", password_reset_confirm_redirect, name="password_reset_confirm",
    ),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # payment
    path('booking/success/', views.booking_success, name='booking_success'),
    path('booking/failure/', views.booking_failure, name='booking_failure'),

    # PAYPAL

    path('paypal/create/', PaypalPaymentView.as_view(), name='ordercreate'),
    path('paypal/validate/', PaypalValidatePaymentView.as_view(), name='paypalvalidate'),

    # path('payment/success/', payment_success, name='payment_success'),
    # path('payment/cancel/', payment_cancel, name='payment_cancel'),
    # path('paypal/create/', PaypalPaymentView.as_view(), name='ordercreate'),
    # path('paypal/validate/', PaypalValidatePaymentView.as_view(), name='paypalvalidate'),
]
















