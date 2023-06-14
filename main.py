import numpy as np
from PIL import Image
import tensorflow as tf
import os
import h5py
from flask import Flask, request, jsonify, send_file
from google.cloud import storage
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
import urllib.request
import datetime
from firebase_admin import db
from firebase_admin import firestore
import pytz



load_dotenv()

# Get Firebase configuration from environment variables
firebase_config = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "projectId": os.getenv("PROJECT_ID"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    "appId": os.getenv("APP_ID")
}

# Initialize Firebase SDK
cred = credentials.Certificate('serviceAccount.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
bucket_name = "skinsight-skin-tone" 


def predict_image_class(image_path, model_h5_path, class_mapping):
    # Load and preprocess the input image
    image = Image.open(image_path)
    image = image.resize((224, 224))  # Resize the image to match the expected input shape of the model
    image = np.array(image) / 255.0  # Normalize the image pixels between 0 and 1
    image = np.expand_dims(image, axis=0)  # Add batch dimension

    # Verify the model.h5 file exists
    if not os.path.isfile(model_h5_path):
        print("Model file does not exist:", model_h5_path)
        return None

    # Check the contents of the model.h5 file
    with h5py.File(model_h5_path, "r") as f:
        if "model_config" not in f.attrs.keys():
            print("Invalid model.h5 file:", model_h5_path)
            return None

    # Load the trained model
    model = tf.keras.models.load_model(model_h5_path)

    # Perform inference
    predictions = model.predict(image)
    predicted_class_index = np.argmax(predictions)
    predicted_class = list(class_mapping.keys())[list(class_mapping.values()).index(predicted_class_index)]

    return predicted_class

def run_image_classification(image_url, model_h5_path):
    # Download the image from the provided URL
    image_path = 'temp_image.jpg'
    urllib.request.urlretrieve(image_url, image_path)

    # Define the class mapping
    class_mapping =  {"Monk 1": 0, "Monk 2": 1, "Monk 3": 2,
                     "Monk 4": 3, "Monk 5": 4, "Monk 6": 5, "Monk 7": 6
                     , "Monk 8": 7, "Monk 9": 8, "Monk 10": 9
                     }

    # Call the predict_image_class function
    predicted_class = predict_image_class(image_path, model_h5_path, class_mapping)

    # Remove the temporary image file
    os.remove(image_path)

    return predicted_class
        

def upload_file_to_bucket(bucket_name, file_name, file):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    blob.upload_from_file(file, content_type='application/octet-stream')

    # Make the uploaded file publicly accessible
    blob.make_public()

    public_url = blob.public_url

    return public_url

@app.route('/detect-tone/<uid>', methods=['POST'])
def upload_skin_picture(uid):
    try:
        if len(request.files) == 0:
            response = jsonify({
                'status': 'Failed',
                'message': 'Tidak ada file yang ditambahkan'
            })
            response.status_code = 400
            return response

        file = next(iter(request.files.values()))
        file_name = file.filename

        public_url = upload_file_to_bucket(bucket_name, file_name, file)

        predicted_class = run_image_classification(public_url, 'SkinTone.h5')

        if predicted_class == "Monk 1":
            description = "Skintone ini sangat cerah dengan warna kulit yang sangat terang. Biasanya memiliki nuansa kuning atau merah muda yang sangat pucat."
            recommendation = "Untuk skintone sangat terang ini, pilihlah foundation dengan nuansa kuning lembut atau merah muda yang pucat. Lipstik dengan warna nude, peach muda, atau merah muda pucat akan memberikan tampilan yang segar."
        elif predicted_class == "Monk 2":
            description = "Skintone ini juga tergolong terang, tetapi sedikit lebih gelap dibandingkan Monk 1. Warna kulitnya mungkin memiliki sedikit lebih banyak pigmen kuning atau merah muda."
            recommendation = "Untuk skintone terang ini, gunakan foundation dengan nuansa kuning atau merah muda yang sedikit lebih hangat. Lipstik dengan warna nude lembut, peach, atau pink pastel akan melengkapi penampilan."
        elif predicted_class == "Monk 3":
            description = " Skintone ini memiliki warna kulit yang cerah, tetapi sedikit lebih terang dibandingkan Monk 2. Kulitnya bisa memiliki sentuhan kuning, peach, atau merah muda yang lebih jelas."
            recommendation = "Foundation dengan nuansa kuning hangat atau peach akan cocok untuk skintone ini. Anda dapat mencoba lipstik dengan warna nude hangat, pink muda, atau coral yang cerah."
        elif predicted_class == "Monk 4":
            description = "Skintone ini memiliki warna kulit yang lebih tengah-tengah. Biasanya memiliki sentuhan kuning atau peach yang sedikit lebih jelas, tetapi masih tergolong terang."
            recommendation = " Skintone ini cocok dengan foundation berwarna kuning kecokelatan atau peach. Lipstik dengan warna nude hangat, coral, atau berry akan memberikan sentuhan yang indah."
        elif predicted_class == "Monk 5":
            description = "Skintone ini merupakan skintone netral atau kulit rata-rata. Biasanya tidak terlalu terang atau terlalu gelap, dengan sentuhan kuning atau peach yang seimbang."
            recommendation = "Untuk skintone netral ini, pilihlah foundation dengan nuansa kuning atau peach yang seimbang. Lipstik dengan warna nude universal, merah klasik, atau pink yang cerah akan terlihat cantik."
        elif predicted_class == "Monk 6":
            description = "Skintone ini tergolong medium, dengan warna kulit yang lebih gelap dibandingkan Monk 5. Mungkin memiliki sentuhan kuning kecokelatan, peach, atau merah muda."
            recommendation = "Foundation dengan nuansa kuning kecokelatan atau peach akan cocok dengan skintone ini. Anda dapat mencoba lipstik dengan warna nude yang lebih dalam, merah anggur, atau berry yang kaya."
        elif predicted_class == "Monk 7":
            description = "Skintone ini memiliki warna kulit yang sedikit lebih gelap daripada Monk 6. Biasanya memiliki sentuhan kuning kecokelatan atau peach yang lebih kaya."
            recommendation = "Pilih foundation dengan nuansa kuning kecokelatan yang dalam atau peach yang kaya. Lipstik dengan warna nude kecokelatan, cokelat merah, atau plum akan memberikan tampilan yang elegan."
        elif predicted_class == "Monk 8":
            description = "Skintone ini tergolong gelap dengan warna kulit yang cukup pekat. Kulitnya mungkin memiliki sentuhan kuning keemasan, kuning kecokelatan, atau peach yang dalam."
            recommendation = " Skintone ini cocok dengan foundation berwarna kuning keemasan atau peach yang dalam. Lipstik dengan warna nude kecokelatan, cokelat kemerahan, atau burgundy akan memberikan tampilan dramatis yang indah."
        elif predicted_class == "Monk 9":
            description = "Monk 9: Skintone ini sangat gelap dengan warna kulit yang sangat pekat. Biasanya memiliki sentuhan kuning kecokelatan yang dalam atau merah keunguan."
            recommendation = "Untuk skintone sangat gelap ini, pilihlah foundation dengan nuansa kuning kecokelatan yang dalam atau merah keunguan. Lipstik dengan warna nude kecokelatan, maroon, atau merah anggur yang dalam akan terlihat menakjubkan."
        elif predicted_class == "Monk 10":
            description = "Skintone ini merupakan skintone yang sangat gelap. Kulitnya mungkin memiliki sentuhan merah keunguan yang dalam atau keabu-abuan yang dalam."
            recommendation = "Foundation dengan nuansa merah keunguan atau abu-abu dalam akan cocok untuk skintone ini. Lipstik dengan warna nude keabu-abuan, merah tua, atau cokelat akan menambahkan sentuhan misterius pada penampilan Anda."

        # Adjust timestamp to client's time zone
        client_timezone = pytz.timezone('Asia/Jakarta')  # Replace with the appropriate time zone
        client_timestamp = datetime.datetime.now(client_timezone)

        doc_ref = db.collection('users').document(uid)
        doc_ref.update({
            'history': firestore.ArrayUnion([{
                'type' : 'Skin Tone Identification',
                'datetime': client_timestamp,
                'predicted_class': predicted_class,
                'detection_img': public_url,
                'description' : description,
                'recommendation' : recommendation
            }])
        })

        response = jsonify({
            'type' : 'Skin Tone Identification',
            'status': 'Success',
            'message': 'Deteksi Skin Tone berhasil',
            'detection_img': public_url,
            'class' : predicted_class,
            'description' : description,
            'recommendation' : recommendation
        })
        response.status_code = 200
        return response

    except Exception as error:
        print(error) 

        response = jsonify({
            'status': 'Failed',
            'message': 'An internal server error occurred',
            'error': str(error)
        })
        response.status_code = 500
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


