import  secrets
import  hashlib

from    static.py.main_functions    import *
from    static.py.db                import execute_sql_query
from    flask                       import Flask, render_template, redirect, flash, url_for, session, g

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return render_template('index.html',user=g.user)

@app.route('/upload', methods=['POST', 'GET'])
def upload():

    isError, data = validate_input()

    folderPath  = 'static/history/'
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

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
        'error1': 'OpenAI ouput error.'
        ,'error2': 'Exceeded google api limit.'
        ,'error3': 'No text was found.'
        ,'error4': 'No image provided.'
        ,'error5': 'No selected file.'
        ,'error6': 'Invalid file format.'
        ,'error7': 'Missing Consent to Privacy and Terms of Condition.'
    }

    if not isError:
        fileName        = f'card_{newId}.jpg'
        imagePath       = os.path.join(folderPath, fileName)
        request.files['image'].save(imagePath)
        
        restaurantName, address = get_meta_data(imagePath)

        data, recognizedText, response, tokens = process_image(imagePath, newId)
        isError         = isinstance(data, str) and data in errorMessage

        insertValue     = (newId, g.id, recognizedText, str(response), tokens, int(isError), None if not isError else errorMessage[data], os.path.join('history/', fileName), address, restaurantName),
  
    else:
        insertValue     = (newId, g.id, None, None, None, 1, errorMessage[data], None, None, None),


    insertStatement     = "INSERT INTO Query (ID, USER_ID, RECOGNIZED_TEXT, OPENAI_RESPONSE, USED_TOKENS, IS_ERROR, ERROR_MESSAGE, IMAGE, ADDRESS, RESTAURANT_NAME) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    execute_sql_query(insertStatement, insertValue, fetch=False)
    
    if isError:
        flash(errorMessage[data], 'error')
        return redirect(url_for('index'))

    insertStatement     = "INSERT INTO Result (QUERY_ID, DISH, TEXT, IMAGE) VALUES (%s, %s, %s, %s)"
    insertValue         = [(newId, item['line'], item['text'], item['image']) for item in data]
    execute_sql_query(insertStatement, insertValue, fetch=False)

    return render_template('index.html',data=data,user=g.user)

@app.route('/imprint')
def imprint():
    return render_template('imprint.html',user=g.user)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html',user=g.user)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if g.user:
        return redirect(url_for('index'))
    if request.method == 'POST':

        if request.form['action'] == 'login':
            result = execute_sql_query("SELECT ID, NAME, EMAIL, PASSWORD FROM User WHERE EMAIL = %s", (request.form['email'],))

            if result:
                if hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest() == result[0][3]:
                    session['user'] = result[0][1]
                    session['id']   = result[0][0]
                    return redirect(url_for('index'))
                else:
                    flash('Wrong password.', 'error')
                    return redirect(url_for('login'))
            
            else:
                flash('Email does not exist.', 'error')
                return redirect(url_for('login'))

        elif request.form['action'] == 'signup':

            result = execute_sql_query("SELECT 1 FROM User WHERE EMAIL = %s", (request.form['email'],))

            if not result:
                hashedPassword  = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
                insertStatement = "INSERT INTO User (EMAIL, PASSWORD, NAME, STATUS) VALUES (%s, %s, %s, %s)"
                insertValue     = (request.form['email'], hashedPassword, request.form['name'], 'open'),
                execute_sql_query(insertStatement, insertValue, fetch=False)

                flash('Successfully registered.', 'success')
            else:
                flash('Email already exists.', 'error')


    return render_template('login.html',user=g.user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/history')
def history():
    if not g.id:
        return redirect(url_for('index'))

    result = execute_sql_query("SELECT	ID, Dish, Q.IMAGE FROM Query Q INNER JOIN Result R ON Q.ID = R.QUERY_ID WHERE USER_ID = %s AND IS_ERROR = 0", (g.id,))

    numMenus = len(set(item[0] for item in result))

    return render_template('history.html', data=result, numMenus = numMenus,user=g.user)


@app.before_request
def before_request():
    g.user  = None
    g.id    = None
    if 'user' in session:
        g.user = session['user']
    if 'id' in session:
        g.id = session['id']

# start server
if __name__ == '__main__':
    app.run(debug=True)