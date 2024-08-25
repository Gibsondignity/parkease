import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("C:\\Users\\aiar8\\PycharmProjects\\Projects\\pythonProject1\\venv\\serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://parkease808802-default-rtdb.firebaseio.com/"
})

