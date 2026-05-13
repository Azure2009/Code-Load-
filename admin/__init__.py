from flask import Blueprint


admin_bp = Blueprint("admin",__name__, static_folder='static')

from admin import routes
