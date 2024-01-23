from rest_framework import serializers
from .models import User, Contract, UserRegistration

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User    
        fields = ['id', 'username', 'email', 'password', 'number', 'iin', 'metamask_address']
        extra_kwargs = {
            'password' : {'write_only' : True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['id', 'contract_address']

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        fields = ['iin', 'metamask_address', 'is_registered']
