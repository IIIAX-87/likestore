from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Address, PasswordReset

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'avatar', 'birthday', 'gender', 'notify_orders',
            'notify_promotions', 'date_joined'
        ]
        read_only_fields = ['id', 'email', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Password reset request serializer."""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirm serializer."""
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])

    def validate_token(self, value):
        try:
            reset = PasswordReset.objects.get(token=value, used=False)
            if reset.expires_at < timezone.now():
                raise serializers.ValidationError('Token has expired')
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError('Invalid token')
        return value

    def save(self):
        reset = PasswordReset.objects.get(token=self.validated_data['token'])
        reset.user.set_password(self.validated_data['new_password'])
        reset.user.save()
        reset.used = True
        reset.save()
        return reset.user


class AddressSerializer(serializers.ModelSerializer):
    """Address serializer."""

    class Meta:
        model = Address
        fields = [
            'id', 'name', 'city', 'street', 'house',
            'apartment', 'postal_code', 'comment', 'is_default'
        ]


from django.utils import timezone
