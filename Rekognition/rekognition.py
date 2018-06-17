import boto3
from Logger.log import LocalLogger
from random import randint
from enum import Enum

class InOut(Enum):
    In = 0
    Out = 1

class CG_Rekognition:

    bucket_name='cdl.cto.rekog'
    client=boto3.client('rekognition','ap-northeast-1')
    client_s3=boto3.client('s3')
    logger = LocalLogger()
    folder_name = 'customer.face/'

    def __init__(self):
        print ('initialted')

    def put(self, Filename=None, Bytes=None):
        data = Bytes
        filename = self.folder_name + Filename
        self.client_s3.put_object(
            Bucket=self.bucket_name, 
            Body=data, 
            Key=filename)
        self.logger.log ('saved ' + filename)
        return filename

    def delete(self, filename):
        _filename = filename
        self.client_s3.delete_object(Bucket=self.bucket_name, Key=_filename)
        self.logger.log ('deleted ' + _filename)
    
    def detect_labels(self, _filename):
        print(_filename)
        response = self.client.detect_labels(Image={'S3Object':{'Bucket':self.bucket_name,'Name':_filename}})
        print('Detected labels for ' + _filename)    
        for label in response['Labels']:
            print (label['Name'] + ' : ' + str(label['Confidence']))

    def compare_faces(self, _filename):
        response = self.client.compare_faces(
            TargetImage=
            {
                'S3Object':
                {
                    'Bucket':self.bucket_name,
                    'Name':_filename
                }
            },
            SourceImage= 
            {
                'S3Object':
                {
                    'Bucket':self.bucket_name,
                    'Name':'input.jpg'
                }
            }
        ) 
        # TODO Add null prevention
        self.logger.log(response['FaceMatches'][0]['Similarity'])
        return response

    def compare_images(self, source, target):
        with open(source, 'rb') as source_image:
            source_bytes = source_image.read()

        with open(target, 'rb') as target_image:
            target_bytes = target_image.read()

        response = self.client.compare_faces(
                        SourceImage={ 'Bytes': source_bytes },
                        TargetImage={ 'Bytes': target_bytes },
                        SimilarityThreshold=20.0
        )
        return response

    def create_collection(self, _collection_id):
        self.client.create_collection(CollectionId=_collection_id)
        print('collection is created')

    def index_faces(self, Collection_id, Filename=None, Bytes=None):
        response = self.client.index_faces(
            CollectionId=Collection_id,
            Image=self.get_image_object(Filename=Filename, Bytes=Bytes),
        )
        print('index faces is done')
        return response

    def search_faces_by_image(self, Collection_id, Filename=None, Bytes=None):
        response = self.client.search_faces_by_image(
            CollectionId=Collection_id,
            Image=self.get_image_object(Filename=Filename, Bytes=Bytes),
            FaceMatchThreshold=20.0
        )
        self.logger.log('***** search_faces_by_image is done *****')
        return response

    def search_faces_by_bytes(self, _collection_id, _filename):
        with open(_filename, 'rb') as source_image:
            data = source_image.read()
        response = self.client.search_faces_by_image(
            CollectionId=_collection_id,
            Image={ 'Bytes': data },
            FaceMatchThreshold=20.0
        )
        self.logger.log('***** search_faces_by_bytes is done *****')
        return response

    def search_faces(self, _collection_id, _face_id):
        response = self.client.search_faces(
            CollectionId=_collection_id,
            FaceId=_face_id
        )
        self.logger.log('search faces is done')
        return response

    def list_faces(self, _collection_id):
        response = self.client.list_faces(CollectionId=_collection_id)
        print('***** list_faces is done *****')
        return response

    def delete_faces(self, _collection_id, _face_ids):
        response = self.client.delete_faces(
            CollectionId=_collection_id,
            FaceIds=_face_ids
        )
        self.logger.log('***** delete_faces is done *****')
        return response

    def detect_faces(self, Filename=None, Bytes=None):
        response = self.client.detect_faces(
            Image=self.get_image_object(Filename=Filename, Bytes=Bytes),
            Attributes=['ALL']
        )
        self.logger.log('***** detect_faces is done *****')
        return response

    def index_faces_2(self, collection_id, filename):
        with open(filename, 'rb') as source_image:
            data = source_image.read()
        response = self.client.index_faces(
            Image=self.get_image_object(Bytes=data),
            CollectionId=collection_id,
        )
        self.logger.log('***** detect_faces is done *****')
        return response

    def get_image_object(self, Filename=None, Bytes=None):
        if Filename:
            return {
                'S3Object': {
                    'Bucket': self.bucket_name,
                    'Name': Filename
                }}
        if Bytes:
            return { 'Bytes': Bytes }


