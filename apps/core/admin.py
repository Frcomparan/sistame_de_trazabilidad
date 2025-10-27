from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('id', 'last_login', 'date_joined')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['user']
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'role')
        }),
        ('Contacto', {
            'fields': ('phone',)
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'entity', 'entity_id', 'ip_address')
    list_filter = ('action', 'entity', 'timestamp')
    search_fields = ('user__username', 'entity', 'entity_id', 'ip_address')
    readonly_fields = ('id', 'user', 'action', 'entity', 'entity_id', 'timestamp', 
                      'ip_address', 'user_agent', 'diff')
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        # Los audit logs no se crean manualmente
        return False
    
    def has_change_permission(self, request, obj=None):
        # Los audit logs no se modifican
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar logs
        return request.user.is_superuser
