from django.apps import AppConfig

class StoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stores'
    
    # 시그널을 앱이 시작될 때 불러오도록 설정
    def ready(self):
        import stores.signals  
