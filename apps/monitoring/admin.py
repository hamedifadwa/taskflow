"""
Monitoring App Admin - Interface d'administration professionnelle
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
import json

from .models import (
    SystemMetric, DeviceMetric, InterfaceMetric, ApplicationMetric,
    Alert, AlertThreshold, NotificationChannel, NotificationLog,
    Dashboard, MetricCollection
)


# ============================================================================
# INLINES
# ============================================================================

class NotificationLogInline(admin.TabularInline):
    """Inline pour les logs de notification dans l'alerte"""
    model = NotificationLog
    extra = 0
    fields = ['channel', 'status_badge', 'sent_at']
    readonly_fields = ['channel', 'status_badge', 'sent_at']
    can_delete = False
    ordering = ['-sent_at']
    
    def status_badge(self, obj):
        colors = {
            'sent': 'success',
            'failed': 'danger',
            'pending': 'warning',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request, obj=None):
        return False


# ============================================================================
# MÉTRIQUES SYSTÈME
# ============================================================================

@admin.register(SystemMetric)
class SystemMetricAdmin(ImportExportModelAdmin):
    """Admin pour les métriques système"""
    list_display = [
        'id_short', 'collected_at', 'cpu_usage_bar', 'memory_usage_bar',
        'disk_usage_bar', 'load_avg_display'
    ]
    list_filter = ['collected_at']
    readonly_fields = ['id', 'created_at', 'collected_at', 'usage_bars']
    ordering = ['-collected_at']
    
    fieldsets = (
        ('Timing', {
            'fields': ('collected_at', 'created_at')
        }),
        ('CPU', {
            'fields': ('cpu_usage', 'cpu_count', 'load_avg_1min', 'load_avg_5min', 'load_avg_15min')
        }),
        ('Memory', {
            'fields': ('memory_total', 'memory_available', 'memory_used', 'memory_percent')
        }),
        ('Disk', {
            'fields': ('disk_total', 'disk_used', 'disk_free', 'disk_percent')
        }),
        ('Network', {
            'fields': ('network_bytes_sent', 'network_bytes_recv', 'network_packets_sent', 'network_packets_recv')
        }),
        ('Visualization', {
            'fields': ('usage_bars',),
            'classes': ('wide',)
        }),
    )
    
    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = 'ID'
    
    def cpu_usage_bar(self, obj):
        color = 'danger' if obj.cpu_usage > 80 else 'warning' if obj.cpu_usage > 60 else 'success'
        return format_html(
            '<div class="progress" style="height: 20px; width: 100px;">'
            '<div class="progress-bar bg-{}" role="progressbar" style="width: {}%;">{}%</div>'
            '</div>',
            color, obj.cpu_usage, obj.cpu_usage
        )
    cpu_usage_bar.short_description = 'CPU'
    
    def memory_usage_bar(self, obj):
        color = 'danger' if obj.memory_percent > 80 else 'warning' if obj.memory_percent > 60 else 'success'
        return format_html(
            '<div class="progress" style="height: 20px; width: 100px;">'
            '<div class="progress-bar bg-{}" role="progressbar" style="width: {}%;">{}%</div>'
            '</div>',
            color, obj.memory_percent, obj.memory_percent
        )
    memory_usage_bar.short_description = 'Memory'
    
    def disk_usage_bar(self, obj):
        color = 'danger' if obj.disk_percent > 80 else 'warning' if obj.disk_percent > 60 else 'success'
        return format_html(
            '<div class="progress" style="height: 20px; width: 100px;">'
            '<div class="progress-bar bg-{}" role="progressbar" style="width: {}%;">{}%</div>'
            '</div>',
            color, obj.disk_percent, obj.disk_percent
        )
    disk_usage_bar.short_description = 'Disk'
    
    def load_avg_display(self, obj):
        if obj.load_avg_1min:
            return f"{obj.load_avg_1min:.2f}, {obj.load_avg_5min:.2f}, {obj.load_avg_15min:.2f}"
        return '-'
    load_avg_display.short_description = 'Load Average'
    
    def usage_bars(self, obj):
        html = '<div style="margin-bottom: 10px;">'
        
        # CPU
        cpu_color = 'danger' if obj.cpu_usage > 80 else 'warning' if obj.cpu_usage > 60 else 'success'
        html += f'<div><strong>CPU:</strong> {obj.cpu_usage}%</div>'
        html += f'<div class="progress" style="height: 20px; margin-bottom: 10px;">'
        html += f'<div class="progress-bar bg-{cpu_color}" role="progressbar" style="width: {obj.cpu_usage}%;"></div>'
        html += f'</div>'
        
        # Memory
        mem_color = 'danger' if obj.memory_percent > 80 else 'warning' if obj.memory_percent > 60 else 'success'
        html += f'<div><strong>Memory:</strong> {obj.memory_percent}%</div>'
        html += f'<div class="progress" style="height: 20px; margin-bottom: 10px;">'
        html += f'<div class="progress-bar bg-{mem_color}" role="progressbar" style="width: {obj.memory_percent}%;"></div>'
        html += f'</div>'
        
        # Disk
        disk_color = 'danger' if obj.disk_percent > 80 else 'warning' if obj.disk_percent > 60 else 'success'
        html += f'<div><strong>Disk:</strong> {obj.disk_percent}%</div>'
        html += f'<div class="progress" style="height: 20px; margin-bottom: 10px;">'
        html += f'<div class="progress-bar bg-{disk_color}" role="progressbar" style="width: {obj.disk_percent}%;"></div>'
        html += f'</div>'
        
        html += '</div>'
        return format_html(html)
    usage_bars.short_description = 'Resource Usage'


# ============================================================================
# MÉTRIQUES DES ÉQUIPEMENTS
# ============================================================================

@admin.register(DeviceMetric)
class DeviceMetricAdmin(ImportExportModelAdmin):
    """Admin pour les métriques des équipements"""
    list_display = [
        'device_link', 'collected_at', 'cpu_usage_bar', 'memory_usage_bar',
        'temperature_display', 'is_reachable_badge', 'response_time_display'
    ]
    list_filter = ['is_reachable', 'collected_at']
    search_fields = ['device__name', 'device__hostname']
    readonly_fields = ['id', 'created_at', 'collected_at']
    raw_id_fields = ['device']
    ordering = ['-collected_at']
    
    fieldsets = (
        ('Device', {
            'fields': ('device', 'collected_at')
        }),
        ('Health', {
            'fields': ('cpu_usage', 'memory_usage', 'temperature', 'uptime')
        }),
        ('Connectivity', {
            'fields': ('is_reachable', 'response_time')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def device_link(self, obj):
        url = reverse('admin:inventory_device_change', args=[obj.device.id])
        return format_html('<a href="{}">{}</a>', url, obj.device.name)
    device_link.short_description = 'Device'
    
    def cpu_usage_bar(self, obj):
        if obj.cpu_usage is not None:
            color = 'danger' if obj.cpu_usage > 80 else 'warning' if obj.cpu_usage > 60 else 'success'
            return format_html(
                '<div class="progress" style="height: 20px; width: 100px;">'
                '<div class="progress-bar bg-{}" role="progressbar" style="width: {}%;">{}%</div>'
                '</div>',
                color, obj.cpu_usage, obj.cpu_usage
            )
        return '-'
    cpu_usage_bar.short_description = 'CPU'
    
    def memory_usage_bar(self, obj):
        if obj.memory_usage is not None:
            color = 'danger' if obj.memory_usage > 80 else 'warning' if obj.memory_usage > 60 else 'success'
            return format_html(
                '<div class="progress" style="height: 20px; width: 100px;">'
                '<div class="progress-bar bg-{}" role="progressbar" style="width: {}%;">{}%</div>'
                '</div>',
                color, obj.memory_usage, obj.memory_usage
            )
        return '-'
    memory_usage_bar.short_description = 'Memory'
    
    def temperature_display(self, obj):
        if obj.temperature is not None:
            color = 'danger' if obj.temperature > 70 else 'warning' if obj.temperature > 50 else 'success'
            return format_html('<span style="color: {};">{}°C</span>', color, obj.temperature)
        return '-'
    temperature_display.short_description = 'Temp'
    
    def is_reachable_badge(self, obj):
        if obj.is_reachable:
            return format_html('<span class="badge badge-success">✓ Reachable</span>')
        return format_html('<span class="badge badge-danger">✗ Unreachable</span>')
    is_reachable_badge.short_description = 'Reachable'
    
    def response_time_display(self, obj):
        if obj.response_time:
            color = 'danger' if obj.response_time > 100 else 'warning' if obj.response_time > 50 else 'success'
            return format_html('<span style="color: {};">{}ms</span>', color, obj.response_time)
        return '-'
    response_time_display.short_description = 'Response'


# ============================================================================
# MÉTRIQUES DES INTERFACES
# ============================================================================

@admin.register(InterfaceMetric)
class InterfaceMetricAdmin(ImportExportModelAdmin):
    """Admin pour les métriques des interfaces"""
    list_display = [
        'interface_link', 'collected_at', 'status_badge',
        'rx_rate_display', 'tx_rate_display', 'errors_display'
    ]
    list_filter = ['status', 'collected_at']
    search_fields = ['interface__name', 'interface__device__name']
    readonly_fields = ['id', 'created_at', 'collected_at']
    raw_id_fields = ['interface']
    ordering = ['-collected_at']
    
    fieldsets = (
        ('Interface', {
            'fields': ('interface', 'collected_at', 'status')
        }),
        ('Statistics', {
            'fields': ('rx_bytes', 'tx_bytes', 'rx_packets', 'tx_packets')
        }),
        ('Errors', {
            'fields': ('rx_errors', 'tx_errors', 'rx_drops', 'tx_drops')
        }),
        ('Rates', {
            'fields': ('rx_rate_bps', 'tx_rate_bps')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def interface_link(self, obj):
        url = reverse('admin:inventory_interface_change', args=[obj.interface.id])
        return format_html('<a href="{}">{}</a>', url, obj.interface.name)
    interface_link.short_description = 'Interface'
    
    def status_badge(self, obj):
        colors = {
            'up': 'success',
            'down': 'danger',
            'admin_down': 'secondary',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.status)
    status_badge.short_description = 'Status'
    
    def rx_rate_display(self, obj):
        if obj.rx_rate_bps:
            if obj.rx_rate_bps > 1e9:
                return f"{obj.rx_rate_bps/1e9:.2f} Gbps"
            elif obj.rx_rate_bps > 1e6:
                return f"{obj.rx_rate_bps/1e6:.2f} Mbps"
            else:
                return f"{obj.rx_rate_bps/1e3:.2f} Kbps"
        return '-'
    rx_rate_display.short_description = 'RX Rate'
    
    def tx_rate_display(self, obj):
        if obj.tx_rate_bps:
            if obj.tx_rate_bps > 1e9:
                return f"{obj.tx_rate_bps/1e9:.2f} Gbps"
            elif obj.tx_rate_bps > 1e6:
                return f"{obj.tx_rate_bps/1e6:.2f} Mbps"
            else:
                return f"{obj.tx_rate_bps/1e3:.2f} Kbps"
        return '-'
    tx_rate_display.short_description = 'TX Rate'
    
    def errors_display(self, obj):
        total_errors = obj.rx_errors + obj.tx_errors
        if total_errors > 0:
            color = 'danger' if total_errors > 100 else 'warning'
            return format_html('<span style="color: {};">{}</span>', color, total_errors)
        return '-'
    errors_display.short_description = 'Errors'


# ============================================================================
# MÉTRIQUES APPLICATIVES
# ============================================================================

@admin.register(ApplicationMetric)
class ApplicationMetricAdmin(ImportExportModelAdmin):
    """Admin pour les métriques applicatives"""
    list_display = [
        'metric_type', 'metric_name', 'metric_value', 'tags_preview', 'collected_at'
    ]
    list_filter = ['metric_type', 'collected_at']
    search_fields = ['metric_name', 'tags']
    readonly_fields = ['id', 'created_at', 'collected_at']
    ordering = ['-collected_at']
    
    fieldsets = (
        ('Metric', {
            'fields': ('metric_type', 'metric_name', 'metric_value', 'collected_at')
        }),
        ('Tags', {
            'fields': ('tags',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tags_preview(self, obj):
        if obj.tags:
            return ', '.join([f"{k}:{v}" for k, v in list(obj.tags.items())[:3]])
        return '-'
    tags_preview.short_description = 'Tags'


# ============================================================================
# ALERTES
# ============================================================================

@admin.register(Alert)
class AlertAdmin(ImportExportModelAdmin):
    """Admin pour les alertes"""
    list_display = [
        'name', 'severity_badge', 'status_badge', 'source', 'device_link',
        'occurrence_count', 'last_occurrence'
    ]
    list_filter = ['severity', 'status', 'source', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'first_occurrence', 'last_occurrence',
        'occurrence_count', 'notifications_sent'
    ]
    raw_id_fields = ['device', 'interface', 'acknowledged_by']
    inlines = [NotificationLogInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'severity', 'status', 'source')
        }),
        ('Target', {
            'fields': ('device', 'interface')
        }),
        ('Threshold', {
            'fields': ('metric_name', 'metric_value', 'threshold_value', 'operator')
        }),
        ('Timing', {
            'fields': ('first_occurrence', 'last_occurrence', 'occurrence_count')
        }),
        ('Acknowledgement', {
            'fields': ('acknowledged_by', 'acknowledged_at', 'resolved_at')
        }),
        ('Notifications', {
            'fields': ('notifications_sent', 'last_notification_at')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def severity_badge(self, obj):
        colors = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'success',
            'info': 'primary',
        }
        color = colors.get(obj.severity, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_severity_display())
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        colors = {
            'active': 'danger',
            'acknowledged': 'warning',
            'resolved': 'success',
            'expired': 'secondary',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def device_link(self, obj):
        if obj.device:
            url = reverse('admin:inventory_device_change', args=[obj.device.id])
            return format_html('<a href="{}">{}</a>', url, obj.device.name)
        return '-'
    device_link.short_description = 'Device'
    
    actions = ['acknowledge_alerts', 'resolve_alerts']
    
    def acknowledge_alerts(self, request, queryset):
        updated = queryset.update(status='acknowledged', acknowledged_at=timezone.now())
        self.message_user(request, f'{updated} alerts acknowledged')
    acknowledge_alerts.short_description = "Acknowledge selected alerts"
    
    def resolve_alerts(self, request, queryset):
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} alerts resolved')
    resolve_alerts.short_description = "Resolve selected alerts"


# ============================================================================
# SEUILS D'ALERTE
# ============================================================================

@admin.register(AlertThreshold)
class AlertThresholdAdmin(ImportExportModelAdmin):
    """Admin pour les seuils d'alerte"""
    list_display = [
        'name', 'threshold_type', 'warning_display', 'critical_display',
        'is_enabled_badge', 'devices_count'
    ]
    list_filter = ['threshold_type', 'is_enabled']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['devices']
    raw_id_fields = ['created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'threshold_type', 'description', 'is_enabled')
        }),
        ('Thresholds', {
            'fields': ('warning_threshold', 'critical_threshold', 'operator', 'duration', 'silence_period')
        }),
        ('Target Devices', {
            'fields': ('devices',),
            'description': 'Leave empty to apply to all devices'
        }),
        ('Metadata', {
            'fields': ('created_by', 'id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def warning_display(self, obj):
        if obj.warning_threshold is not None:
            return f"{obj.operator} {obj.warning_threshold}"
        return '-'
    warning_display.short_description = 'Warning'
    
    def critical_display(self, obj):
        if obj.critical_threshold is not None:
            return f"{obj.operator} {obj.critical_threshold}"
        return '-'
    critical_display.short_description = 'Critical'
    
    def is_enabled_badge(self, obj):
        if obj.is_enabled:
            return format_html('<span class="badge badge-success">Enabled</span>')
        return format_html('<span class="badge badge-secondary">Disabled</span>')
    is_enabled_badge.short_description = 'Status'
    
    def devices_count(self, obj):
        count = obj.devices.count()
        if count == 0:
            return 'All Devices'
        return count
    devices_count.short_description = 'Devices'


# ============================================================================
# CANAUX DE NOTIFICATION
# ============================================================================

@admin.register(NotificationChannel)
class NotificationChannelAdmin(ImportExportModelAdmin):
    """Admin pour les canaux de notification"""
    list_display = ['name', 'channel_type', 'is_enabled_badge', 'config_preview']
    list_filter = ['channel_type', 'is_enabled']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'channel_type', 'description', 'is_enabled')
        }),
        ('Configuration', {
            'fields': ('config',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_enabled_badge(self, obj):
        if obj.is_enabled:
            return format_html('<span class="badge badge-success">Enabled</span>')
        return format_html('<span class="badge badge-secondary">Disabled</span>')
    is_enabled_badge.short_description = 'Status'
    
    def config_preview(self, obj):
        if obj.config:
            return ', '.join([f"{k}:{v}" for k, v in list(obj.config.items())[:3]])
        return '-'
    config_preview.short_description = 'Config'


# ============================================================================
# LOGS DE NOTIFICATION
# ============================================================================

@admin.register(NotificationLog)
class NotificationLogAdmin(ImportExportModelAdmin):
    """Admin pour les logs de notification"""
    list_display = [
        'id_short', 'alert_link', 'channel_link', 'status_badge', 'sent_at'
    ]
    list_filter = ['status', 'sent_at']
    search_fields = ['alert__name', 'channel__name']
    readonly_fields = ['id', 'created_at', 'sent_at']
    
    fieldsets = (
        ('Notification', {
            'fields': ('alert', 'channel', 'status')
        }),
        ('Details', {
            'fields': ('error_message',),
            'classes': ('wide',)
        }),
        ('Timing', {
            'fields': ('sent_at',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = 'ID'
    
    def alert_link(self, obj):
        url = reverse('admin:monitoring_alert_change', args=[obj.alert.id])
        return format_html('<a href="{}">{}</a>', url, obj.alert.name)
    alert_link.short_description = 'Alert'
    
    def channel_link(self, obj):
        url = reverse('admin:monitoring_notificationchannel_change', args=[obj.channel.id])
        return format_html('<a href="{}">{}</a>', url, obj.channel.name)
    channel_link.short_description = 'Channel'
    
    def status_badge(self, obj):
        colors = {
            'sent': 'success',
            'failed': 'danger',
            'pending': 'warning',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'


# ============================================================================
# TABLEAUX DE BORD
# ============================================================================

@admin.register(Dashboard)
class DashboardAdmin(ImportExportModelAdmin):
    """Admin pour les tableaux de bord"""
    list_display = ['name', 'owner_link', 'is_public_badge', 'widgets_count', 'created_at']
    list_filter = ['is_public']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['owner']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'owner', 'is_public')
        }),
        ('Configuration', {
            'fields': ('config',),
            'classes': ('collapse',)
        }),
        ('Widgets', {
            'fields': ('widgets',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def owner_link(self, obj):
        if obj.owner:
            url = reverse('admin:users_user_change', args=[obj.owner.id])
            return format_html('<a href="{}">{}</a>', url, obj.owner.email)
        return '-'
    owner_link.short_description = 'Owner'
    
    def is_public_badge(self, obj):
        if obj.is_public:
            return format_html('<span class="badge badge-success">Public</span>')
        return format_html('<span class="badge badge-secondary">Private</span>')
    is_public_badge.short_description = 'Visibility'
    
    def widgets_count(self, obj):
        return len(obj.widgets) if obj.widgets else 0
    widgets_count.short_description = 'Widgets'


# ============================================================================
# COLLECTIONS DE MÉTRIQUES
# ============================================================================

@admin.register(MetricCollection)
class MetricCollectionAdmin(ImportExportModelAdmin):
    """Admin pour les collections de métriques"""
    list_display = ['name', 'metric_type', 'aggregation', 'retention_days', 'metrics_count']
    list_filter = ['metric_type', 'aggregation']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'metric_type', 'aggregation')
        }),
        ('Configuration', {
            'fields': ('metric_names', 'retention_days')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def metrics_count(self, obj):
        return len(obj.metric_names) if obj.metric_names else 0
    metrics_count.short_description = 'Metrics'
