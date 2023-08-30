import  requests
import  tiktoken
import  static.py.keys          as keys

from    flask                   import request
from    forex_python.converter  import CurrencyRates
from    PIL                     import Image
from    PIL.ExifTags            import TAGS

def get_user_home_currency():
    languageCurrency = {
        'de': 'EUR',
        'es': 'MXN',
        'en': 'USD',
        'uk': 'GBP'
    }
    userLanguage = request.headers.get('Accept-Language')
    return languageCurrency.get(userLanguage[:2].lower(), 'USD')


def convert_to_euro(FromCurrency, ToCurrency, price):
    c           = CurrencyRates()
    euroAmount  = c.convert(FromCurrency, ToCurrency, price)
    return euroAmount


def allowed_file(fileName):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in fileName and fileName.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_input():
    if 'image' not in request.files:
        return True, "error4"

    image = request.files['image']

    if not image.filename:
        return True, "error5"
    
    if not allowed_file(image.filename):
        return True, "error6"
    
    if 'privacyTerms' not in request.form:
        return True, "error7"
    
    return False, ""


def dms_to_decimal(degrees, minutes, seconds):
    decimal_value = degrees + (minutes / 60) + (seconds / 3600)
    return float(decimal_value)


def get_address_from_coordinates(latitude, longitude):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={keys.GOOGLE_API_KEY}"
    
    response    = requests.get(url)
    data        = response.json()
    
    if data["status"] == "OK":
        result  = data["results"][0]
        address = result["formatted_address"]
        return address
    else:
        return None


def get_nearest_restaurant(latitude, longitude):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=500&type=restaurant&key={keys.GOOGLE_API_KEY}"
    
    response    = requests.get(url)
    data        = response.json()
    
    if data["status"] == "OK" and len(data["results"]) > 0:
        restaurant_name = data["results"][0]["name"]
        return restaurant_name
    else:
        return None


def get_meta_data(imagePath):
    restaurantName  = None
    address         = None

    try:
        img = Image.open(imagePath)
        exifData = img._getexif()

        for tag, value in exifData.items():
            tagName = TAGS.get(tag, tag)
            
            if tagName == 'GPSInfo':
                if isinstance(value, dict):
                    lat             = value.get(2)
                    lon             = value.get(4)        
                    latitude        = dms_to_decimal(*lat)
                    longitude       = dms_to_decimal(*lon)
                    address         = get_address_from_coordinates(latitude, longitude)
                    restaurantName  = get_nearest_restaurant(latitude, longitude)
    except:
        pass

    return restaurantName, address

def num_tokens_from_string(text, encodingName):
    encoding    = tiktoken.get_encoding(encodingName)
    numTokens   = len(encoding.encode(text))
    return numTokens