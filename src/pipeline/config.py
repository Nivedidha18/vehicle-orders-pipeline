from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "build"

DUCKDB_PATH = OUT_DIR / "warehouse.duckdb"
PARQUET_DIR = OUT_DIR / "parquet"

ORDERS_CSV = DATA_DIR / "orders.csv"
VEHICLES_CSV = DATA_DIR / "vehicles.csv"

REPORTING_CURRENCY = "GBP"

# Exchange rates to GBP
FX_RATES_TO_GBP = {
    "GBP": 1.00,
    "EUR": 0.85,
    "USD": 0.79,
    "CHF": 0.88,
    "SEK": 0.075,
    "NOK": 0.074,
    "DKK": 0.11,
    "PLN": 0.20,
}
# Currency symbols found in source files
CURRENCY_SYMBOLS = {
    "£": "GBP",
    "€": "EUR",
    "$": "USD",
    "kr": "SEK",
    "zł": "PLN",
}
# Market mappings
MARKET_ALIASES = {
    "uk": "United Kingdom",
    "gb": "United Kingdom",
    "gbr": "United Kingdom",
    "united kingdom": "United Kingdom",
    "great britain": "United Kingdom",

    "de": "Germany",
    "ger": "Germany",
    "deu": "Germany",
    "deutschland": "Germany",
    "germany": "Germany",

    "fr": "France",
    "fra": "France",
    "france": "France",

    "es": "Spain",
    "esp": "Spain",
    "spain": "Spain",
    "españa": "Spain",

    "it": "Italy",
    "ita": "Italy",
    "italy": "Italy",
    "italia": "Italy",

    "nl": "Netherlands",
    "nld": "Netherlands",
    "netherlands": "Netherlands",
    "holland": "Netherlands",

    "se": "Sweden",
    "swe": "Sweden",
    "sweden": "Sweden",

    "pl": "Poland",
    "pol": "Poland",
    "poland": "Poland",
}
# Used for validation checks only
MARKET_DEFAULT_CURRENCY = {
    "United Kingdom": "GBP",
    "Germany": "EUR",
    "France": "EUR",
    "Spain": "EUR",
    "Italy": "EUR",
    "Netherlands": "EUR",
    "Sweden": "SEK",
    "Poland": "PLN",
}
# Sales channels
CHANNEL_ALIASES = {
    "online": "Online",
    "web": "Online",
    "website": "Online",
    "ecommerce": "Online",
    "e-commerce": "Online",

    "subscription": "Subscription",
    "subscribe": "Subscription",

    "dealer": "Dealer",
    "dealership": "Dealer",
    "showroom": "Dealer",
    "branch": "Dealer",

    "phone": "Phone",
    "telephone": "Phone",
    "call": "Phone",
    "call centre": "Phone",
    "call center": "Phone",

    "partner": "Partner",
    "broker": "Partner",
    "fleet": "Fleet",
}
# Fuel types
FUEL_ALIASES = {
    "petrol": "Petrol",
    "gasoline": "Petrol",
    "gas": "Petrol",

    "diesel": "Diesel",

    "electric": "Electric",
    "ev": "Electric",
    "bev": "Electric",

    "hybrid": "Hybrid",
    "hev": "Hybrid",

    "phev": "Plug-in Hybrid",
    "plug-in hybrid": "Plug-in Hybrid",
    "plugin hybrid": "Plug-in Hybrid",
}
# Vehicle manufacturers
MAKE_ALIASES = {
    "vw": "Volkswagen",
    "volkswagen": "Volkswagen",

    "merc": "Mercedes-Benz",
    "mercedes": "Mercedes-Benz",
    "mercedes benz": "Mercedes-Benz",

    "bmw": "BMW",
    "audi": "Audi",
    "skoda": "Skoda",
    "seat": "SEAT",
    "cupra": "Cupra",
    "renault": "Renault",
    "peugeot": "Peugeot",
    "citroen": "Citroen",
    "toyota": "Toyota",
    "tesla": "Tesla",
    "ford": "Ford",
    "vauxhall": "Vauxhall",
    "opel": "Opel",
    "kia": "Kia",
    "hyundai": "Hyundai",
}
# Order statuses
STATUS_ALIASES = {
    "completed": "completed",
    "complete": "completed",
    "fulfilled": "completed",
    "delivered": "completed",

    "cancelled": "cancelled",
    "canceled": "cancelled",
    "cancel": "cancelled",

    "returned": "returned",
    "refunded": "returned",

    "pending": "pending",
    "processing": "pending",
    "in progress": "pending",
    "open": "pending",
}
# Statuses treated as successful sales
COMPLETED_STATUSES = {"completed"}