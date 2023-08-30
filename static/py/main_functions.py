import pytesseract
import os
import ast

from static.py.help_functions   import *
from forex_python.converter     import CurrencyCodes

from langchain.vectorstores     import FAISS
from langchain.document_loaders import TextLoader
from langchain.indexes          import VectorstoreIndexCreator
from langchain.chat_models      import ChatOpenAI

os.environ["OPENAI_API_KEY"] = keys.APIKEY

chat_model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", streaming=True)
chat_model.openai_api_key = os.environ['OPENAI_API_KEY']

def process_text(path):
    loader = TextLoader(path, encoding='utf8')

    languageMap = {
        'de': 'german',
        'es': 'spanish',
        'en': 'english'
    }
    language = languageMap.get(request.headers.get('Accept-Language')[:2].lower(), 'english')

    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()


    query = """
    extract dishes with prices and currencies if available.
    Respond with a Python-usable array:
    [
        [
            dish name 1,
            your own brief description of dish in """ + language + """ language (up to 10 words),
            extracted price of dish (default = None),
            currency as ISO code (default = USD)
        ],
        [...],
        ...
    ]
    Limit the description to a maximum of 10 words.
    Correct dish names for typos and adjust capitalization.
    """

    index = VectorstoreIndexCreator(vectorstore_cls=FAISS).from_loaders([loader])

    result = index.query(query, llm=chat_model)

    tokens = num_tokens_from_string(text, "cl100k_base") + num_tokens_from_string(query, "cl100k_base") + num_tokens_from_string(result, "cl100k_base")
    
    return result, tokens


def process_image(imagePath, newId):

    recognizedText  = pytesseract.image_to_string(imagePath, config=keys.myconfig)
    response        = ""
    filteredData    = []
    tokens          = 0

    if not recognizedText.strip():
        return "error3", recognizedText, response, tokens

    outputFile = f'static/temp/data_{newId}.txt'
    with open(outputFile, 'w', encoding='utf-8') as file:
        file.write(recognizedText)

    response, tokens = process_text(outputFile)

    try:
        print(response)
        if isinstance(response, str):
            responseArray = ast.literal_eval(response)
        elif isinstance(response, list):
            responseArray = response
        else:
            return "error1", recognizedText, response, tokens   
    except (ValueError, SyntaxError):
        return "error1", recognizedText, response, tokens
    
    os.remove(outputFile)

    ToCurrency = get_user_home_currency()

    currency_codes = CurrencyCodes()

    for line in responseArray:
        url, isError = get_relevant_image("meal: " + line[0])
        if isError:
            return "error2", recognizedText, response, tokens
        if line[2] and line[3] and currency_codes.get_currency_name(line[3]):
            try:
                euroPrice   = round(convert_to_euro(line[3], ToCurrency, line[2]), 2)
            except:
                pass
        else:
            euroPrice   = "-"

        filteredData.append([line[0],line[1],euroPrice,ToCurrency,url])

    data = [{'line': lineMeal, 'text': lineText, 'price': price, 'currency': currency, 'image': image} for lineMeal, lineText, price, currency, image in filteredData]

    return data, recognizedText, response, tokens


def get_relevant_image(searchQuery):
    relevantImage   = None
    numberResults   = 3
    isError         = False
    url             = f'https://www.googleapis.com/customsearch/v1?key={keys.GOOGLE_API_KEY}&cx={keys.SEARCH_ENGINE_ID}&q={searchQuery}&searchType=image&num={numberResults}&fileType=jpg,png'

    data = requests.get(url).json()

    if 'items' in data:
        for dish in data['items']:
            imageUrl = dish.get('link')

            if imageUrl and allowed_file(imageUrl):
                relevantImage = imageUrl
                break
    else:
        if data['error']['code'] == 429:
            isError = True

    return relevantImage, isError