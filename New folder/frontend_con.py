from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    return render_template('login.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('exampleInputEmail1')
        password = request.form.get('exampleInputPassword1')
        # Do something with the username and password
        print(username)
        return "Login successful"
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
