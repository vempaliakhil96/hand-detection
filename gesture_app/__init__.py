import os

from click import get_app_dir

GESTURE_APP_HOME = get_app_dir("gesture_app")

if not os.path.exists(GESTURE_APP_HOME):
    os.makedirs(GESTURE_APP_HOME)