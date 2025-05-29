from flask import Flask, render_template, request, redirect
import threading
import os
from bot import start

app = Flask(__name__)
thread = None

def iniciar_bot():
    global thread
    if thread is None or not thread.is_alive():
        thread = threading.Thread(target=start)
        thread.daemon = True
        thread.start()

@app.route("/", methods=["GET", "POST"])
def painel():
    if request.method == "POST":
        if "ativo" in request.form:
            with open("ativo.txt", "w") as f:
                f.write(request.form["ativo"])
        if "status" in request.form:
            with open("status.txt", "w") as f:
                f.write(request.form["status"])
            if request.form["status"].upper() == "ON":
                iniciar_bot()
        return redirect("/")
    
    try:
        with open("ativo.txt") as f:
            ativo = f.read().strip()
    except:
        ativo = "EUR/USD"

    try:
        with open("status.txt") as f:
            status = f.read().strip()
    except:
        status = "OFF"

    return render_template("painel.html", ativo=ativo, status=status)

if __name__ == "__main__":
    iniciar_bot()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
