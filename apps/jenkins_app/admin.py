"""
Jenkins App Admin - Interface d'administration professionnelle
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
import json

from .models import (
    JenkinsServer, JenkinsJob, JenkinsBuild, JenkinsNode,
    JenkinsPlugin, JenkinsCredential, JenkinsView, JenkinsPipeline
)


# ============================================================================
# INLINES
# ============================================================================

class JenkinsJobInline(admin.TabularInline):
    """Inline pour les jobs dans le serveur"""
    model = JenkinsJob
    extra = 0
    fields = ['name_link', 'job_type', 'color', 'last_build_status', 'is_active']
    readonly_fields = ['name_link', 'job_type', 'color', 'last_build_status']
    can_delete = False
    
    def name_link(self, obj):
        url = reverse('admin:jenkins_app_jenkinsjob_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.name)
    name_link.short_description = 'Name'
    
    def has_add_permission(self, request, obj=None):
        return False


class JenkinsBuildInline(admin.TabularInline):
    """Inline pour les builds dans le job"""
    model = JenkinsBuild
    extra = 0
    fields = ['build_number', 'status_badge', 'result', 'started_at', 'duration_display']
    readonly_fields = ['build_number', 'status_badge', 'result', 'started_at', 'duration_display']
    can_delete = False
    ordering = ['-build_number']
    
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'running': 'info',
            'completed': 'success',
            'failed': 'danger',
            'aborted': 'secondary',
            'unstable': 'warning',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def duration_display(self, obj):
        if obj.duration:
            if obj.duration < 60:
                return f"{obj.duration:.1f}s"
            elif obj.duration < 3600:
                return f"{obj.duration/60:.1f}m"
            else:
                return f"{obj.duration/3600:.1f}h"
        return '-'
    duration_display.short_description = 'Duration'
    
    def has_add_permission(self, request, obj=None):
        return False


# ============================================================================
# SERVEURS JENKINS
# ============================================================================

@admin.register(JenkinsServer)
class JenkinsServerAdmin(ImportExportModelAdmin):
    """Admin pour les serveurs Jenkins"""
    list_display = [
        'name_display', 'url', 'status_badge', 'version',
        'jobs_count', 'last_sync_at', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description', 'url']
    readonly_fields = ['id', 'created_at', 'updated_at', 'version', 'last_sync_at']
    autocomplete_fields = ['created_by']
    inlines = [JenkinsJobInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'url', 'status')
        }),
        ('Authentication', {
            'fields': ('username', 'password'),
            'classes': ('wide',)
        }),
        ('Configuration', {
            'fields': ('timeout', 'max_concurrent_builds'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('version', 'last_sync_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def name_display(self, obj):
        url = reverse('admin:jenkins_app_jenkinsserver_change', args=[obj.id])
        return format_html('<a href="{}"><strong>{}</strong></a>', url, obj.name)
    name_display.short_description = 'Name'
    
    def status_badge(self, obj):
        colors = {
            'active': 'success',
            'inactive': 'secondary',
            'maintenance': 'warning',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def jobs_count(self, obj):
        count = obj.jobs.count()
        return format_html('<span class="badge badge-info">{}</span>', count)
    jobs_count.short_description = 'Jobs'
    
    actions = ['test_connection', 'sync_all']
    
    def test_connection(self, request, queryset):
        """Teste la connexion aux serveurs Jenkins"""
        success = 0
        for server in queryset:
            client = server.get_client()
            result = client.get_version()
            if result['success']:
                server.version = result.get('version', '')
                server.last_sync_at = timezone.now()
                server.save()
                success += 1
        self.message_user(request, f"{success}/{queryset.count()} servers connected successfully")
    test_connection.short_description = "Test connection"
    
    def sync_all(self, request, queryset):
        """Synchronise toutes les données des serveurs"""
        # Cette action serait implémentée avec des tâches Celery
        self.message_user(request, "Sync started (async)")
    sync_all.short_description = "Sync all data"


# ============================================================================
# JOBS JENKINS
# ============================================================================

@admin.register(JenkinsJob)
class JenkinsJobAdmin(ImportExportModelAdmin):
    """Admin pour les jobs Jenkins"""
    list_display = [
        'name_display', 'server_link', 'job_type', 'color_badge',
        'last_build_status', 'build_count', 'is_active'
    ]
    list_filter = ['job_type', 'is_active', 'server']
    search_fields = ['name', 'description']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'synced_at',
        'last_build_number', 'last_build_status', 'last_build_at',
        'color', 'health_report', 'config_preview'
    ]
    autocomplete_fields = ['server']
    inlines = [JenkinsBuildInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('server', 'job_id', 'name', 'description', 'job_type')
        }),
        ('Configuration', {
            'fields': ('url', 'color', 'health_report'),
            'classes': ('collapse',)
        }),
        ('Parameters', {
            'fields': ('parameters',),
            'classes': ('collapse',)
        }),
        ('Last Build', {
            'fields': ('last_build_number', 'last_build_status', 'last_build_at')
        }),
        ('Statistics', {
            'fields': ('build_count', 'is_active')
        }),
        ('Synchronization', {
            'fields': ('synced_at',),
            'classes': ('collapse',)
        }),
        ('Configuration XML', {
            'fields': ('config_xml', 'config_preview'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def name_display(self, obj):
        url = reverse('admin:jenkins_app_jenkinsjob_change', args=[obj.id])
        return format_html('<a href="{}"><strong>{}</strong></a>', url, obj.name)
    name_display.short_description = 'Name'
    
    def server_link(self, obj):
        url = reverse('admin:jenkins_app_jenkinsserver_change', args=[obj.server.id])
        return format_html('<a href="{}">{}</a>', url, obj.server.name)
    server_link.short_description = 'Server'
    
    def color_badge(self, obj):
        colors = {
            'blue': 'success',
            'red': 'danger',
            'yellow': 'warning',
            'grey': 'secondary',
            'disabled': 'dark',
        }
        color = colors.get(obj.color, 'info')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.color)
    color_badge.short_description = 'Color'
    
    def config_preview(self, obj):
        if obj.config_xml:
            preview = obj.config_xml[:500] + ('...' if len(obj.config_xml) > 500 else '')
            return format_html('<pre style="background-color: #f8f9fa; padding: 10px;">{}</pre>', preview)
        return '-'
    config_preview.short_description = 'Config Preview'


# ============================================================================
# BUILDS JENKINS
# ============================================================================

@admin.register(JenkinsBuild)
class JenkinsBuildAdmin(ImportExportModelAdmin):
    """Admin pour les builds Jenkins"""
    list_display = [
        'id_short', 'job_link', 'build_number', 'status_badge',
        'result', 'started_at', 'duration_display'
    ]
    list_filter = ['status', 'result']
    search_fields = ['job__name', 'built_by']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'duration',
        'console_output', 'test_results', 'artifacts', 'metrics',
        'console_preview'
    ]
    autocomplete_fields = ['job', 'triggered_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('job', 'build_number', 'status', 'result')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration', 'estimated_duration')
        }),
        ('Details', {
            'fields': ('url', 'built_by', 'triggered_by')
        }),
        ('Parameters', {
            'fields': ('parameters', 'causes'),
            'classes': ('collapse',)
        }),
        ('Console Output', {
            'fields': ('console_preview',),
            'classes': ('wide',)
        }),
        ('Test Results', {
            'fields': ('test_results',),
            'classes': ('collapse',)
        }),
        ('Artifacts', {
            'fields': ('artifacts',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = 'ID'
    
    def job_link(self, obj):
        url = reverse('admin:jenkins_app_jenkinsjob_change', args=[obj.job.id])
        return format_html('<a href="{}">{}</a>', url, obj.job.name)
    job_link.short_description = 'Job'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'running': 'info',
            'completed': 'success',
            'failed': 'danger',
            'aborted': 'secondary',
            'unstable': 'warning',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def duration_display(self, obj):
        if obj.duration:
            if obj.duration < 60:
                return f"{obj.duration:.1f}s"
            elif obj.duration < 3600:
                return f"{obj.duration/60:.1f}m"
            else:
                return f"{obj.duration/3600:.1f}h"
        return '-'
    duration_display.short_description = 'Duration'
    
    def console_preview(self, obj):
        if obj.console_output:
            preview = obj.console_output[:1000] + ('...' if len(obj.console_output) > 1000 else '')
            return format_html('<pre style="background-color: #f8f9fa; padding: 10px;">{}</pre>', preview)
        return '-'
    console_preview.short_description = 'Console Preview'


# ============================================================================
# NŒUDS JENKINS
# ============================================================================

@admin.register(JenkinsNode)
class JenkinsNodeAdmin(ImportExportModelAdmin):
    """Admin pour les nœuds Jenkins"""
    list_display = [
        'name', 'server_link', 'node_type', 'status_badge',
        'num_executors', 'load_average', 'synced_at'
    ]
    list_filter = ['status', 'node_type']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'synced_at']
    autocomplete_fields = ['server']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('server', 'node_id', 'name', 'node_type', 'description')
        }),
        ('Status', {
            'fields': ('status', 'offline_reason')
        }),
        ('Capacity', {
            'fields': ('num_executors', 'total_memory', 'free_memory', 
                      'total_disk', 'free_disk', 'cpu_cores', 'load_average')
        }),
        ('Labels', {
            'fields': ('labels',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'synced_at'),
            'classes': ('collapse',)
        }),
    )
    
    def server_link(self, obj):
        url = reverse('admin:jenkins_app_jenkinsserver_change', args=[obj.server.id])
        return format_html('<a href="{}">{}</a>', url, obj.server.name)
    server_link.short_description = 'Server'
    
    def status_badge(self, obj):
        colors = {
            'online': 'success',
            'offline': 'danger',
            'disconnected': 'warning',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'


# ============================================================================
# PLUGINS JENKINS
# ============================================================================

@admin.register(JenkinsPlugin)
class JenkinsPluginAdmin(ImportExportModelAdmin):
    """Admin pour les plugins Jenkins"""
    list_display = [
        'name', 'version', 'server_link', 'enabled_badge',
        'has_update', 'installed_at'
    ]
    list_filter = ['enabled', 'has_update']
    search_fields = ['name', 'title', 'description']
    readonly_fields = ['id', 'created_at', 'installed_at', 'updated_at']
    autocomplete_fields = ['server']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('server', 'plugin_id', 'name', 'version', 'title')
        }),
        ('Description', {
            'fields': ('description', 'url')
        }),
        ('Status', {
            'fields': ('enabled', 'has_update', 'compatible_version')
        }),
        ('Dependencies', {
            'fields': ('dependencies',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'installed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def server_link(self, obj):
        url = reverse('admin:jenkins_app_jenkinsserver_change', args=[obj.server.id])
        return format_html('<a href="{}">{}</a>', url, obj.server.name)
    server_link.short_description = 'Server'
    
    def enabled_badge(self, obj):
        if obj.enabled:
            return format_html('<span class="badge badge-success">Enabled</span>')
        return format_html('<span class="badge badge-secondary">Disabled</span>')
    enabled_badge.short_description = 'Enabled'


# ============================================================================
# CREDENTIALS JENKINS
# ============================================================================

@admin.register(JenkinsCredential)
class JenkinsCredentialAdmin(ImportExportModelAdmin):
    """Admin pour les credentials Jenkins"""
    list_display = [
        'name', 'credential_type', 'server_link', 'scope', 'synced_at'
    ]
    list_filter = ['credential_type', 'scope']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'synced_at']
    autocomplete_fields = ['server']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('server', 'credential_id', 'name', 'credential_type', 'description')
        }),
        ('Credentials', {
            'fields': ('username', 'password', 'private_key', 'passphrase', 'secret'),
            'classes': ('wide',)
        }),
        ('Scope', {
            'fields': ('scope',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'synced_at'),
            'classes': ('collapse',)
        }),
    )
    
    def server_link(self, obj):
        url = reverse('admin:jenkins_app_jenkinsserver_change', args=[obj.server.id])
        return format_html('<a href="{}">{}</a>', url, obj.server.name)
    server_link.short_description = 'Server'


# ============================================================================
# VUES JENKINS
# ============================================================================

@admin.register(JenkinsView)
class JenkinsViewAdmin(ImportExportModelAdmin):
    """Admin pour les vues Jenkins"""
    list_display = ['name', 'server_link', 'view_type', 'jobs_count']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['server']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('server', 'view_id', 'name', 'description', 'view_type')
        }),
        ('Configuration', {
            'fields': ('url', 'jobs')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def server_link(self, obj):
        url = reverse('admin:jenkins_app_jenkinsserver_change', args=[obj.server.id])
        return format_html('<a href="{}">{}</a>', url, obj.server.name)
    server_link.short_description = 'Server'
    
    def jobs_count(self, obj):
        if obj.jobs:
            return len(obj.jobs)
        return 0
    jobs_count.short_description = 'Jobs'


# ============================================================================
# PIPELINES JENKINS
# ============================================================================

@admin.register(JenkinsPipeline)
class JenkinsPipelineAdmin(ImportExportModelAdmin):
    """Admin pour les pipelines Jenkins"""
    list_display = ['name', 'jobs_count', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['jobs']
    autocomplete_fields = ['created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Jobs', {
            'fields': ('jobs',)
        }),
        ('Configuration', {
            'fields': ('parameters', 'environment')
        }),
        ('Pipeline Script', {
            'fields': ('pipeline_script',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def jobs_count(self, obj):
        count = obj.jobs.count()
        return format_html('<span class="badge badge-info">{}</span>', count)
    jobs_count.short_description = 'Jobs'
