from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import User

from .serializers import UserSerializer


@api_view(['GET', 'POST'])
def users(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
