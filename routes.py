from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from pymongo import MongoClient
import bcrypt
import functools
import datetime

app = Flask(__name__)
app.secret_key = '7684d16e188311e10cf5653c8f86ce22233f3ee591d5bed84cbab91db66b42ec'

# MongoDB 연결 설정
client = MongoClient('mongodb://localhost:27017/')
db = client.splatedb
collection_level = db.level
collection_place = db.place
collection_recommend = db.recommend
collection_review = db.review
collection_user = db.user

def check_login():
    if not session.get('user_id'):
        # 로그인 되지 않은 상태
        return jsonify(logged_in=False)
    else:
        # 로그인 상태인 경우
        collection_user = db.user
        id = session.get('user_id')
        user_data = collection_user.find_one({"user_id": id})
        user_nm = user_data['user_nm']
        user_level = user_data['user_level']
        user_point = user_data['user_point']
        user_review_cnt = user_data['user_review_cnt']
        user_role = user_data['user_role']
        return jsonify(logged_in=True, user_nm=user_nm, user_level=user_level, user_point=user_point, user_review_cnt=user_review_cnt, user_role = user_role)

#index
def index():
    all_food = collection_place.find({
        "place_category" : "food",
        "place_status" : 10
    })
    all_food.sort("place_score_avg", -1)
    data_food = list(all_food)

    all_cafe = collection_place.find({
        "place_category" : "cafe",
        "place_status" : 10
    })

    all_cafe.sort("place_score_avg", -1)
    data_cafe = list(all_cafe)

    return render_template('home.html', data_food=data_food, data_cafe = data_cafe)


def login():
    if request.method == "POST":
        id = request.form['user_id'].strip()
        pw = request.form['user_pw'].strip()

        # check the user from db
        user_data = collection_user.find_one({"user_id": id, "user_status": 10})

        # db에 id 존재
        if user_data:
            user_data_pw = user_data['user_pw']

            if bcrypt.checkpw(pw.encode('utf-8'), user_data_pw.encode('utf-8')):
                session["user_id"] = id
                return redirect(url_for('index'))
            else:
                flash('아이디 또는 비밀번호를 다시 확인해주세요.')
                return redirect(url_for('login'))
        else: # db에 아이디 없음
            flash('아이디 또는 비밀번호를 다시 확인해주세요.')
            return redirect(url_for('login'))

    return render_template('login.html')

def signup():
    if request.method == "POST":
        name = request.form['user_nm'].strip()
        id = request.form['user_id'].strip()
        pw = request.form['user_pw'].strip()

        if collection_user.find_one({'user_id': id, 'user_status' : 10}):
            #활성화 확인
            flash('중복된 아이디가 있습니다. 다른 아이디를 이용해주세요.')
            return redirect(url_for('signup'))
    
        pw_encrypted = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        decode_pw = pw_encrypted.decode('utf-8')
        
        seq_max_document = collection_user.find().sort('user_seq', -1).limit(1) # seq를 내림차순으로 정렬
        seq_max_value = int(seq_max_document[0]['user_seq']) # user_seq 값만 저장

        result = collection_user.insert_one({
            "user_seq": seq_max_value + 1,
            "user_id": id,
            "user_pw": decode_pw,
            "user_nm": name,
            "user_point": 0,
            "user_level": 1,
            "user_role": "user",
            "user_status": 10,
            "user_review_cnt": 0
        })

        if result.inserted_id:
            flash('회원가입에 성공했습니다! 가입한 아이디로 로그인해주세요.')
            return redirect(url_for('login'))
        
        return redirect(url_for('index'))

    return render_template('signup.html')

def logout():
    session.clear()
    return redirect(url_for('index'))