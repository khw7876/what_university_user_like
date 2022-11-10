# what_university_user_like

오픈 소스 데이터셋을 활용한 대학별 선호도 조사 API 기능 구현

  <details>
  <summary>오픈 소스 데이터셋 활용</summary>
  <div markdown="1">
  
  #### 대학교에 대한 정보가 들어있는 오픈소스에서 정보를 가져오기!<br>
    <python>
    
    def get(self, request: Request) -> Response:
        
        url = requests.get("http://universities.hipolabs.com/search")
        text = url.text
        data = json.loads(text)
        
        if not data == cache.get('data'):
            cache.delete('data')
            url = requests.get("http://universities.hipolabs.com/search")
            text = url.text
            data = json.loads(text)
            cache.set('data', data)

        data = cache.get('data')

        if not cache.get('country_name_list'):
            country_name_list = []
            country_code_list = []

            for univercity_data in data:
                if univercity_data["country"] not in country_name_list:
                    country_name_list.append(univercity_data["country"])
                    country_code_list.append(univercity_data['alpha_two_code'])
            cache.set('country_name_list', country_name_list)
            cache.set('country_code_list', country_code_list)

        country_name_list = cache.get('country_name_list')
        country_code_list = cache.get('country_code_list')
        

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
  </div>
  </details>
  <details>
  <summary>사용자 더미데이터 생성 커스텀 커맨드</summary>
  <div markdown="1">
  
  #### Faker를 사용한 커스텀 커맨드를 이용하여 유저 더미데이터 생성!<br>
  
  ```
  python manage.py seed_users --total ${생성할 유저의 수}
  ```
  <python>
   
    class Command(BaseCommand):

      def add_arguments(self, parser) -> None:
          parser.add_argument(
              "--total",
              default=1000,
              type=int,
          )

      def handle(self, *args, **options) -> None:
          total = options.get("total")
          seeder = Seed.seeder()

          seeder.add_entity(
              User,
              total,
              {
                  "username" : lambda x: Faker().name(),
                  "email" : lambda x: seeder.faker.email(),
                  "nickname" : lambda x: Faker().name(),
              },
          )
          seeder.execute()
  </div>
  </details>
  <details>
  <summary>각 유저당 20개의 선호 대학교를 지정해주는 로직</summary>
  <div markdown="1">
  
  #### 각 유저 한명당 20개의 선호 대학교를 랜덤으로 고를 수 있도록 하는 로직<br>
  #### random의 범위는 id = 0인 대학이 없으므로 총 10000개의 대학이 대상이기에 id = 1~9500 이 된다.<br>
    
    all_user_queryset = User.objects.all()
        for user in all_user_queryset:
            while user.universitypreference_set.count() <= 20:
                UniversityPreference.objects.create(user = user, university_id = randrange(1,9500))

  </div>
  </details>
  <details>
  <summary>각 나라가 가지고 있는 대학교의 수를 점수로 매기는 로직</summary>
  <div markdown="1">
  
  #### 만약 한국이 14개의 대학교를 지녔다면, 한국_score = 14<br>
    
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

  </div>
  </details>
  <details>
  <summary>대학교 선호 순위를 매기기 위한 각 대학교의 점수를 구하는 로직</summary>
  <div markdown="1">
  
  #### 4번째에서 구한 국가점수 + 각 대학교의 학생 수<br>
    
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

  </div>
  </details>

</br>

## 💻 기술 스택
<div style='flex'>
<img src="https://img.shields.io/badge/Python3.9.5-3776AB?style=for-the-badge&logo=Python&logoColor=white" >
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=Django&logoColor=white">
</div>
<br>

</br>
</br>

## 📌 컨벤션
### ❓ Commit Message
- feat/ : 새로운 기능 추가/수정/삭제
- enhan/ : 기존 코드에 기능을 추가하거나 기능을 강화할 때
- refac/ : 코드 리팩토링,버그 수정
- test/ : 테스트 코드/기능 추가
- edit/ : 파일을 수정한 경우(파일위치변경, 파일이름 변경, 삭제)

### ❓ Naming
- Class : Pascal 
- Variable : Snake 
- Function : Snake 
- Constant : Pascal + Snake

### ❓ 주석
- Docstring을 활용하여 클래스와 함수단위에 설명을 적어주도록 하자.
- input/output을 명시하여 문서 없이 코드만으로 어떠한 결과가 나오는지 알 수 있도록 하자.

### ❓ Lint
- autopep8 사용




