import requests

class Price:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __add__(self, other):
        if self.currency != other.currency:
            self_price_chf = self.convert(self.amount, self.currency, "CHF") 
            other_price_chf = self.convert(other.amount, other.currency, "CHF")

            total_price_chf = self_price_chf + other_price_chf

            return Price(self.convert(total_price_chf, "CHF", self.currency), self.currency)

        return Price(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        if self.currency != other.currency:
            self_price_chf = self.convert(self.amount, self.currency, "CHF") 
            other_price_chf = self.convert(other.amount, other.currency, "CHF")

            total_price_chf = self_price_chf - other_price_chf

            return Price(self.convert(total_price_chf, "CHF", self.currency), self.currency)
        
        return Price(self.amount - other.amount, self.currency)

    def __repr__(self):
        return f"{self.amount:.2f} {self.currency}"

    def convert(self, price, from_currency, to_currency):
        if from_currency == to_currency:
            return price

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "apikey": "3GLHW7BI5J44TRBK"
        }

        response = requests.get(url, params=params)
        data = response.json()

        try:
            rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
            converted_price = price * rate
            return converted_price
        except KeyError:
            print("Error fetching exchange rate:", data)
            return None

a = Price(100,"USD")

b = Price(150, "UAH")

c = a + b

print(c)
