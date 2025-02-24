from django.apps import AppConfig


class ModeluserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modelUser'

    # def ready(self):
    #     import modelUser.signals
