from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from ..models import Room
import json

@login_required
@require_POST
def delete_room(request):
    try:
        room_id = request.POST.get('room_id')
        room = Room.objects.get(room_id=room_id, user=request.user)
        room.delete()
        return JsonResponse({'status': 'success', 'message': 'Room deleted successfully.'})
    except Room.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Room not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
@require_POST
def add_room(request):
    print(request)
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if room_name:
            try:
                # Attempt to create the room
                new_room = Room.objects.create(name=room_name, user=request.user)
                return JsonResponse({'status': 'success', 'room_id': str(new_room.room_id), 'room_name': new_room.name})
            except Exception as e:
                # Handle any exceptions that occur and return a JSON error response
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Room name is required'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405) 
    
@login_required
@require_POST
def update_room_position(request):
    try:
        room_id = request.POST.get('room_id')
        position_x = request.POST.get('position_x')
        position_y = request.POST.get('position_y')
        room = Room.objects.get(room_id=room_id, user=request.user)
        room.position_x = position_x
        room.position_y = position_y
        room.save()
        return JsonResponse({'status': 'success', 'message': 'Room position updated successfully.'})
    except Room.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Room not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def connect_rooms(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        room1_id = data['room1_id']
        room2_id = data['room2_id']
        
        room1 = Room.objects.get(pk=room1_id, user=request.user)
        room2 = Room.objects.get(pk=room2_id, user=request.user)
        
        room1.connected_rooms.add(room2)  # Add connection
        room1.save()
        
        return JsonResponse({'status': 'success', 'message': 'Rooms connected successfully.'})
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Room.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Room not found.'}, status=404)
    except KeyError:
        return JsonResponse({'status': 'error', 'message': 'Missing data.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)