import time
import requests
from telegram import Bot
from datetime import datetime, timedelta

# === CONFIGURAÇÕES ===
API_KEY = "c95f42c34f934f91938f91e5cc8604a6"
INTERVAL = "1min"
TELEGRAM_TOKEN = "7239698274:AAFyg7HWLPvXceJYDope17DkfJpxtU4IU2Y"
TELEGRAM_ID = "6821521589"
bot = Bot(token=TELEGRAM_TOKEN)
preco_anterior = None

# === LER ATIVO DO ARQUIVO ===
def obter_ativo():
    try:
        with open("ativo.txt", "r") as f:
            return f.read().strip().upper()
    except:
        return "EUR/USD"

# === LER STATUS ON/OFF ===
def bot_ativo():
    try:
        with open("status.txt", "r") as f:
            return f.read().strip().upper() == "ON"
    except:
        return True

# === OBTER HORÁRIO DA EXNOVA (usando UTC padrão da API) ===
def obter_horario_exnova():
    try:
        response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC")
        if response.status_code == 200:
            data = response.json()
            datetime_utc = datetime.fromisoformat(data["utc_datetime"].replace("Z", "+00:00"))
            return datetime_utc
    except Exception as e:
        print("Erro ao sincronizar horário:", e)
    return datetime.utcnow()

# === OBTER DADOS DO TWELVEDATA ===
def obter_dados(symbol):
    try:
        preco_url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={INTERVAL}&apikey={API_KEY}&outputsize=2"
        preco_data = requests.get(preco_url).json()
        if "values" not in preco_data:
            raise Exception(preco_data.get("message", "Erro desconhecido"))
        preco = float(preco_data["values"][0]["close"])

        rsi_url = f"https://api.twelvedata.com/rsi?symbol={symbol}&interval={INTERVAL}&apikey={API_KEY}&time_period=14"
        rsi_data = requests.get(rsi_url).json()
        rsi = float(rsi_data["values"][0]["rsi"]) if "values" in rsi_data else None

        ma5_url = f"https://api.twelvedata.com/ma?symbol={symbol}&interval={INTERVAL}&apikey={API_KEY}&time_period=5&type=sma"
        ma20_url = f"https://api.twelvedata.com/ma?symbol={symbol}&interval={INTERVAL}&apikey={API_KEY}&time_period=20&type=sma"
        ma5_data = requests.get(ma5_url).json()
        ma20_data = requests.get(ma20_url).json()
        ma5 = float(ma5_data["values"][0]["ma"]) if "values" in ma5_data else None
        ma20 = float(ma20_data["values"][0]["ma"]) if "values" in ma20_data else None

        return preco, rsi, ma5, ma20
    except Exception as e:
        print("Erro ao obter dados:", e)
        return None, None, None, None

# === ENVIAR MENSAGEM PARA TELEGRAM ===
def enviar_sinal(mensagem):
    try:
        bot.send_message(chat_id=TELEGRAM_ID, text=mensagem)
    except Exception as e:
        print("Erro ao enviar:", e)

# === MONITORAR ATIVO ===
def monitorar():
    global preco_anterior
    while True:
        if not bot_ativo():
            print("⛔ Bot desligado")
            time.sleep(10)
            continue

        ativo = obter_ativo()
        preco, rsi, ma5, ma20 = obter_dados(ativo)
        agora_exnova = obter_horario_exnova()
        entrada = agora_exnova + timedelta(minutes=1)
        horario_entrada = entrada.strftime("%H:%M")

        if preco and rsi and ma5 and ma20:
            mensagem = f"📊 {ativo} - ${preco:.5f}\n"
            if preco_anterior:
                variacao = ((preco - preco_anterior) / preco_anterior) * 100
                mensagem += f"🔄 Variação: {variacao:.3f}%\n"
            else:
                variacao = 0
                mensagem += "🟡 Iniciando monitoramento...\n"

            preco_anterior = preco
            sinal = "⚪ SEM AÇÃO"

            if rsi < 45 or (ma5 > ma20 and variacao > 0.01):
                sinal = f"🟢 COMPRA às {horario_entrada}"
            elif rsi > 55 or (ma5 < ma20 and variacao < -0.01):
                sinal = f"🔴 VENDA às {horario_entrada}"

            mensagem += f"📈 RSI: {rsi:.2f}\n"
            mensagem += f"📉 MA5: {ma5:.5f} | MA20: {ma20:.5f}\n"
            mensagem += f"📍 SINAL: {sinal}"

            enviar_sinal(mensagem)

        time.sleep(30)

# === FUNÇÃO DE INÍCIO PADRÃO ===
def start():
    print("✅ Bot iniciado com sucesso.")
    monitorar()
    
