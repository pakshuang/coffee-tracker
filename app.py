from datetime import datetime
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy


load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "sketchy"


class CoffeeBag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brew_method = db.Column(db.String(100), nullable=False)
    roaster = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    tasting_notes = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    target_freeze_date = db.Column(db.String(20), nullable=False)
    grams = db.Column(db.Integer, nullable=False)
    frozen = db.Column(db.Boolean, default=False)


class CoffeeVials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brew_method = db.Column(db.String(100), nullable=False)
    roaster = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    tasting_notes = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    vials = db.Column(db.Integer, nullable=False)
    grams_per_vial = db.Column(db.Integer, nullable=False)
    actual_freeze_date = db.Column(db.String(20), nullable=False)


# Inject website name
@app.context_processor
def inject_website_name():
    return dict(website_name=os.getenv("WEBSITE_NAME"))


@app.route("/", methods=["GET"])
def index():
    # Get beans from database
    coffee_bags = db.session.scalars(
        db.select(CoffeeBag)
        .where(CoffeeBag.frozen == False)
        .order_by(CoffeeBag.target_freeze_date.asc())
    )
    coffee_vials = db.session.scalars(
        db.select(CoffeeVials)
        .where(CoffeeVials.vials > 0)
        .order_by(CoffeeVials.vials.desc())
    )

    past_vials = db.session.scalars(
        db.select(CoffeeVials)
        .where(CoffeeVials.vials == 0)
        .order_by(CoffeeVials.actual_freeze_date.desc())
    )

    return render_template(
        "index.html",
        coffee_bags=coffee_bags,
        coffee_vials=coffee_vials,
        past_vials=past_vials,
    )


# Add beans to database
@app.route("/add_bag", methods=["GET", "POST"])
def add_bag():
    if request.method == "POST":
        name = request.form.get("name")
        brew_method = request.form.get("brew_method")
        roaster = request.form.get("roaster")
        origin = request.form.get("origin")
        tasting_notes = request.form.get("tasting_notes")
        notes = request.form.get("notes")
        target_freeze_date = request.form.get("target_freeze_date")
        grams = request.form.get("grams")
        new_coffee = CoffeeBag(
            name=name,
            brew_method=brew_method,
            roaster=roaster,
            origin=origin,
            tasting_notes=tasting_notes,
            notes=notes,
            target_freeze_date=target_freeze_date,
            grams=grams,
        )
        db.session.add(new_coffee)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add_bag.html")


@app.route("/add_vial", methods=["GET", "POST"])
def add_vial():
    if request.method == "POST":
        name = request.form.get("name")
        brew_method = request.form.get("brew_method")
        roaster = request.form.get("roaster")
        origin = request.form.get("origin")
        tasting_notes = request.form.get("tasting_notes")
        notes = request.form.get("notes")
        vials = request.form.get("vials")
        grams_per_vial = request.form.get("grams_per_vial")
        actual_freeze_date = request.form.get("actual_freeze_date")
        new_coffee = CoffeeVials(
            name=name,
            brew_method=brew_method,
            roaster=roaster,
            origin=origin,
            tasting_notes=tasting_notes,
            notes=notes,
            vials=vials,
            grams_per_vial=grams_per_vial,
            actual_freeze_date=actual_freeze_date,
        )
        db.session.add(new_coffee)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add_vial.html")


# View beans
@app.route("/view_bag/<int:coffee_id>", methods=["GET"])
def view_bag(coffee_id):
    bag = db.get_or_404(CoffeeBag, coffee_id)
    return render_template("view_bag.html", bag=bag)


@app.route("/view_vial/<int:coffee_id>", methods=["GET"])
def view_vial(coffee_id):
    vial = db.get_or_404(CoffeeVials, coffee_id)
    return render_template("view_vial.html", vial=vial)


# Edit beans
@app.route("/edit_bag/<int:coffee_id>", methods=["GET", "POST"])
def edit_bag(coffee_id):
    bag = db.get_or_404(CoffeeBag, coffee_id)
    if request.method == "POST":
        bag.name = request.form.get("name")
        bag.brew_method = request.form.get("brew_method")
        bag.roaster = request.form.get("roaster")
        bag.origin = request.form.get("origin")
        bag.tasting_notes = request.form.get("tasting_notes")
        bag.notes = request.form.get("notes")
        bag.target_freeze_date = request.form.get("target_freeze_date")
        bag.grams = request.form.get("grams")
        db.session.commit()
        return redirect(url_for("view_bag", coffee_id=bag.id))
    return render_template("edit_bag.html", bag=bag)


@app.route("/edit_vial/<int:coffee_id>", methods=["GET", "POST"])
def edit_vial(coffee_id):
    vial = db.get_or_404(CoffeeVials, coffee_id)
    if request.method == "POST":
        vial.name = request.form.get("name")
        vial.brew_method = request.form.get("brew_method")
        vial.roaster = request.form.get("roaster")
        vial.origin = request.form.get("origin")
        vial.tasting_notes = request.form.get("tasting_notes")
        vial.notes = request.form.get("notes")
        vial.vials = request.form.get("vials")
        vial.grams_per_vial = request.form.get("grams_per_vial")
        vial.actual_freeze_date = request.form.get("actual_freeze_date")
        db.session.commit()
        return redirect(url_for("view_vial", coffee_id=vial.id))
    return render_template("edit_vial.html", vial=vial)


# Delete beans
@app.route("/delete_bag/<int:coffee_id>", methods=["GET"])
def delete_bag(coffee_id):
    bag = db.get_or_404(CoffeeBag, coffee_id)
    db.session.delete(bag)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete_vial/<int:coffee_id>", methods=["GET"])
def delete_vial(coffee_id):
    vial = db.get_or_404(CoffeeVials, coffee_id)
    db.session.delete(vial)
    db.session.commit()
    return redirect(url_for("index"))


# Convert bag to vials
@app.route("/freeze_bag/<int:coffee_id>", methods=["GET", "POST"])
def freeze_bag(coffee_id):
    if request.method == "POST":
        vials = request.form.get("vials")
        grams_per_vial = request.form.get("grams_per_vial")
        actual_freeze_date = request.form.get("actual_freeze_date")
        bag = db.get_or_404(CoffeeBag, coffee_id)
        new_vials = CoffeeVials(
            name=bag.name,
            brew_method=bag.brew_method,
            roaster=bag.roaster,
            origin=bag.origin,
            tasting_notes=bag.tasting_notes,
            notes=bag.notes,
            vials=vials,
            grams_per_vial=grams_per_vial,
            actual_freeze_date=actual_freeze_date,
        )
        db.session.add(new_vials)
        bag.frozen = True
        db.session.commit()
        return redirect(url_for("index"))
    bag = db.get_or_404(CoffeeBag, coffee_id)
    return render_template("freeze_bag.html", bag=bag)


# Convert vials to bag
@app.route("/unfreeze_vial/<int:coffee_id>", methods=["GET"])
def unfreeze_vial(coffee_id):
    coffee_bag = db.get_or_404(CoffeeBag, coffee_id)
    coffee_vials = db.get_or_404(CoffeeVials, coffee_id)
    coffee_bag.frozen = False
    coffee_bag.name = coffee_vials.name
    coffee_bag.brew_method = coffee_vials.brew_method
    coffee_bag.roaster = coffee_vials.roaster
    coffee_bag.origin = coffee_vials.origin
    coffee_bag.tasting_notes = coffee_vials.tasting_notes
    coffee_bag.notes = coffee_vials.notes
    db.session.delete(coffee_vials)
    db.session.commit()
    return redirect(url_for("index"))


# Consume vial
@app.route("/consume_vials/<int:coffee_id>", methods=["GET"])
def consume_vial(coffee_id):
    coffee = db.get_or_404(CoffeeVials, coffee_id)
    vials_available = coffee.vials

    if vials_available <= 0:
        return "No vials to consume!"

    coffee.vials -= 1
    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, host="0.0.0.0")
