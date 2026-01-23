from flask import Flask, render_template
import os
import method


app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
