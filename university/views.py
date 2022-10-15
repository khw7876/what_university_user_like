import requests, json
from random import randrange

from django.db.models import Q

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Country, University, UniversityPreference
from user.models import User

from university.serializers import UniversitySerializer
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

        for univercity_data in data:
            country_id = Country.objects.get(name = univercity_data["country"])
            if University.objects.filter(name=univercity_data["name"]):
                pass
            else:
                University.objects.get_or_create(name=univercity_data["name"], webpage = univercity_data["web_pages"][0], country=country_id)

        all_user_queryset = User.objects.all()

        for user in all_user_queryset:
            while user.universitypreference_set.count() <= 20:
                UniversityPreference.objects.create(user = user, university_id = randrange(1,1000))

        # preference_data = UniversityPreference.objects.all()
        # for preference_obj in preference_data:
        #     preference_obj.university.contry

        return Response({"detail": "정보 저장이 완료되었습니다."}, status=status.HTTP_200_OK)


class SearchView(APIView):
    def get(self, request):
        """
        대학교 검색
            search (str) : 대학교 이름이나 국가코드 검색
            page_limit (int) : 한 페이지에 보여지는 게시글 수
            page (int) : 보고자하는 페이지
            
            return = 검색어 있을 때 : 적용된 대학교의 pk값 내림차순을 최대 10개까지 페이징처리된 serializer.data
                    검색어 없을 때 : '검색어가 비어있습니다' 알림
        """
        search = self.request.GET.get('search', '')
        if search == '':
            return Response ({'detail': '검색어가 비어있습니다'}, status=status.HTTP_404_NOT_FOUND)
        
        university_search = University.objects.filter(
            Q(name__icontains=search) 
            | Q(country__code__icontains=search)
            )
        search_list = university_search.order_by('-pk')
    
        page_limit = int(self.request.GET.get('page-limit', 10))
        page = int(self.request.GET.get('page', 1))
        start_obj = page_limit * (page-1)
        end_obj = page * page_limit
        
        serializer = UniversitySerializer(search_list[start_obj:end_obj], many=True)
        return Response (serializer.data, status=status.HTTP_200_OK)