from django.conf import settings

# Directory in which to save image files for ActivityMember verification.
ACTIVITY_FILE_DIR = getattr(settings, 'ACTIVITY_FILE_DIR', 'activities')