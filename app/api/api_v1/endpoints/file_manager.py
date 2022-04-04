from flask import Blueprint
from flask_autoindex import AutoIndexBlueprint

from app import APP_ROOT

file_manager = Blueprint("file_manager", __name__)

AutoIndexBlueprint(file_manager, browse_root=APP_ROOT)
