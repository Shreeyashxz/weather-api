import requests
from flask import Flask, render_template, request


def get_simple_weather(city):
    """Fetches weather data from wttr.in for a given city and returns a tuple
    (result_dict, error_message). On success, error_message is None.
    """
    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        area = data.get('nearest_area', [{}])[0].get('areaName', [{}])[0].get('value', city)
        current = data.get('current_condition', [{}])[0]
        today = data.get('weather', [{}])[0]

        result = {
            'area': area,
            'current': {
                'temp_C': current.get('temp_C'),
                'feels_like_C': current.get('FeelsLikeC'),
                'description': current.get('weatherDesc', [{}])[0].get('value'),
                'windspeed_kmph': current.get('windspeedKmph'),
                'humidity': current.get('humidity'),
            },
            'today': {
                'maxtempC': today.get('maxtempC'),
                'mintempC': today.get('mintempC'),
                'avgtempC': today.get('avgtempC'),
                'sunrise': today.get('astronomy', [{}])[0].get('sunrise'),
                'sunset': today.get('astronomy', [{}])[0].get('sunset'),
            }
        }

        return result, None

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return None, f"City '{city}' not found."
        return None, f"HTTP error: {http_err}"
    except requests.exceptions.ConnectionError:
        return None, "Could not connect. Check your internet connection."
    except Exception as err:
        return None, f"Error: {err}"


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    error = None
    city_name = ''

    if request.method == 'POST':
        city_name = request.form.get('city', '').strip()
        if not city_name:
            error = 'City name cannot be empty.'
        else:
            weather, error = get_simple_weather(city_name)

    return render_template('index.html', weather=weather, error=error, city=city_name)


if __name__ == '__main__':
    # Run in debug mode on port 5000; change host to '0.0.0.0' for external access
    app.run(debug=True, host='127.0.0.1', port=5000)
    