from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import Notification, Room, Device, MedicationSchedule, HeucodEvent, MQTTConfiguration, StateConfig, Event, Alarmed
from ..serializers import NotificationSerializer, RoomSerializer, DeviceSerializer, MedicationScheduleSerializer, HeucodEventSerializer, MQTTConfigurationSerializer, StateConfigSerializer, EventSerializer, AlarmedSerializer
from django.http import Http404
from django.shortcuts import redirect

class AlarmedAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Try to get the alarm instance for the user, or None if it doesn't exist
        alarm, _ = Alarmed.objects.get_or_create(user=request.user)
        serializer = AlarmedSerializer(alarm)
        return Response(serializer.data)

    def post(self, request):
        # Retrieve the existing alarm instance for the user, or create a new one if it doesn't exist
        alarm, created = Alarmed.objects.get_or_create(user=request.user)
        serializer = AlarmedSerializer(alarm, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(serializer.data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data["user"] = request.user.id  # Add logged in user to the request data
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def delete(self, request, notification_id):
        try:
            notification = Notification.objects.get(notification_id=notification_id, user=request.user)
        except Notification.DoesNotExist:
            return Response({"message": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RoomAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(user=request.user)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, room_id):
        room = Room.objects.get(room_id=room_id)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class DeviceAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = Device.objects.filter(user=request.user)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, device_id):
        device = Device.objects.get(device_id=device_id)
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class StateConfigAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state_configs = StateConfig.objects.filter(user=request.user)
        serializer = StateConfigSerializer(state_configs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = StateConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, state_config_id):
        state_config = StateConfig.objects.get(state_config_id=state_config_id)
        state_config.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
def delete_sound(request, state_config_id):
    try:
        state_config = StateConfig.objects.get(state_config_id=state_config_id)
        if state_config.sound_file:
            state_config.sound_file.delete()  # Delete the file
            state_config.sound_file = None
            state_config.save()
        return redirect('/configuration')
    except StateConfig.DoesNotExist:
        raise Http404("StateConfig not found")

class MedicationScheduleAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        schedules = MedicationSchedule.objects.filter(user=request.user)
        serializer = MedicationScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MedicationScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, schedule_id):
        schedule = MedicationSchedule.objects.get(schedule_id=schedule_id)
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class HeucodEventAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = HeucodEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MQTTConfigurationAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        config, created = MQTTConfiguration.objects.get_or_create(user=request.user)
        serializer = MQTTConfigurationSerializer(config)
        return Response(serializer.data)

    def post(self, request):
        config, created = MQTTConfiguration.objects.get_or_create(user=request.user)
        serializer = MQTTConfigurationSerializer(config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EventAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if request.data is a list of items
        if isinstance(request.data, list):
            serializer = EventSerializer(data=request.data, many=True, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Handle a single item
            serializer = EventSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

