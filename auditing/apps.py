from django.apps import AppConfig

class AuditingConfig(AppConfig):
    name = 'auditing'
    verbose_name = "Auditing"
    
    def ready(self):
        from auditing import signals