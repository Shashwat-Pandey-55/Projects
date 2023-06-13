import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from ratelimit import RateLimitException

from helpers import apology, login_required, lookup, usd, time_convert

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("".join(("sqlite:///", os.path.abspath("finance.db"))))

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Pull portofolio data of user if any, else render blank template
    try:
        stocks = db.execute("SELECT stock_symbol, shares_owned, average_value_per_share FROM portofolios WHERE id = ?", session["user_id"])
    except:
        return render_template("index.html")

    # Collect each stock data from database in a dictionary
    quotes = []
    for stock in stocks:
        temp = {}
        temp["symbol"] = stock["stock_symbol"]
        temp["price"] = stock["average_value_per_share"]
        temp["name"] = db.execute("SELECT stock_name FROM transactions WHERE id = ? AND stock_symbol = ? LIMIT 1", session["user_id"], temp["symbol"])[0]["stock_name"]
        temp["total"] = temp["price"] * stock["shares_owned"]
        temp["shares"] = stock["shares_owned"]
        quotes.append(temp)

    # Pull user cash balance data
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = cash[0]["cash"]

    # Calculate total portofolio balance
    total_portofolio = sum(item["total"] for item in quotes)
    total_portofolio += cash

    return render_template("index.html", quotes=quotes, cash=cash, total_portofolio=total_portofolio)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure API calls success
        try:
            quotes = lookup(request.form.get("symbol"))
        except RateLimitException as api_limit:
            waiting_time = time_convert(api_limit.period_remaining)
            return apology(f"API Calls hit limit, please try again in {waiting_time}", 503)
        
        # Ensure submitted symbol is valid
        if quotes is None:
            return apology("invalid symbol", 400)

        # Ensure submitted shares is valid
        shares = request.form.get("shares")
        if re.search("^[0-9]+$", shares) is None:
            return apology("blank or invalid number of shares", 400)

        shares = int(shares)

        # Ensure user can afford the purchase
        total_purchase = quotes["price"] * shares
        current_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        current_cash = current_cash[0]["cash"]
        if total_purchase > current_cash:
            return apology("not enough cash balance", 400)

        # Update purchase transaction into database
        db.execute("INSERT INTO transactions (id, stock_symbol, stock_name, price, shares_number, total_value, transaction_type, transaction_datetime) VALUES (?, ?, ?, ?, ?, ?, 'BUY', datetime('now'))",
                   session["user_id"], quotes["symbol"], quotes["name"], quotes["price"], shares, total_purchase)

        # If stock already owned, update portofolio shares number, else insert new stock data
        try:
            stock_owned = db.execute(
                "SELECT stock_symbol, shares_owned, average_value_per_share FROM portofolios WHERE id = ? AND stock_symbol = ?", session["user_id"], quotes["symbol"])[0]
            
            # Calculate average_value_per_share after purchase
            total_shares = stock_owned["shares_owned"] + shares
            total_value = (stock_owned["shares_owned"] * stock_owned["average_value_per_share"]) + total_purchase
            new_avg_value = total_value // total_shares
            
            db.execute("UPDATE portofolios SET shares_owned = ?, average_value_per_share = ? WHERE id = ? AND stock_symbol = ?",
                       total_shares, new_avg_value, session["user_id"], quotes["symbol"])
        except:
            db.execute("INSERT INTO portofolios (id, stock_symbol, shares_owned, average_value_per_share) VALUES (?, ?, ?, ?)",
                       session["user_id"], quotes["symbol"], shares, quotes["price"])

        # Update user cash balance
        updated_cash = current_cash - total_purchase
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, session["user_id"])

        # Redirect to homepage
        flash("Your BUY transaction is successful")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        symbol = request.args.get("symbol")
        if symbol is None:
            return render_template("buy.html")
        else:
            return render_template("buy.html", symbol=symbol)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Pull transaction history data of user if any, else render blank template
    try:
        history = db.execute(
            "SELECT stock_symbol, shares_number, price, transaction_type, transaction_datetime FROM transactions WHERE id = ?", session["user_id"])
        return render_template("history.html", history=history)
    except:
        return render_template("history.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure API calls success
        try:
            quotes = lookup(request.form.get("symbol"))
        except RateLimitException as api_limit:
            waiting_time = time_convert(api_limit.period_remaining)
            return apology(f"API Calls hit limit, please try again in {waiting_time}", 503)

        # Ensure submitted symbol is valid
        if quotes is None:
            return apology("invalid symbol", 400)
        else:
            return render_template("quoted.html", quotes=quotes)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure password match with the confirmation
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("password did not match with the confirmation", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username have not already exists
        if rows:
            return apology("username already exist", 400)

        # Generate hash password and insert into database
        password_hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), password_hash)

        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("You are successfully registered")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    # User already logged in will be redirected to homepage
    else:
        if session.get("user_id") is None:
            return render_template("register.html")
        else:
            return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure user have stocks to sell
        stock_list = db.execute("SELECT shares_owned, stock_symbol FROM portofolios WHERE id = ?", session["user_id"])
        if len(stock_list) == 0:
            return apology("You do not have any stocks to sell", 400)

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure API calls success
        try:
            quotes = lookup(request.form.get("symbol"))
        except RateLimitException as api_limit:
            waiting_time = time_convert(api_limit.period_remaining)
            return apology(f"API Calls hit limit, please try again in {waiting_time}", 503)

        # Ensure submitted symbol is valid
        if quotes is None:
            return apology("invalid symbol", 403)
        elif not any(item["stock_symbol"] == quotes["symbol"] for item in stock_list):
            return apology("You do not have any shares of this stock", 400)

        # Ensure submitted shares is valid
        shares = request.form.get("shares")
        if re.search("^[0-9]+$", shares) is None:
            return apology("blank or invalid number of shares", 400)

        shares = int(shares)
        shares_owned = sum(item["shares_owned"] for item in stock_list if item["stock_symbol"] == quotes["symbol"])
        if shares > shares_owned:
            return apology("You do not have that many shares of the stock", 400)

        # Calculate total sell value
        total_sold = quotes["price"] * shares

        # Update sell transaction into database
        db.execute("INSERT INTO transactions (id, stock_symbol, stock_name, price, shares_number, total_value, transaction_type, transaction_datetime) VALUES (?, ?, ?, ?, ?, ?, 'SELL', datetime('now'))",
                   session["user_id"], quotes["symbol"], quotes["name"], quotes["price"], shares, total_sold)

        # Update portofolio shares number, else insert new stock data
        if shares == shares_owned:
            db.execute("DELETE FROM portofolios WHERE id = ? AND stock_symbol = ?", session["user_id"], quotes["symbol"])
        else:
            db.execute("UPDATE portofolios SET shares_owned = ? WHERE id = ? AND stock_symbol = ?",
                       shares_owned - shares, session["user_id"], quotes["symbol"])

        # Update user cash balance
        current_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        updated_cash = current_cash[0]["cash"] + total_sold
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, session["user_id"])

        # Redirect to homepage
        flash("Your SELL transaction is successful")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        stocks = db.execute("SELECT stock_symbol FROM portofolios WHERE id = ?", session["user_id"])

        symbol = request.args.get("symbol")
        if symbol is None:
            return render_template("sell.html", stocks=stocks)
        else:
            return render_template("sell.html", symbol=symbol, stocks=stocks)
