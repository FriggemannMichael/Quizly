from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    """Validate registration requests and create Django users."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        user_model = get_user_model()
        if user_model.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'A user with that username already exists.'
            )
        return value

    def validate_email(self, value):
        user_model = get_user_model()
        if user_model.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError(
                {'confirmed_password': 'Passwords do not match.'}
            )
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirmed_password')
        return get_user_model().objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validate login credentials and expose the authenticated user."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['username'],
            password=attrs['password'],
        )
        if user is None:
            raise serializers.ValidationError('Invalid credentials.')
        attrs['user'] = user
        return attrs
