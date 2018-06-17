import time
from Rekognition.rekognition import CG_Rekognition
from os import listdir
from Logger.log import LocalLogger

class ImageHandler:
    rekog=CG_Rekognition()
    logger=LocalLogger()

    def searchImages(self):
        file_prefix='images/test0'
        collectionId = 'ticface'
        for i in range(1,6):
            filename = file_prefix+str(i)+'.jpg'
            self.rekog.put(filename)
            response = self.rekog.search_faces_by_image(collectionId, filename)
            self.rekog.delete(filename)
            '''
            for faceMatch in response['FaceMatches']:
                print('=== Similarity: '+ str(faceMatch['Similarity']) + ' ===')
                print('=== FaceId: '+ faceMatch['Face']['FaceId'] + ' ===')
                print('-------------------------------------------------')
                '''
    def get_all_filename(self, dir_path):
        return list(map(lambda x: dir_path+'/'+x, listdir(dir_path)))

    def add_index_faces(self, collection_id, filenames):
        for filename in filenames:
            if not filename.endswith('.jpg'):
                continue
            with open(filename, 'rb') as source_image:
                image = source_image.read()
            if image:
                self.rekog.put(filename)
                self.rekog.index_faces(
                    collection_id=collection_id,
                    data=image)
                self.rekog.delete(filename)
        self.logger.log('add_index_faces is done')

    def searchImage(self):
        collectionId = 'ticface'
        filename = 'images/test01.jpg'
        #self.rekog.put(filename)
        start = time.time()
        response = self.rekog.search_faces_by_bytes(collectionId, filename)
        stop = time.time()
        #self.rekog.delete(filename)
        print (stop-start)
        
        for faceMatch in response['FaceMatches']:
            print('=== Similarity: '+ str(faceMatch['Similarity']) + ' ===')
            print('=== FaceId: '+ faceMatch['Face']['FaceId'] + ' ===')
            print('-------------------------------------------------')
            

    def delete_faces(self, _collection_id):
        face_ids = self.get_faces(_collection_id)
        response=self.rekog.delete_faces(_collection_id, face_ids)
        return response

    def get_faces(self, _collection_id):
        response=self.rekog.list_faces(_collection_id)
        return list(map(lambda x: x['FaceId'], response['Faces']))

    def initialAddFace(self, _collection_id, _filename):
        response=self.rekog.index_faces(_collection_id, _filename)
        

