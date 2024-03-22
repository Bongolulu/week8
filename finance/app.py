import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"]=True
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


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
    
    # Kontostand
    rows=db.execute("select cash from users where id = ?",session["user_id"])
    kontostand=rows[0]["cash"]
    # Symbol und shares aus history
    ergebnis=db.execute("select symbol, sum (shares) as anzahl from history where users_id=? group by symbol",session["user_id"])
    
    # durchs ganze ergebnis gehen und für jede aktie den aktuellen wert heraussuchen

    for eintrag in ergebnis:
        eintrag["preis"] = lookup(eintrag["symbol"]).get("price")
        eintrag["total"] = eintrag["preis"]*eintrag["anzahl"]

    gesamtbetrag=kontostand+ sum(eintrag["total"] for eintrag in ergebnis)   

    # index in neues template index.html flanschen, cash und total einbringen
    return render_template("index.html",index=ergebnis, bargeld=kontostand, gesamtbetrag=gesamtbetrag)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""   
    if request.method == "POST":
        ergebnis=lookup (request.form.get("symbol"))
        if not ergebnis:
            return render_template("buy.html",fehler="Symbol not found")  
        
        
        """prüfen ob anzahl eine ganzzahl ist"""
        if re.match(r'^[1-9]\d*$', request.form.get("shares")) is None:
             return render_template("buy.html",fehler="Please enter an integer larger than 0")
        anzahl = int(request.form.get("shares"))
        
        # kaufkosten cash, shares, price
        kaufkosten=anzahl * ergebnis.get("price")
        
        #ausrechnen, ob noch genügend geld zur verfügung steht
        rows=db.execute("select cash from users where id = ?",session["user_id"])
        kontostand=rows[0]["cash"]
        
        # ausrechnen, wie viel geld noch vorhanden ist    
        neuerKontostand = (kontostand - kaufkosten)
        
        
        if kaufkosten > kontostand:
            return apology(f"You only have {usd(kontostand)} at your disposal. You need {usd(kaufkosten)}")
        
        # buy in db einfügen
        db.execute("INSERT INTO history (users_id, symbol, shares, price) VALUES(?, ?, ?, ?)",session["user_id"], request.form.get("symbol"), anzahl, ergebnis.get("price"))
        
        # db aktualisieren
        db.execute("update users set cash = ? where id = ?",neuerKontostand, session["user_id"])

        return redirect("/")

    else:
        return render_template("buy.html")
    

@app.route("/history")
@login_required
def history():
    
    # history aus db abrufen
    ergebnis=db.execute("select *,CASE WHEN shares>0 THEN 'BUY' ELSE 'SELL' END AS buysell, shares*price as total from history where users_id=?",session["user_id"])

    # history in neues template history.html flanschen
    """Show history of transactions"""
    return render_template("history.html",history=ergebnis)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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
    if request.method == "POST":
        ergebnis=lookup (request.form.get("symbol"))
        if not ergebnis:
            return render_template("quote.html",fehler=True)
        return render_template("quote.html", symbol = ergebnis.get("symbol"),price = ergebnis.get("price"))        
        #zeige den aktienpreis an
    else:
        return render_template("quote.html")
    """Get stock quote."""


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
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
        
        elif not request.form.get ("confirmation"):
            return apology("must confirm password", 403)
        
        elif not request.form.get("password") == request.form.get ("confirmation"):
            return apology("Passwords do not match", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        
        if len(rows) ==1:
            return apology("Username already exists")
        # passwort hashen
        hashed_password=generate_password_hash(request.form.get("password"))
        # user in db einfügen
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"), hashed_password)
        
        # Redirect user to home page
        return redirect("/")
    
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == 'POST':
        if not request.form.get("shares") or not request.form.get("symbol"):
            return apology("Anzahl und/oder Symbol nicht eingegeben", 403)
    
        #ausrechnen, ob noch genügend aktien zur verfügung stehen
        rows=db.execute("select sum (shares) as vorhandeneAktien from history where symbol = ? and users_id = ? group by symbol",request.form.get("symbol"), session["user_id"])
        aktienbestand=rows[0]["vorhandeneAktien"]
        
        if request.form.get("shares") > aktienbestand:
            return apology(f"Too many shares")
        
        
        
        
        
        symbol = request.form['symbol']
        return f'Du hast die Option {symbol} ausgewählt.'
    else:
        ergebnis=db.execute("select symbol from history where users_id=? group by symbol",session["user_id"])
        symbols=[dct[next(iter(dct))] for dct in ergebnis]
        return render_template('sell.html',symbols=symbols)


if __name__ == '__main__':
    app.run(debug=True)
    
    
   