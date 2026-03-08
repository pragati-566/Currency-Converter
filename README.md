# 💱 Real-Time Currency Converter

A Python desktop application that converts currencies in real-time using live exchange rate data fetched from the [exchangerate-api.com](https://www.exchangerate-api.com/) API, with a Tkinter GUI.

## 📁 Project Structure

```
Currency-Converter/
├── main.py          # Tkinter GUI — run this to start the app
├── converter.py     # RealTimeCurrencyConverter class (API + conversion logic)
└── README.md
```

## 🚀 Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 or later |
| `requests` | Any recent version |


### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pragati-566/Currency-Converter.git
   cd Currency-Converter
   ```

2. **Install the only dependency**
   ```bash
   pip install requests
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

---

## 🖥️ How to Use

| Step | Action |
|---|---|
| 1 | Select the **source currency** from the left dropdown |
| 2 | Enter the **amount** you want to convert |
| 3 | Select the **target currency** from the right dropdown |
| 4 | Click **Convert** |
| 5 | The converted amount appears in the result box |

> Use the **⇄** button to swap the source and target currencies with a single click.
