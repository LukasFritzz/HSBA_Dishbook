from flask import Flask, render_template, request, jsonify, redirect, flash, url_for
import cv2
import pytesseract
import requests
import os
import secrets
import openai
import ast
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
from res.py.db import execute_sql_query

GOOGLE_API_KEY      = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
SEARCH_ENGINE_ID    = 'XXXXXXXXXXXXXXXXX'
TESSERACT_PATH      = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
openai.api_key      = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def process_image(imagePath):

    image = cv2.imread(imagePath)

    recognizedText  = pytesseract.image_to_string(image)
    openaiResponse  = ""
    filteredData    = []

    if not recognizedText.strip():
        return "error4", recognizedText, openaiResponse

    try:
        openaiResponse = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "you are chef. Follow 2 steps. 1. step: extract all dishes you can find in text1 = '" + recognizedText + "'and respond with array[[,],[,] etc...] and no other explanation. Array[i][0] contains names of extracted dishes that appear in text1. Correct the names if typo. 2 step which (does not relate to my text1) append array with new column Array[i][1] which contains helpful information (<= 10 words) of dish, generate your own don't take it from text1"}],  
            max_tokens=150
        )
    except Exception as e:
        return "error1", recognizedText, openaiResponse
        
    try:
        responseArray = ast.literal_eval(openaiResponse.choices[0].message.content)
    except (ValueError, SyntaxError):
        return "error2", recognizedText, openaiResponse
    
    if not isinstance(responseArray, list):
        return "error2", recognizedText, openaiResponse

    for line in responseArray:
        url, isError = get_relevant_image("meal: " + line[0])
        if isError:
            return "error3", recognizedText, openaiResponse
        filteredData.append([line[0],line[1],url])

    data = [{'line': lineMeal, 'text': lineText, 'image': image} for lineMeal, lineText, image in filteredData]

    return data, recognizedText, openaiResponse


def get_relevant_image(searchQuery):
    relevantImage   = None
    numberResults   = 3
    isError         = False
    url             = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={searchQuery}&searchType=image&num={numberResults}'

    data = requests.get(url).json()

    if 'items' in data:
        for dish in data['items']:
            imageUrl = dish.get('link')

            if imageUrl and imageUrl.lower().endswith(('.jpg', '.png')):
                relevantImage = imageUrl
                break
    else:
        if data['error']['code'] == 429:
            isError = True

    return relevantImage, isError


def allowed_file(fileName):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in fileName and fileName.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image():
    if 'image' not in request.files:
        return True, "error5"

    image = request.files['image']
    if not image.filename:
        return True, "error6"
    
    if not allowed_file(image.filename):
        return True, "error7"
    
    return False, ""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():

    isError, data = validate_image()

    folderPath  = 'res/img/'
    files       = os.listdir(folderPath)
    folderId    = 0
    for image in files:
        if image.startswith('card_'):
            try:
                currentId   = int(image.split('_')[1].split('.')[0])
                folderId    = max(folderId, currentId)
            except ValueError:
                pass
    
    queryID = execute_sql_query("SELECT MAX(ID) FROM Query", False, fetch=True)[0][0]

    newId = max(queryID, folderId) + 1 if queryID is not None else folderId + 1
    
    errorMessage = {
        'error1': 'OpenAI SSL certificate error.'
        ,'error2': 'OpenAI ouput error.'
        ,'error3': 'Exceeded google api limit.'
        ,'error4': 'No text was found.'
        ,'error5': 'No image provided.'
        ,'error6': 'No selected file.'
        ,'error7': 'Invalid file format.'
    }

    if not isError:
        fileName        = f'card_{newId}.jpg'
        imagePath       = os.path.join(folderPath, fileName)
        request.files['image'].save(imagePath)
    
        data, recognizedText, openaiResponse = process_image(imagePath)
        isError         = isinstance(data, str) and data in errorMessage
        insertValue     = (newId, recognizedText, str(openaiResponse), int(isError), None if not isError else errorMessage[data], imagePath),
  
    else:
        insertValue     = (newId, None, None, 1, errorMessage[data], None),

    insertStatement     = "INSERT INTO Query (ID, RECOGNIZED_TEXT, OPENAI_RESPONSE, IS_ERROR, ERROR_MESSAGE, IMAGE) VALUES (%s,%s,%s,%s,%s,%s)"
    execute_sql_query(insertStatement, insertValue, fetch=False)
    
    if isError:
        flash(errorMessage[data], 'error')
        return redirect(url_for('index'))

    insertStatement     = "INSERT INTO Result (QUERY_ID, DISH, TEXT, IMAGE) VALUES (%s, %s, %s, %s)"
    insertValue         = [(newId, item['line'], item['text'], item['image']) for item in data]
    execute_sql_query(insertStatement, insertValue, fetch=False)

    return render_template('index.html', data=data)

@app.route('/imprint')
def imprint():
    return render_template('imprint.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# start server
if __name__ == '__main__':
    app.run(debug=True)
