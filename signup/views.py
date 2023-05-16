from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Signup
from .serializers import SignupSerializer
from rest_framework import status
from django.contrib.auth.hashers import check_password


@api_view(['POST'])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)
    if request.data.get('password') != request.data.get('confirm_password'):
        return Response({"error": "Password and Confirm Password do not match."}, status=400)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = Signup.objects.get(email=username)
    except Signup.DoesNotExist:
        return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(password, user.password):
        return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    # Authentication successful
    return Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)
