"""
WebSocket Consumers for Real-Time Updates
Handles real-time updates for wards, beds, addresses, and deliveries
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from hospital_wards.models import Ward, WardBed, PatientAdmission
from delivery.models import DeliveryAddress


class WardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time ward and bed status updates
    """
    
    async def connect(self):
        """
        Handle WebSocket connection
        """
        self.ward_id = self.scope['url_route']['kwargs'].get('ward_id')
        self.room_group_name = f'ward_{self.ward_id}'
        
        # Verify user has permission to access this ward
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current ward status
        ward_data = await self.get_ward_status()
        await self.send(text_data=json.dumps({
            'type': 'ward_status',
            'data': ward_data
        }))
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection
        """
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Handle incoming messages from client
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'get_status':
                # Send current ward status
                ward_data = await self.get_ward_status()
                await self.send(text_data=json.dumps({
                    'type': 'ward_status',
                    'data': ward_data
                }))
            
            elif action == 'get_bed_status':
                # Send specific bed status
                bed_id = data.get('bed_id')
                bed_data = await self.get_bed_status(bed_id)
                await self.send(text_data=json.dumps({
                    'type': 'bed_status',
                    'data': bed_data
                }))
        
        except Exception as e:
            print(f"Error in WardConsumer.receive: {e}")
    
    async def ward_update(self, event):
        """
        Handle ward update messages from the group
        """
        ward_data = await self.get_ward_status()
        
        await self.send(text_data=json.dumps({
            'type': 'ward_status',
            'data': ward_data,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def bed_status_change(self, event):
        """
        Handle bed status change messages
        """
        bed_id = event['bed_id']
        new_status = event['status']
        patient_id = event.get('patient_id')
        
        await self.send(text_data=json.dumps({
            'type': 'bed_status_change',
            'bed_id': bed_id,
            'status': new_status,
            'patient_id': patient_id,
            'timestamp': timezone.now().isoformat()
        }))
    
    @database_sync_to_async
    def get_ward_status(self):
        """
        Get current ward status including all beds
        """
        try:
            ward = Ward.objects.get(id=self.ward_id, is_active=True)
            beds = WardBed.objects.filter(ward=ward, is_active=True)
            
            bed_data = []
            for bed in beds:
                bed_data.append({
                    'id': bed.id,
                    'bed_number': bed.bed_number,
                    'status': bed.status,
                    'patient': {
                        'id': bed.patient.id,
                        'name': bed.patient.get_full_name() if bed.patient else None
                    } if bed.patient else None,
                    'assigned_date': bed.patient_assigned_date.isoformat() if bed.patient_assigned_date else None,
                })
            
            return {
                'ward_id': ward.id,
                'ward_name': ward.name,
                'total_beds': beds.count(),
                'occupied_beds': beds.filter(status='occupied').count(),
                'available_beds': beds.filter(status='available').count(),
                'beds': bed_data,
                'timestamp': timezone.now().isoformat()
            }
        except Ward.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_bed_status(self, bed_id):
        """
        Get status of a specific bed
        """
        try:
            bed = WardBed.objects.get(id=bed_id, ward_id=self.ward_id, is_active=True)
            
            return {
                'id': bed.id,
                'bed_number': bed.bed_number,
                'status': bed.status,
                'ward': bed.ward.name,
                'patient': {
                    'id': bed.patient.id,
                    'name': bed.patient.get_full_name()
                } if bed.patient else None,
                'assigned_date': bed.patient_assigned_date.isoformat() if bed.patient_assigned_date else None,
            }
        except WardBed.DoesNotExist:
            return None


class DeliveryConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time delivery tracking
    """
    
    async def connect(self):
        """
        Handle WebSocket connection for delivery tracking
        """
        self.room_group_name = 'deliveries'
        
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Handle incoming delivery status updates
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'get_active_deliveries':
                deliveries = await self.get_active_deliveries()
                await self.send(text_data=json.dumps({
                    'type': 'deliveries_list',
                    'data': deliveries
                }))
            
            elif action == 'update_delivery_location':
                order_id = data.get('order_id')
                latitude = data.get('latitude')
                longitude = data.get('longitude')
                
                # Broadcast location update to group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'delivery_location_update',
                        'order_id': order_id,
                        'latitude': latitude,
                        'longitude': longitude,
                        'timestamp': timezone.now().isoformat()
                    }
                )
        
        except Exception as e:
            print(f"Error in DeliveryConsumer.receive: {e}")
    
    async def delivery_location_update(self, event):
        """
        Handle delivery location update messages
        """
        await self.send(text_data=json.dumps({
            'type': 'delivery_location_update',
            'order_id': event['order_id'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'timestamp': event['timestamp']
        }))
    
    async def delivery_status_update(self, event):
        """
        Handle delivery status updates
        """
        await self.send(text_data=json.dumps({
            'type': 'delivery_status_update',
            'order_id': event['order_id'],
            'status': event['status'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def get_active_deliveries(self):
        """
        Get all active deliveries with current status
        """
        from orders.models import Order, OrderStatus
        
        orders = Order.objects.filter(
            status__in=[OrderStatus.READY, OrderStatus.IN_TRANSIT]
        ).values(
            'id', 'created_at', 'status', 'user__get_full_name', 
            'delivery_address__full_address'
        ).order_by('status', 'created_at')
        
        return list(orders)


class AddressConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time address updates and delivery zone changes
    """
    
    async def connect(self):
        """
        Handle WebSocket connection for address updates
        """
        self.user_id = self.scope['user'].id
        self.room_group_name = f'addresses_{self.user_id}'
        
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def address_added(self, event):
        """
        Handle new address added notification
        """
        await self.send(text_data=json.dumps({
            'type': 'address_added',
            'address_id': event['address_id'],
            'address': event['address'],
            'timestamp': event['timestamp']
        }))
    
    async def address_updated(self, event):
        """
        Handle address updated notification
        """
        await self.send(text_data=json.dumps({
            'type': 'address_updated',
            'address_id': event['address_id'],
            'address': event['address'],
            'timestamp': event['timestamp']
        }))
    
    async def delivery_zone_updated(self, event):
        """
        Handle delivery zone update notification
        """
        await self.send(text_data=json.dumps({
            'type': 'delivery_zone_updated',
            'zone': event['zone'],
            'charge': event['charge'],
            'timestamp': event['timestamp']
        }))
