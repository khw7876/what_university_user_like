from rest_framework import serializers
from .models import User as UserModel
from django.contrib.auth.password_validation import validate_password
class UserSignupSerializer(serializers.ModelSerializer):

    def validate(self, data):
        validate_password(data["password"])
        return data

    def create(self, *args, **kwargs):
        user = super().create(*args, **kwargs)
        p = user.password
        user.set_password(p)
        user.save()
        return user
    
    class Meta:
        model = UserModel
        fields = "__all__"