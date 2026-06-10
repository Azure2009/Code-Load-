from flask_login import LoginManager
from models import User, Administrator

login_manager = LoginManager()

login_manager.blueprint_login_views = {

    'routes': 'routes.administrator'

}

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id: str):

    if user_id.startswith('user-'):

        return User.query.get(int(user_id.split('-')[1]))  

    if user_id.startswith('admin-'):

        return Administrator.query.get(int(user_id.split('-')[1]))
    
    return None