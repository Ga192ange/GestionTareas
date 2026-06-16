import os
import json
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore

firebase_creds = json.loads(
    os.environ.get("FIREBASE_CREDENTIALS")
)

cred = credentials.Certificate(firebase_creds)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()