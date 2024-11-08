#!/usr/bin/env python3
import telebot
import requests
import time
from datetime import datetime

BOT_TOKEN = "XXXXXXXXXXX"
CHAT_IDS = ["XXXXXXXXXXX", "XXXXXXXXXXX"]  # Chat IDs list

bot = telebot.TeleBot(BOT_TOKEN)

def send_message(message):
    for chat_id in CHAT_IDS:
        try:
            bot.send_message(chat_id, message, parse_mode="Markdown")
            print(f"Message sent to {chat_id}")
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")

def get_mega_sena_info():
    requests.packages.urllib3.disable_warnings()
    url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/"

    try:
        response = requests.get(url, verify=False)  # Disable SSL verification
        if response.status_code == 200:
            data = response.json()
            next_drawing_date = data.get("dataProximoConcurso")
            estimated_prize = data.get("valorEstimadoProximoConcurso", 0.0)
            estimated_prize_millions = float(estimated_prize) / 1000000  # Convert to millions

            # Convert the next_drawing_date to a datetime object with "dd/mm/yyyy" format
            next_drawing_date_datetime = datetime.strptime(next_drawing_date, "%d/%m/%Y")
            day_of_week = next_drawing_date_datetime.strftime("%A")

            return data, next_drawing_date, estimated_prize_millions, day_of_week
        else:
            print("Failed to retrieve data. Status code:", response.status_code)
            return None, None, None, None
    except Exception as e:
        print("An error occurred:", e)
        return None, None, None, None

if __name__ == "__main__":
    prev_next_drawing_date = None
    prev_estimated_prize = None

    while True:
        data, current_next_drawing_date, current_estimated_prize, current_day_of_week = get_mega_sena_info()

        if data and ((prev_next_drawing_date != current_next_drawing_date) or (prev_estimated_prize != current_estimated_prize)):
            # Extract the latest drawn numbers
            last_drawn_numbers = ", ".join(data.get("dezenasSorteadasOrdemSorteio", []))

            # Extract prize distribution details
            prize_distribution = ""
            for prize in data.get("listaRateioPremio", []):
                descricao = prize.get("descricaoFaixa", "")
                numero_de_ganhadores = prize.get("numeroDeGanhadores", 0)
                valor_premio = prize.get("valorPremio", 0.0)
                prize_distribution += (
                    f"\n{descricao}\n"
                    f"Ganhadores: {numero_de_ganhadores}\n"
                    f"Prêmio: R$ {valor_premio:,.2f}"
                    f"\n"
                )

            # Format the message
            message = (
                f"** UPDATE **\n"
                f"\nÚltimas Dezenas Sorteadas: {last_drawn_numbers}\n"
                f"\n🎉 Próximo Sorteio da Mega: **{current_next_drawing_date}** ({current_day_of_week})\n"
                f"💰 Prêmio Estimado: **R$ {current_estimated_prize:.2f} Milhões**\n"
                f"{prize_distribution}"
            )

            send_message(message)

            # Update previous values to track changes
            prev_next_drawing_date = current_next_drawing_date
            prev_estimated_prize = current_estimated_prize

        # Wait for 6 hours before checking again
        time.sleep(6 * 3600)