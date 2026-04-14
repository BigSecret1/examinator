from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .actions import GoogleOAuthAction
from .serializers import GoogleLoginSerializer, UserSerializer


class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = GoogleOAuthAction.authenticate(
            serializer.validated_data['credential'],
        )

        return Response({
            'user': UserSerializer(result['user']).data,
            'access': result['access'],
            'refresh': result['refresh'],
        })


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
