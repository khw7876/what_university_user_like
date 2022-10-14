from user.serializers import UserSignupSerializer
def create_user(create_data : dict[str,str]) -> None:
    """
    Args:
        create_data (dict[str,str]): views.py에서 넘겨준 request.data{
            "username" (str): user의 username,
            "email" (str): user의 email,
            "password: (str): user의 password
        }
    """
    user_data_serializer = UserSignupSerializer(data=create_data)
    user_data_serializer.is_valid(raise_exception=True)
    user_data_serializer.save()
