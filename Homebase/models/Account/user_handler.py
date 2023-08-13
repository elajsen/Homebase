from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


class UserHandler:
    def __init__(self):
        pass

    def create_user(self, **credentials) -> int:
        """
        Creates a user with the information passed in the data_dict

        :param data_dict -> dict

        :returns int
            1: Success
            0: Failed
        """
        username = credentials.get("username")

        if not User.objects.filter(username=username).exists():
            new_user = User.objects.create_user(**credentials)
            new_user.save()
            return 1
        else:
            return 0

    def delete_user(self, **credentials) -> int:
        """
        Takes credentials and tries to delete a user

        :param:
            credentials: {username, password}

        returns: 
            1: success
            0: failed
        """
        user = authenticate(**credentials)

        if user is not None:
            user.delete()
            return 1
        else:
            return 0

    def login_user(self, request=None, **credentials) -> int:
        """
        Takes credentials and tries to log in an user

        :param
            request -> request object
            credentials -> {username, password}
        """
        if request.user.is_authenticated:
            print("user is already logged in")
            return 1

        user = authenticate(request, **credentials)
        if user is not None:
            login(request, user)
            if request.user.is_authenticated:
                return 1
            else:
                return 0
        else:
            return 0

    def logout_user(self, request) -> int:
        """
        Takes the request object and tried to log it out

        :param
            request -> request object
        """
        if not request.user.is_authenticated:
            return 0

        logout(request)

        if not request.user.is_authenticated:
            return 1
        else:
            return 0
