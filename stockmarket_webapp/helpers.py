import os
import requests
import urllib.parse
import time

from flask import redirect, render_template, session
from functools import wraps
from ratelimit import limits, RateLimitException


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@limits(calls=500, period=86400)
@limits(calls=5, period=60)
def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={urllib.parse.quote_plus(symbol)}&apikey={api_key}"
        response_1 = requests.get(url)
        response_1.raise_for_status()
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={urllib.parse.quote_plus(symbol)}&apikey={api_key}"
        response_2 = requests.get(url)
        response_2.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        company_overview = response_1.json()
        quote = response_2.json()["Global Quote"]
        return {
            "name": company_overview["Name"],
            "symbol": company_overview["Symbol"],
            "price": float(quote["05. price"])
        }
    except (KeyError, TypeError, ValueError):
        if response_1.json().get("Note"):
            raise RateLimitException("API hits limit", 59)
        else:
            return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def time_convert(seconds):
    if seconds > 3600:
        converted_time = time.strftime("%H hours %M minutes", time.gmtime(seconds))
    elif seconds > 60:
        converted_time = time.strftime("%M minutes %S seconds", time.gmtime(seconds))
    else:
        converted_time = time.strftime("%S seconds", time.gmtime(seconds))
    return converted_time
