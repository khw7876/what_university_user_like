from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import requests, json

from .models import Country
# Create your views here.

class UnivercityView(APIView):
    """
    대학교에 관한 View
    """
    def get(self, request: Request) -> Response:
        url = requests.get("http://universities.hipolabs.com/search")
        text = url.text
        data = json.loads(text)
        country_name_list = []
        country_code_list = []
        
        for univercity_data in data:
            if univercity_data["country"] not in country_name_list:
                country_name_list.append(univercity_data["country"])
                country_code_list.append(univercity_data['alpha_two_code'])
        for index, A in enumerate (country_name_list): 
            Country.objects.get_or_create(name = A, code = country_code_list[index])
    

        return Response({"detail": "회원가입을 성공하였습니다"}, status=status.HTTP_200_OK)