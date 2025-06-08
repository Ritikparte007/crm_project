from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def target_list_view(request):
    # Simple placeholder for now
    return Response({'message': 'Targets endpoint working'})