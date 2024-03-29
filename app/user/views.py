from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """make changes to user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    persmission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrive and reuturn authentication user"""
        return self.request.user
