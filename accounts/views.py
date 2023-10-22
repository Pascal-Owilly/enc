from django.shortcuts import render
from .serializers import ProfileSerializer
# from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from accounts.models import Profile
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError  # Import ValidationError

from django.db import IntegrityError

from allauth.account.views import SignupView
from allauth.account.utils import perform_login
from django.contrib.auth import get_user_model
from accounts.models import Profile

from allauth.account.views import SignupView
from accounts.forms import CustomSignupForm 




# Profile serializers

class ProfileViewset(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by('-created_at')
    serializer_class = ProfileSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            # Get the profile of the authenticated user
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            # Attempt to retrieve the profile to update
            profile = Profile.objects.get(user=request.user)

            # Validate the incoming data with the serializer
            serializer = ProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            return Response({"detail": f"Integrity error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"detail": f"Validation error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_valid(self, form):
        # Call the parent class's form_valid method
        super().form_valid(form)

        # Return the response as usual
        return self.get_success_url()