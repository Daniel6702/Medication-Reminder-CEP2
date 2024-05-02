from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import MQTTConfiguration, Device, Room, StateConfig
from ..forms import MQTTConfigurationForm, DeviceForm, RoomForm, StateConfigForm
import json
from rest_framework.authtoken.models import Token
from django.http import HttpResponseRedirect

class ConfigurationView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/configuration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Getting or creating a token for the user
        token, created = Token.objects.get_or_create(user=self.request.user)
        context['token'] = token
        context['device_form'] = DeviceForm()
        context['devices'] = Device.objects.filter(user=self.request.user)
        context['room_form'] = RoomForm()

        # Getting or creating the MQTT configuration instance for the user
        mqtt_config, created = MQTTConfiguration.objects.get_or_create(
            user=self.request.user,
            defaults={'port': 1883, 'broker_address': 'localhost'}  # Default values
        )
        context['mqtt_form'] = MQTTConfigurationForm(instance=mqtt_config)
        
        rooms = Room.objects.filter(user=self.request.user)
        context['rooms'] = rooms
        rooms_data = [{'room_id': str(room.room_id), 'name': room.name, 'position_x': room.position_x, 'position_y': room.position_y} for room in rooms]
        context['rooms_json'] = json.dumps(rooms_data)
        room_connections = []
        for room in context['rooms']:
            connected_rooms = room.connected_rooms.all()
            for connected_room in connected_rooms:
                room_connections.append({
                    'source': str(room.room_id),
                    'target': str(connected_room.room_id),
                })
        json_rooms = json.dumps(room_connections)
        context['room_connections_json'] = json_rooms

        # Ensure default StateConfig exists
        if not StateConfig.objects.filter(user=self.request.user).exists():
            self.create_default_state_configs(self.request.user)

        state_name = self.request.GET.get('state', 'IDLE')  
        state_config, _ = StateConfig.objects.get_or_create(
            user=self.request.user, 
            state_name=state_name,
            defaults={'color_code': '#FFFFFF'}  
        )
        context['state_config_form'] = StateConfigForm(instance=state_config)
        context['current_state'] = state_name
        context['state_names'] = StateConfig.STATE_NAMES
        context['state_config'] = state_config
        
        return context

    def create_default_state_configs(self, user):
        default_configs = [
            {'state_name': 'IDLE', 'color_code': '#FFFFFF'},
            {'state_name': 'ACTIVE', 'color_code': '#00FF00'},
            {'state_name': 'MEDICATION_TAKEN', 'color_code': '#0000FF'},
            {'state_name': 'MEDICATION_MISSED', 'color_code': '#FF0000'},
            {'state_name': 'ALERT', 'color_code': '#FFFF00'},
        ] 
        
        for config in default_configs:
            StateConfig.objects.create(
                user=user,
                state_name=config['state_name'],
                color_code=config['color_code']
            )

    def post(self, request, *args, **kwargs):
        # Initialize both forms
        mqtt_config, created = MQTTConfiguration.objects.get_or_create(
            user=request.user,
            defaults={'port': 1883, 'broker_address': 'localhost'}
        )
        mqtt_form = MQTTConfigurationForm(request.POST, instance=mqtt_config)

        device_form = DeviceForm(request.POST or None)
        room_form = RoomForm(request.POST or None)

        # Check if MQTT configuration form is submitted 
        if 'mqtt_submit' in request.POST:
            if mqtt_form.is_valid():
                mqtt_form.save()
                return redirect(reverse('configuration'))  # Adjust the redirect as needed

        # Check if Device form is submitted
        elif 'device_submit' in request.POST:
            if device_form.is_valid():
                device = device_form.save(commit=False)
                device.user = request.user
                device.save()
                return redirect(reverse('configuration'))  # Adjust the redirect as needed
            
        # Check if Room form is submitted
        elif 'room_submit' in request.POST:
            if room_form.is_valid():
                room = room_form.save(commit=False)
                room.user = request.user
                room.save() 
                return redirect(reverse('configuration'))  # Adjust the redirect as needed
            
        elif 'state_config_submit' in request.POST:
            state_config_form = StateConfigForm(request.POST, request.FILES, instance=StateConfig.objects.get(user=request.user, state_name=request.POST.get('state_name')))
            if state_config_form.is_valid():
                state_config_form.save()

        elif 'connect_rooms' in request.POST:
            room1_id = request.POST.get('room1_id')
            room2_id = request.POST.get('room2_id')
            try:
                room1 = Room.objects.get(pk=room1_id, user=request.user)
                room2 = Room.objects.get(pk=room2_id, user=request.user)
                room1.connected_rooms.add(room2)  # Add connection
                room1.save()
                return JsonResponse({'status': 'success', 'message': 'Rooms connected successfully.'})
            except Room.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Room not found.'}, status=404)
            
        elif 'update_device_room' in request.POST:
            device_id = request.POST.get('update_device_room')
            device = Device.objects.get(device_id=device_id, user=request.user)
            room_id = request.POST.get('room')
            if room_id:
                device.room = Room.objects.get(room_id=room_id, user=request.user)
            else:
                device.room = None
            device.save()
            
        context = self.get_context_data(mqtt_form=mqtt_form, device_form=device_form, room_form=room_form)
        return self.render_to_response(context)  