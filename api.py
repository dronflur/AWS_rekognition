from flask import Flask, request, jsonify
from Logger.log import LocalLogger
from Rekognition.rekognition import CG_Rekognition
from DB.postgresRepo import *
from random import randint
from Builder.filenameBuilder import InOut
import time

from Builder.filenameBuilder import FileNameBuilder

app = Flask(__name__)

logger = LocalLogger()
rekog = CG_Rekognition()
COLLECTION_ID = 'ticface'
user_data = {}

filenameBuilder = FileNameBuilder()

class ImageRequest:
    Bytes = None
    Filename = None

class UserData:
    T1C = None
    TransactionId = None
    FaceIds = None

class FaceImage:
    FaceId = None
    ImagePath = None

@app.route("/faceDetection", methods=['POST'])
def detect_faces():
    imageRequest = set_image_request(request.files, request.form)
    
    if imageRequest.Bytes or imageRequest.Filename:
        response = rekog.detect_faces(Filename=imageRequest.Filename, Bytes=imageRequest.Bytes)
        return jsonify(response)

    return jsonify("Require specific parameters"), 422


@app.route("/faceMatching", methods=['POST'])
def search_faces_by_image():
    imageRequest = set_image_request(request.files, request.form)
    filename = request.files['image'].filename
    result = {'success': True}

    try:
        if imageRequest.Bytes or imageRequest.Filename:
            start = time.time()
            search_response = rekog.search_faces_by_image(Filename=imageRequest.Filename, Bytes=imageRequest.Bytes, Collection_id=COLLECTION_ID)
            stop = time.time()
            first_face_match = search_response['FaceMatches'][0]
            similarity = first_face_match['Similarity']
            print('Similarity: ' + str(similarity))
            face_id = first_face_match['Face']['FaceId']
            result['face_id'] = face_id
            print('cal time: ' + str(stop-start))
            if search_response and 'FaceMatches' in search_response and len(search_response['FaceMatches']) > 0:
                face_original_id = get_face_id_from_face_rec(face_id)

                if face_id in user_data and user_data[face_id]:
                    transaction_id = user_data[face_id].TransactionId
                    t1c = user_data[face_id].T1C
                    filename = filename = filenameBuilder.getFileName(T1C = t1c, inout=InOut.Out)
                    face_image = FaceImage()
                    face_image.FaceId = ''
                    face_image.ImagePath = rekog.put(Bytes=imageRequest.Bytes, Filename=filename)
                    print("start face_target_id ===========")
                    face_target_id = insert_face_data(transaction_id, face_image, 2)
                    print("end face_target_id ===========")
                    match_id = insert_match_data(face_original_id, face_target_id, similarity)
                    print('user_data: ' + str(transaction_id))
                    update_transaction_data(match_id, transaction_id)

                    print('T1C: ' + user_data[face_id].T1C)
                    for faceId in user_data[face_id].FaceIds:
                        del user_data[faceId]
                    print(user_data)
                    result['t1c'] = user_data[face_id].T1C
                else:
                    result['success'] = False
    except Exception as inst:
        result['success'] = False
        result['exception'] = inst
        
    return jsonify(result)


@app.route("/faceIndex", methods=['POST'])
def index_faces():
    result = {'success': True}
    imageRequests = list(map(lambda x: encoded_file(x), request.files.getlist("images")))
    t1c = request.form['t1c']

    if len(imageRequests) <= 0 or len(t1c) <= 0:
        result['success'] = False
        result['exception'] = 'Require specific parameters'
        return jsonify(result)
    
    face_images = []
    face_id = None
    for imageRequest in imageRequests:
        start = time.time()
        index_response = rekog.index_faces(Bytes=imageRequest, Collection_id=COLLECTION_ID)
        stop = time.time()
        print('cal time: ' + str(stop-start))
        if index_response and 'FaceRecords' in index_response:
            face_image = FaceImage()
            face_image.FaceId = index_response['FaceRecords'][0]['Face']['FaceId']
            filename = filenameBuilder.getFileName(T1C = t1c)
            face_image.ImagePath = rekog.put(Bytes=imageRequest, Filename=filename)
            face_images.append(face_image)
            face_id = face_image.FaceId
            print('faceId: ' + str(face_id))
            user_data[face_id] = UserData()
            user_data[face_id].T1C = t1c

    face_ids = map(lambda x: x.FaceId, face_images)
    tran_id = insert_transaction_data(t1c, 2)
    temp_face_ids = []
    for face_id_data in face_ids:
        user_data[face_id_data].TransactionId = tran_id
        user_data[face_id_data].FaceIds = face_ids
        temp_face_ids.append(face_id_data)
    insert_faces_data(user_data[face_id].TransactionId, face_images, 2)
    result['transaction_id'] = tran_id
    result['face_ids'] = temp_face_ids
    result['t1c'] = t1c

    return jsonify(result)
    


@app.route("/")
def hello():
    return "Hello"

def encoded_file(file):
    if file:
        return file.read()
    return None

def set_image_request(files, form):
    imageRequest = ImageRequest()
    if 'image' in files and files['image']:
        image = request.files['image']
        imageRequest.Bytes = encoded_file(image)

    if 'filename' in form and form['filename']:
        imageRequest.Filename = request.form['filename']

    return imageRequest



'''
Base64 -> 3 pics -> str
T1c no. -> str



Temp, Main -> stored 3 pics and map with T1c no

'''