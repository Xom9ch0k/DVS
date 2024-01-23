from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, ContractSerializer, UserRegistrationSerializer
from .models import User, Contract, UserRegistration
from django.contrib.auth import get_user_model
import jwt, datetime
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveDestroyAPIView

# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        number = request.data.get('number')
        password = request.data.get('password')
        metamask_address = request.data.get('metamask_address')

        if not email or not password or not metamask_address:
            raise AuthenticationFailed('Email, password, and Metamask address are required.')

        user = get_user_model().objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        # Check if the Metamask address matches
        if user.metamask_address != metamask_address:
            raise AuthenticationFailed('Metamask address does not match')

        payload = {
            'id' : user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message' : 'success'
        }

        return response

# class ContractView(APIView):
#     def get(self, request):
#         contracts = Contract.objects.all()
#         serializer = ContractSerializer(contracts, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = ContractSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractView(RetrieveDestroyAPIView):
    def post(self, request):
        contract_address = request.data.get('contract_address')

        if not contract_address:
            return Response({'error': 'Адрес контракта обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        # Удаляем текущую запись (если она существует)
        Contract.objects.all().delete()

        UserRegistration.objects.all().delete()

        # Создаем новую запись
        contract = Contract.objects.create(contract_address=contract_address)

        serializer = ContractSerializer(contract)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        # Получаем текущую запись (если она существует)
        contract = Contract.objects.first()

        if not contract:
            return Response({'error': 'Нет доступных записей о контрактах'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContractSerializer(contract)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckAdminView(APIView):
    def get(self, request, metamask_address):
        user = get_object_or_404(User, metamask_address=metamask_address)
        is_admin = user.isAdmin
        return Response({'isAdmin': is_admin}, status=status.HTTP_200_OK)
    
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            iin = serializer.validated_data['iin']
            metamask_address = serializer.validated_data['metamask_address']

# Check if a user with the same iin and metamask_address exists in the general table
            existing_user = User.objects.filter(iin=iin, metamask_address=metamask_address).first()
            if not existing_user:
                return Response({'error': 'User with the specified iin and metamask_address not found in the general table.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if a user with the same iin and metamask_address already exists in the voting table
            existing_registration = UserRegistration.objects.filter(iin=iin, metamask_address=metamask_address).first()
            if existing_registration:
                return Response({'error': 'User with the same iin and metamask_address is already registered for voting.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        users = UserRegistration.objects.all()
        serializer = UserRegistrationSerializer(users, many=True)
        return Response(serializer.data)

class VoterRegistrationView(APIView):
    def post(self, request):
        user_address = request.data.get('user_address')
        try:
            user_registration = UserRegistration.objects.get(metamask_address=user_address)
            user_registration.is_registered = True
            user_registration.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_200_OK)
        except UserRegistration.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)