import pytesseract
import os
import ast

from static.py.help_functions   import *
from iso4217                    import Currency
from langchain.document_loaders import TextLoader
from langchain.indexes          import VectorstoreIndexCreator
from langchain.chat_models      import ChatOpenAI
from langchain.memory           import ConversationBufferMemory

def process_image(imagePath, newId):

    recognizedText  = pytesseract.image_to_string(imagePath, config=keys.myconfig)
    response  = ""
    filteredData    = []

    if not recognizedText.strip():
        return "error3", recognizedText, response
    
    languageMap = {
        'de': 'german',
        'es': 'spanish',
        'en': 'english'
    }
    language = languageMap.get(request.headers.get('Accept-Language')[:2].lower(), 'english')

    outputFile = f'static/temp/data_{newId}.txt'
    with open(outputFile, 'w', encoding='utf-8') as file:
        file.write(recognizedText)

    # reset muss weiterhin getestet werden, nicht 100% sicher
    ConversationBufferMemory().clear()
    os.environ["OPENAI_API_KEY"] = keys.APIKEY
    
    query   = "extract all dishes and (prices, currencies if available) and respond with python usable array[[name of dish 1, explanation of what dish could consist in " + language + " language. (create your own text and use a maximum of 10 words), extracted price of respective dish as number default = None, Price currency ISO code default = USD],[,,,] etc...] and no other explanation. Correct dish names if typo and adjust capitalization of dish"

    loader          = TextLoader(outputFile)
    index           = VectorstoreIndexCreator().from_loaders([loader])
    response        = index.query(query, llm=ChatOpenAI())

    try:
        print(response)
        if isinstance(response, str):
            responseArray = ast.literal_eval(response)
            print("if")
        elif isinstance(response, list):
            responseArray = response
            print("elif")
        else:
            print("else")
            return "error1", recognizedText, response   
    except (ValueError, SyntaxError):
        print("except")
        return "error1", recognizedText, response
    
    os.remove(outputFile)

    ToCurrency = get_user_home_currency()

    for line in responseArray:
        url, isError = get_relevant_image("meal: " + line[0])
        if isError:
            return "error2", recognizedText, response
        if line[2] and line[3]:
            try:
                Currency(line[3])
                euroPrice   = round(convert_to_euro(line[3], ToCurrency, line[2]), 2)
            except:
                pass
        else:
            euroPrice   = "-"

        filteredData.append([line[0],line[1],euroPrice,ToCurrency,url])

    data = [{'line': lineMeal, 'text': lineText, 'price': price, 'currency': currency, 'image': image} for lineMeal, lineText, price, currency, image in filteredData]

    return data, recognizedText, response



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