from flask import Flask, render_template, request
import bot

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ativo = request.form.get("ativo", "EUR/USD").strip().upper()
        status = request.form.get("status", "ON").strip().upper()

        with open("ativo.txt", "w") as f:
            f.write(ativo)
        with open("status.txt", "w") as f:
            f.write(status)

    try:
        with open("ativo.txt", "r") as f:
            ativo = f.read().strip().upper()
    except:
        ativo = "EUR/USD"

    try:
        with open("status.txt", "r") as f:
            status = f.read().strip().upper()
    except:
        status = "ON"

    return render_template("index.html", ativo=ativo, status=status)

if __name__ == "__main__":
    bot.iniciar_thread()
    app.run(host="0.0.0.0", port=10000)
    
