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

def admin_user():
    return render_template('/admin/adminUser.html')

def admin_userprofile(): # 유저 프로필 화면 기능
    user_id = session.get('user_id')
    filter_query = {'user_id': user_id}
    document = collection_user.find_one(filter_query)
    user_nm = document['user_nm']
    user_point = int(document['user_point'])
    user_level = int(document['user_level'])
    if document['user_role'] == "admin" :
        user_role = "관리자"
    else :
        user_role = "일반 회원"
    user_review_cnt = document['user_review_cnt']

    filter_query = {'level_seq': user_level}
    #print(user_level)
    document = collection_level.find_one(filter_query)
    user_level_img = document['level_img']

    user_data = {
        'user_id' : user_id,
        'user_nm': user_nm,
        'user_point': user_point,
        'user_level': user_level,
        'user_role': user_role,
        'user_review_cnt': user_review_cnt,
        'user_level_img': user_level_img
    }
    #print(user_data)

    return render_template('/admin/adminUser_profile.html', user_data=user_data)

def admin_user2():
    user_id = session.get('user_id')
    reviews = collection_review.find({
        "review_status" : 10,
        "user_id" : user_id
    })

    if request.method == 'POST':
        #print(request.form['action'])
        review_con = request.form['reviewcontents']
        delete_num = int(40)
        #print(review_numb, review_scor, review_con)

        if request.form['action'] == 'delete5':
        # Delete 버튼이 클릭된 경우의 처리
            
            #review의 내용을 가지고 review도큐먼트 검색
            filter_query = {'review_contents': review_con}
            documentreview = collection_review.find_one(filter_query)
            cur_place_seq = int(documentreview['place_seq']) #해당 review의 place_seq저장
            cur_review_score = int(documentreview['review_score']) #해당 review의 현재 점수 저장

            #해당 place를 검색해서 현재 place의 review개수와 평균 점수 검색
            filter_query = {'place_seq': cur_place_seq}
            documentplace = collection_place.find_one(filter_query)
            cur_review_cnt = int(documentplace['place_review_count'])
            cur_review_avg = float(documentplace['place_score_avg'])
            #print(cur_place_seq, cur_review_cnt)

            #해당 place의 review개수와 review 평균 점수 재연산
            temp_total_score = float(cur_review_cnt*cur_review_avg)
            new_total_score = temp_total_score - cur_review_score
            new_review_cnt = cur_review_cnt - 1
            if(new_review_cnt == 0):
                new_review_avg = float(0.0)
            else:
                new_review_avg = float(new_total_score/new_review_cnt)
            #print(new_total_score, new_review_cnt, new_review_avg)

            #해당 review의 비활성화 업데이트 진행
            filter_query = {'review_contents': review_con}
            update_query = {'$set': {'review_status': delete_num}}
            result = collection_review.update_one(filter_query, update_query) #review콜렉션에서 업덷이트

            #해당 place에 새로운 리뷰 개수와 리뷰 평균값 업데이트
            filter_query = {'place_seq': cur_place_seq}
            update_query = {'$set': {'place_review_count': new_review_cnt, 'place_score_avg':new_review_avg}}
            result = collection_place.update_one(filter_query, update_query)

            #user의 리뷰개수 업데이트
            user_id = session.get('user_id') #현재의 user_id로 user의 현재 리뷰개수 저장
            filter_query = {'user_id': user_id}
            documentuser = collection_user.find_one(filter_query)
            cur_user_review_cnt = int(documentuser['user_review_cnt'])
            new_user_review_cnt = cur_user_review_cnt - 1 #새로 저장할 user의 리뷰개수
            filter_query = {'user_id': user_id}
            update_query = {'$set': {'user_review_cnt': new_user_review_cnt}}
            result = collection_user.update_one(filter_query, update_query) #user콜렉션에 업데이트
            return redirect(url_for('admin_user2'))


    return render_template('/admin/adminUser_dmr.html', reviews=reviews)

def admin_user3():
    if request.method == 'POST':
        if request.form['action'] == 'changepw':
            currentpw = request.form['curpassword']
            newpw = request.form['newpassword']

            user_id = session.get('user_id')
            filter_query = {'user_id': user_id}
            document = collection_user.find_one(filter_query)
            real_user_pw = document['user_pw']
            
            if not bcrypt.checkpw(currentpw.encode('utf-8'), real_user_pw.encode('utf-8')):
                # 문서를 찾지 못한 경우 처리할 내용 작성
                #print("문서를 찾지 못했습니다.")
                return redirect(url_for('admin_user3fail'))
            else:
                # 문서를 찾은 경우 처리할 내용 작성
                #print("문서를 찾았습니다.")
                #print(document)
                filter_query = {'user_pw': real_user_pw, 'user_id': user_id}
                #비밀번호로 조건 넣으면, 중복 비밀번호 변경
                pw_encrypted = bcrypt.hashpw(newpw.encode('utf-8'), bcrypt.gensalt())
                decode_pw = pw_encrypted.decode('utf-8')
                update_query = {'$set': {'user_pw': decode_pw}}
                result = collection_user.update_one(filter_query, update_query)
                #print(result.raw_result)
                return redirect(url_for('admin_user3suc'))

    return render_template('/admin/adminUser_cp.html')

def admin_user3suc():
    return render_template('/admin/adminUser_cpsuc.html')

def admin_user3fail():
    return render_template('/admin/adminUser_cpfail.html')