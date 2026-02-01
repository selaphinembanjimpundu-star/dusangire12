"""
Admin logging utilities for tracking admin panel activities
"""
import logging
import json
from functools import wraps
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from .models import AdminLog

# Configure logging
logger = logging.getLogger('admin_panel')


def get_client_ip(request):
    """
    Extract client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Extract user agent from request
    """
    return request.META.get('HTTP_USER_AGENT', '')[:500]


def log_admin_action(
    user,
    action,
    model_name,
    description,
    object_id=None,
    old_values=None,
    new_values=None,
    status='SUCCESS',
    error_message='',
    request=None,
    duration_ms=None
):
    """
    Log an admin action to the database
    
    Args:
        user: The admin user performing the action
        action: Type of action (CREATE, UPDATE, DELETE, etc.)
        model_name: Name of the model affected
        description: Detailed description of the action
        object_id: ID of the affected object
        old_values: Previous values (dict or JSON)
        new_values: New values (dict or JSON)
        status: Status of the action (SUCCESS, FAILED, PENDING, WARNING)
        error_message: Error message if failed
        request: HTTP request object (optional, for IP and user agent)
        duration_ms: Duration of action in milliseconds
    
    Returns:
        AdminLog instance
    """
    try:
        log_entry = AdminLog.objects.create(
            admin_user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            status=status,
            error_message=error_message,
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else '',
            duration_ms=duration_ms
        )
        
        # Also log to Python logger
        log_level = logging.ERROR if status == 'FAILED' else logging.INFO
        logger.log(
            log_level,
            f"Admin Action: {action} on {model_name}#{object_id} by {user} - {description}"
        )
        
        return log_entry
    except Exception as e:
        logger.error(f"Failed to create admin log: {str(e)}")
        return None


def admin_action_logger(action, model_name):
    """
    Decorator to automatically log admin actions
    
    Usage:
        @admin_action_logger('UPDATE', 'Order')
        def update_order(request, order_id):
            # Your code here
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                response = view_func(request, *args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Log successful action
                log_admin_action(
                    user=request.user,
                    action=action,
                    model_name=model_name,
                    description=f"{action} performed on {model_name}",
                    object_id=kwargs.get('pk') or kwargs.get('id'),
                    status='SUCCESS',
                    request=request,
                    duration_ms=duration_ms
                )
                
                return response
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Log failed action
                log_admin_action(
                    user=request.user,
                    action=action,
                    model_name=model_name,
                    description=f"Failed to {action} on {model_name}",
                    object_id=kwargs.get('pk') or kwargs.get('id'),
                    status='FAILED',
                    error_message=str(e),
                    request=request,
                    duration_ms=duration_ms
                )
                
                raise
        
        return wrapper
    return decorator


def log_model_change(user, instance, action, old_instance=None, request=None):
    """
    Log changes to a model instance
    
    Args:
        user: The user making the change
        instance: The new/modified model instance
        action: Type of action (CREATE, UPDATE, DELETE)
        old_instance: The previous state of the instance (for UPDATE)
        request: HTTP request object (optional)
    """
    try:
        model_name = instance.__class__.__name__
        object_id = instance.pk if hasattr(instance, 'pk') else None
        
        old_values = None
        new_values = None
        
        if action == 'UPDATE' and old_instance:
            old_values = {}
            new_values = {}
            
            # Compare fields
            for field in instance._meta.get_fields():
                if field.name.startswith('_'):
                    continue
                try:
                    old_val = getattr(old_instance, field.name, None)
                    new_val = getattr(instance, field.name, None)
                    
                    # Skip if values are the same
                    if old_val == new_val:
                        continue
                    
                    # Convert to JSON-serializable format
                    old_values[field.name] = str(old_val)
                    new_values[field.name] = str(new_val)
                except:
                    pass
        
        elif action == 'CREATE':
            new_values = {}
            for field in instance._meta.fields:
                try:
                    val = getattr(instance, field.name, None)
                    if val is not None:
                        new_values[field.name] = str(val)
                except:
                    pass
        
        log_admin_action(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            description=f"{action}: {model_name}#{object_id}",
            old_values=old_values,
            new_values=new_values,
            request=request
        )
    
    except Exception as e:
        logger.error(f"Failed to log model change: {str(e)}")


def get_recent_logs(limit=50, action=None, user=None, model_name=None):
    """
    Retrieve recent admin logs with optional filtering
    
    Args:
        limit: Number of logs to retrieve
        action: Filter by action type
        user: Filter by user
        model_name: Filter by model name
    
    Returns:
        QuerySet of AdminLog objects
    """
    logs = AdminLog.objects.all()
    
    if action:
        logs = logs.filter(action=action)
    
    if user:
        logs = logs.filter(admin_user=user)
    
    if model_name:
        logs = logs.filter(model_name=model_name)
    
    return logs[:limit]


def get_logs_by_date_range(start_date, end_date, action=None, user=None):
    """
    Get logs within a date range
    """
    logs = AdminLog.objects.filter(
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    )
    
    if action:
        logs = logs.filter(action=action)
    
    if user:
        logs = logs.filter(admin_user=user)
    
    return logs


def export_logs_to_json(queryset):
    """
    Export logs to JSON format
    """
    data = []
    for log in queryset:
        data.append({
            'id': log.id,
            'admin_user': str(log.admin_user),
            'action': log.get_action_display(),
            'model_name': log.model_name,
            'object_id': log.object_id,
            'description': log.description,
            'status': log.status,
            'timestamp': log.timestamp.isoformat(),
            'ip_address': log.ip_address,
            'duration_ms': log.duration_ms,
        })
    
    return json.dumps(data, indent=2, cls=DjangoJSONEncoder)
