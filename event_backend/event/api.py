# from django.http import JsonResponse
#
# from rest_framework.decorators import api_view, permission_classes, authentication_classes
#
# from .models import Event
# from .serializers import EventSerializer
#
# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([])
# def event_list(request):
#     """
#     List all events.
#     """
#     events = Event.objects.all()
#     serializer = EventSerializer(events, many=True)
#     return JsonResponse(serializer.data, safe=False)