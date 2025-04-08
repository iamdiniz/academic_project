from flask import Flask

app = Flask(__name__)

@app.route('/')
def idenx():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0') # host para expor o servidor para fora do container