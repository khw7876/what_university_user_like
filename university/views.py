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

        for index, country_name in enumerate (country_name_list): 
            getted_country, created_country = Country.objects.get_or_create(name = country_name, code = country_code_list[index])
            if getted_country:
                getted_country.country_score = 0
                getted_country.save(update_fields=['country_score'])

        for univercity_data in data:
            country_id = Country.objects.get(name = univercity_data["country"])
            if University.objects.filter(name=univercity_data["name"]):
                University.objects.filter(name=univercity_data["name"]).update(university_score = 0)
            else:
                University.objects.get_or_create(name=univercity_data["name"], webpage = univercity_data["web_pages"][0], country=country_id)

        all_user_queryset = User.objects.all()

        # 각 유저당 20개의 선호 대학교를 지정해주는 로직
        for user in all_user_queryset:
            while user.universitypreference_set.count() <= 20:
                UniversityPreference.objects.create(user = user, university_id = randrange(1,9500))

        # 여기서부터 선호 대학교의 국가 가중치를 계산하고 저장하는 로직
        preference_data = UniversityPreference.objects.all().select_related("university")
        no_overlap_preference_univ_list = []
        preference_univ_name_list = []
        for preference_obj in preference_data:
            if preference_obj.university.name not in preference_univ_name_list:
                preference_univ_name_list.append(preference_obj.university.name)
                no_overlap_preference_univ_list.append(preference_obj)

        for preference_univ_obj in no_overlap_preference_univ_list:
            country_query = Country.objects.filter(university__name = preference_univ_obj.university.name)
            country_query.update(country_score = country_query.get().country_score + 1)

        # 대학교점수(국가가중치 + 선호대학 가중치) 저장하는 로직
        for preference_univ_name in preference_univ_name_list:
            univ_preference_count = UniversityPreference.objects.filter(university__name=preference_univ_name).count()
            univ_count_score = Country.objects.get(university__name = preference_univ_name).country_score

            univ_obj = University.objects.get(name = preference_univ_name)

            univ_obj.university_score = univ_preference_count + univ_count_score
            univ_obj.save(update_fields=['university_score'])

        


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