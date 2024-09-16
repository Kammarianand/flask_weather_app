from flask import Flask, render_template, request, redirect, url_for
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=25d3252148432ed7a153fa0bb2e2ab47'
    try:
        r = requests.get(url.format(city)).json()
        return {
            'city': city,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon']
        }
    except KeyError:
        return None

@app.route('/')
def index():
    cities = City.query.all()
    weather_data = []
    for city in cities:
        city_weather = get_weather_data(city.name)
        if city_weather:
            weather_data.append(city_weather)
    return render_template('weather.html', weather=weather_data)

@app.route('/add', methods=['POST'])
def add_city():
    new_city = request.form.get('city')
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_obj = City(name=new_city)
            db.session.add(new_city_obj)
            db.session.commit()
    return redirect(url_for('index'))

def initialize_db():
    with app.app_context():
        db.create_all()
        if City.query.count() == 0:
            initial_cities = ['New York', 'London', 'Tokyo']
            for city_name in initial_cities:
                new_city = City(name=city_name)
                db.session.add(new_city)
            db.session.commit()

# if __name__ == '__main__':
#     initialize_db()
#     app.run(debug=True)