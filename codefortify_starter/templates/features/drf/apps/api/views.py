from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers import HealthSerializer


class HealthAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = HealthSerializer(data={"status": "ok", "service": "api"})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

