from flask import Flask

PORT = 5000
app = Flask(__name__)

@app.route('/')
@app.route('/hello')

def HelloWorld():
    return "Hello World"

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port=PORT)
