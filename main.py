import requests
from flask import Flask, render_template, request

app = Flask(__name__)

response = requests.get(
    "http://api.nbp.pl/api/exchangerates/tables/C?format=json")
data = response.json()

CURRENCY_ICONS = {
    "USD": "🇺🇸",
    "AUD": "🇦🇺",
    "CAD": "🇨🇦",
    "EUR": "🇪🇺",
    "HUF": "🇭🇺",
    "CHF": "🇨🇭",
    "GBP": "🇬🇧",
    "JPY": "🇯🇵",
    "CZK": "🇨🇿",
    "DKK": "🇩🇰",
    "NOK": "🇳🇴",
    "SEK": "🇸🇪",
    "XDR": "🌐",
}


def get_rates(data):
    rates = []
    for item in data:
        for rate in item['rates']:
            rates.append([
                rate['currency'],
                rate['code'],
                rate['bid'],
                rate['ask'],
                get_currency_icon(rate['code'])
            ])
    return rates


def get_currency_icon(currency_code):
    # Domyślna flaga to biała flaga
    return CURRENCY_ICONS.get(currency_code, "🏳️")


def create_csv(data):
    import csv
    with open('exchange_rates.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['currency', 'code', 'bid', 'ask'])
        for rate in get_rates(data):
            # zapisywanie pliku csv bez flagi
            writer.writerow(rate[:4])


create_csv(data)


@app.route("/calculator/", methods=["GET", "POST"])
def calculator():
    if request.method == 'GET':
        return render_template("base.html", rates=get_rates(data))

    # Obsługa metody POST
    currency_code = request.form.get("currency")
    amount_str = request.form.get("amount")
    result_cost = None
    amount = 0
    icon = CURRENCY_ICONS.get(currency_code, "🏳️")

    try:
        amount = float(amount_str)
        all_rates = get_rates(data)
        for rate in all_rates:
            # rate[1] to kod waluty (np. 'USD')
            # rate[3] to kurs sprzedaży ('ask')
            if rate[1] == currency_code:
                result_cost = amount * rate[3]
                break
    except (ValueError, TypeError):
        # Obsługa przypadków, gdy 'amount' nie jest poprawną liczbą lub jest None
        amount = amount_str
        result_cost = None

    return render_template(
        "result.html", rates=get_rates(data), currency=currency_code,
        amount=amount, result_cost=result_cost, icon=icon
    )


if __name__ == '__main__':
    app.run(debug=True)
