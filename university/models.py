from django.db import models
from user.models import User

# Create your models here.
class Country(models.Model):
    code = models.CharField("국가코드", max_length=2)
    name = models.CharField("국가 영문 이름", max_length=255)
    created_at = models.DateTimeField("생성 일시", auto_now_add=True)

    def __str__(self):
        return self.name

class University(models.Model):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    webpage = models.CharField("대학교 사이트 주소", max_length=255, null=True)
    name = models.CharField("대학교 이름", max_length=255, null=True, unique=True)
    created_at = models.DateTimeField("생성 일시", auto_now_add=True)
    
    def __str__(self):
        return self.name

class UniversityPreference(models.Model):
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField("생성 일시", auto_now_add=True)
    deleted_at = models.DateTimeField("삭제 일시", auto_now=True)

    def __str__(self):
        return self.user