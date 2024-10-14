from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)
app.config['API_KEY'] = '1928401'

# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# Get a random cafe from DB
@app.route("/random")
def get_random():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(random_cafe.to_dict())


# Get all cafes
@app.route('/all')
def get_all():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    cafe_list = []
    for cafe in all_cafes:
        cafe_list.append(cafe.to_dict())
    return jsonify(cafe_list)


# Search DB by location
@app.route('/search')
def search():
    location = request.args.get('location')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == location))
    all_results = result.scalars().all()
    if all_results:
        return jsonify(cafe=[cafe.to_dict() for cafe in all_results])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# Add cafe to DB
@app.route('/addcafe', methods=['POST'])
def add_cafe():
    new_cafe = Cafe(name=request.form.get('name'),
                    map_url=request.form.get('map_url'),
                    img_url=request.form.get('img_url'),
                    location=request.form.get('location'),
                    seats=request.form.get('seats'),
                    has_sockets=bool(request.form.get('has_sockets')),
                    has_toilet=bool(request.form.get('has_toilet')),
                    can_take_calls=bool(request.form.get('can_take_calls')),
                    coffee_price=request.form.get('coffee_price'),
                    has_wifi=bool(request.form.get('has_wifi'))
                    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# Update a cafe's coffee price
@app.route('/updateprice/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    try:
        new_price = request.args.get('price')
        cafe_to_edit = db.get_or_404(Cafe, cafe_id)
        cafe_to_edit.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully edited the cafe details."})
    except:
        return jsonify(error={"Not Found": "Sorry, we cannot find a cafe with that id.",},), 404


# Delete a cafe from DB
@app.route('/deletecafe/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    if request.args.get('api-key') == app.config['API_KEY']:
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(response={"success": "Successfully deleted the cafe."})
    else:
        return jsonify(error={"Permissions Error": "Sorry, you do not have the correct permissions."}), 403


if __name__ == '__main__':
    app.run(debug=True)
