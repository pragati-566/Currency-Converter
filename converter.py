import requests


class RealTimeCurrencyConverter:
    """
    Fetches live exchange rates from exchangerate-api.com and converts
    amounts between currencies.
    """

    BASE_URL = "https://api.exchangerate-api.com/v4/latest/{}"

    def __init__(self, base: str = "USD"):
        self.base = base.upper()
        self.rates: dict = {}
        self._fetch_rates()

    def _fetch_rates(self) -> None:
        """Download latest exchange rates for *self.base* currency."""
        try:
            url = self.BASE_URL.format(self.base)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.rates = data.get("rates", {})
        except requests.exceptions.RequestException as exc:
            raise ConnectionError(
                f"Could not fetch exchange rates: {exc}"
            ) from exc

    def get_currencies(self) -> list[str]:
        """Return a sorted list of all available currency codes."""
        return sorted(self.rates.keys())

    def convert(self, from_currency: str, to_currency: str, amount: float) -> float:
        """
        Convert *amount* from *from_currency* to *to_currency*.

        Parameters
        ----------
        from_currency : str
            ISO 4217 currency code of the source currency (e.g. ``"USD"``).
        to_currency : str
            ISO 4217 currency code of the target currency (e.g. ``"INR"``).
        amount : float
            Positive numeric value to convert.

        Returns
        -------
        float
            Converted amount rounded to 4 decimal places.

        Raises
        ------
        ValueError
            If either currency code is not found in the rate data.
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency not in self.rates:
            raise ValueError(f"Unknown currency: {from_currency}")
        if to_currency not in self.rates:
            raise ValueError(f"Unknown currency: {to_currency}")

        # Convert through the base currency
        amount_in_base = amount / self.rates[from_currency]
        converted = amount_in_base * self.rates[to_currency]
        return round(converted, 4)


# ---------------------------------------------------------------------------
# Quick self-test when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    converter = RealTimeCurrencyConverter(base="USD")
    currencies = converter.get_currencies()
    print(f"Loaded {len(currencies)} currencies.  Sample: {currencies[:8]}")

    test_cases = [
        ("USD", "INR", 100),
        ("EUR", "GBP", 50),
        ("JPY", "USD", 1000),
    ]
    for src, tgt, amt in test_cases:
        result = converter.convert(src, tgt, amt)
        print(f"  {amt:>8} {src}  ->  {result:>12.4f} {tgt}")
