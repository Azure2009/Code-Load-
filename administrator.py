from app import *

@app.route('/administrator', methods=['POST'])
def administrator():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = Administrator.query.filter_by(admin_username = username).first()

    

    return render_template('Administrator/administrator_login.html')