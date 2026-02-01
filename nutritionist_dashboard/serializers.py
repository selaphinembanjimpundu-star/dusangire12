"""
DRF Serializers for nutritionist dashboard APIs.
Used for REST API endpoints and data validation.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import NutritionistProfile, ClientAssignment

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user details"""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'username']

    def get_full_name(self, obj):
        return obj.get_full_name()


class NutritionistProfileSerializer(serializers.ModelSerializer):
    """Serializer for nutritionist profiles"""

    user = UserDetailSerializer(read_only=True)
    current_client_count = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = NutritionistProfile
        fields = [
            'id',
            'user',
            'user_id',
            'bio',
            'specialization',
            'license_number',
            'phone_number',
            'status',
            'max_clients',
            'current_client_count',
            'is_available',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def get_current_client_count(self, obj):
        return obj.current_client_count

    def get_is_available(self, obj):
        return obj.is_available

    def validate_bio(self, value):
        if value and len(value) > 1000:
            raise serializers.ValidationError(
                "Bio cannot exceed 1000 characters."
            )
        return value

    def validate_max_clients(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "You must be able to manage at least 1 client."
            )
        return value


class ClientAssignmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing client assignments"""

    client = UserDetailSerializer(read_only=True)
    nutritionist = UserDetailSerializer(read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = ClientAssignment
        fields = [
            'id',
            'nutritionist',
            'client',
            'status',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'start_date',
        ]

    def get_is_active(self, obj):
        return obj.is_active


class ClientAssignmentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for client assignments"""

    client = UserDetailSerializer(read_only=True)
    nutritionist = UserDetailSerializer(read_only=True)
    is_active = serializers.SerializerMethodField()
    client_id = serializers.IntegerField(write_only=True, required=False)
    nutritionist_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = ClientAssignment
        fields = [
            'id',
            'nutritionist',
            'nutritionist_id',
            'client',
            'client_id',
            'status',
            'start_date',
            'end_date',
            'notes',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'start_date',
        ]

    def get_is_active(self, obj):
        return obj.is_active

    def validate(self, data):
        """Validate assignment data"""
        # Check that nutritionist and client are different
        nutritionist = data.get('nutritionist')
        client = data.get('client')

        if nutritionist and client and nutritionist == client:
            raise serializers.ValidationError(
                "A user cannot be assigned to themselves as a nutritionist."
            )

        return data


class NutritionistStatsSerializer(serializers.Serializer):
    """Serializer for nutritionist statistics"""

    total_clients = serializers.IntegerField()
    max_clients = serializers.IntegerField()
    available_slots = serializers.IntegerField()
    active_assignments = serializers.IntegerField()
    paused_assignments = serializers.IntegerField()
    completed_assignments = serializers.IntegerField()
    profile_status = serializers.CharField()


class BulkAssignmentActionSerializer(serializers.Serializer):
    """Serializer for bulk assignment actions"""

    assignment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of assignment IDs to act on"
    )
    action = serializers.ChoiceField(
        choices=['activate', 'pause', 'complete', 'terminate'],
        help_text="Action to perform on assignments"
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional notes for the action"
    )
