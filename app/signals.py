from django.dispatch import Signal

analysis_end = Signal(providing_args=["path"])
