#!/usr/bin/python
import psycopg2
from DB.config import config

create_commands = (
            '''
            CREATE TABLE branches (
                branch_id SERIAL PRIMARY KEY,
                branch_name VARCHAR(255) NOT NULL
            )
            ''',
            '''
            CREATE TABLE matches (
                match_id SERIAL PRIMARY KEY,
                face_original_id INTEGER NOT NULL,
                face_target_id INTEGER NOT NULL,
                similarity REAL NOT NULL
            )
            ''',
            '''
            CREATE TABLE cameras (
                camera_id SERIAL PRIMARY KEY,
                camera_name VARCHAR(255) NOT NULL
            )
            ''',
            '''
            CREATE TABLE user_transactions (
                transaction_id SERIAL PRIMARY KEY,
                match_id INTEGER NOT NULL,
                t1c_id VARCHAR(255) NOT NULL,
                time_in TIMESTAMP set default now(),
                time_out TIMESTAMP,
                branch_id INTEGER,
                FOREIGN KEY (branch_id)
                    REFERENCES branches (branch_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (match_id)
                    REFERENCES matches (match_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE faces (
                face_id SERIAL PRIMARY KEY,
                transaction_id INTEGER NOT NULL,
                face_recog_id VARCHAR(255) NOT NULL,
                image_path VARCHAR(255) NOT NULL,
                camera_id INTEGER,
                FOREIGN KEY (transaction_id)
                    REFERENCES user_transactions (transaction_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (camera_id)
                    REFERENCES cameras (camera_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
            ''',
        )
 
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        #create_table(conn)
        insert_data(conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
 

def create_table(conn):
    cur = conn.cursor()
    # create table one by one
    for command in create_commands:
        cur.execute(command)
    # close communication with the PostgreSQL database server
    cur.close()
    # commit the changes
    conn.commit()

def alter_table(conn):
    command = '''
    ALTER TABLE user_transactions
    ALTER time_in SET default now()
    '''
    cur = conn.cursor()
    cur.execute(command)
    cur.close()
    conn.commit()

insert_camera_command = '''
            INSERT INTO cameras(camera_name) VALUES(%s)
            RETURNING camera_id;
            '''
insert_transaction_command = '''
            INSERT INTO user_transactions(t1c_id, branch_id) VALUES(%s, %s)
            RETURNING transaction_id;
            '''
update_transaction_command = '''
            UPDATE user_transactions
            SET match_id = %s,
            time_out = now()
            WHERE transaction_id = %s
            '''
insert_match_command = '''
            INSERT INTO matches(face_original_id, face_target_id, similarity) VALUES(%s, %s, %s)
            RETURNING match_id;
            '''
insert_faces_command = '''
            INSERT INTO faces(transaction_id, face_recog_id, image_path, camera_id) VALUES(%s, %s, %s, %s)
            '''

insert_face_command = '''
            INSERT INTO faces(transaction_id, face_recog_id, image_path, camera_id) VALUES(%s, %s, %s, %s)
            RETURNING face_id
            '''
delete_transactions_command = '''
            DELETE from user_transactions
            '''

delete_faces_command = '''
            DELETE from faces
            '''

delete_matches_command = '''
            DELETE from matches
            '''
def insert_transaction_data(t1c, branch_id):
    conn = None
    transaction_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        cur.execute(insert_transaction_command, (t1c, branch_id))
        transaction_id = cur.fetchone()[0]
        print('transaction_id: ' + str(transaction_id))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return transaction_id

def update_transaction_data(match_id, transaction_id):
    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        print('update with match_id: ' + str(match_id))
        cur.execute(update_transaction_command, (match_id, transaction_id))
        updated_rows = cur.rowcount
        print('no. rows updated: ' + str(updated_rows))
        print('transaction_id: ' + str(transaction_id) + ' is updated')
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return transaction_id

def insert_match_data(face_original_id, face_target_id, similarity):
    conn = None
    match_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        cur.execute(insert_match_command, (face_original_id, face_target_id, similarity,))
        match_id = cur.fetchone()[0]
        print('match_id: ' + str(match_id))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return match_id

def insert_faces_data(transaction_id, face_images, camera_id):
    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        params = list(map(lambda x: (transaction_id, x.FaceId, x.ImagePath, camera_id,), face_images))
        print(params)
        cur.executemany(insert_faces_command, params)
        conn.commit()
        cur.close()
        print('inserted faces data')
        print('insert_faces_data tran_id: '+transaction_id)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def insert_face_data(transaction_id, face_image, camera_id):
    conn = None
    face_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        cur.execute(insert_face_command, (transaction_id, face_image.FaceId, face_image.ImagePath, camera_id,))
        face_id = cur.fetchone()[0]
        print('face_id: ' + str(face_id))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return face_id

select_face_id_command = '''
                        SELECT face_id 
                        FROM faces
                        WHERE face_recog_id = %s
'''
def get_face_id_from_face_rec(face_rec_id):
    conn = None
    face_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        cur.execute(select_face_id_command, (face_rec_id,))
        face_id = cur.fetchone()[0]
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return face_id

set_time_zone_command = '''
SET TIMEZONE TO %s;
'''
def set_time_zone(): 
    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        bangkok = 'Asia/Bangkok'
        cur.execute(set_time_zone_command, (bangkok,))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    set_time_zone()