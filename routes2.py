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

def food_list():
    #데이터 조회
    data=collection_place.find({
        "place_category":"food",
        "place_status" : 10
    })
    data_list=list(data)
    list_nm="식당"
    #템플릿 렌더링 및 데이터 전달
    return render_template('/place/placeList.html',data_list=data_list,list_nm=list_nm)

def food_detail(seq):
    data = collection_place.find_one({"place_seq" : seq, "place_status" : 10})
    reviews = collection_review.find({"place_seq": seq, "review_status" : 10})
    reviews.sort("datereview_created_date",-1)
    review_list = list(reviews)
    levels = collection_level.find()
    level_list = list(levels)
    score_value = data.get("place_score_avg", 0.0)
    limited_score_value = round(score_value, 2)
    data["place_score_avg"] = limited_score_value

    if request.method=='POST':
           if request.form['action'] == 'addreview':
                #입력받은 별점과 리뷰내용 저장
                review_score = int(request.form['reviewscore'])
                review_contents = request.form['review_content_area']

                #리뷰를 입력한 user의 document 검색
                user_id = session.get('user_id')
                filter_query = {'user_id': user_id}
                documentuser = collection_user.find_one(filter_query)

                #해당 user의 현재 review개수, 현재 level, 현재 point를 검색
                #앞으로 저장할 새로운 review개수, 새로운 point 저장
                cur_user_review_cnt = documentuser['user_review_cnt']
                new_user_review_cnt = cur_user_review_cnt + 1
                cur_user_level = int(documentuser['user_level'])
                cur_user_point = int(documentuser['user_point'])
                new_user_point = int(cur_user_point) + 50
                
                #현재 level정보로 현재 level의 최대 포인트 값 검색
                filter_query = {'level_seq': cur_user_level}
                leveldocument = collection_level.find_one(filter_query)
                level_condition = leveldocument['level_max']

                #user의 새로운 point가 최대 포인트를 초과했다면 user의 level 새로 업데이트 진행
                if (level_condition < new_user_point):
                    filter_query = {'user_id': user_id}
                    new_user_level = cur_user_level + 1
                    update_query = {'$set': {'user_level': new_user_level}}
                    result = collection_user.update_one(filter_query, update_query)

                #user의 새로운 review개수, 새로운 point값 update
                filter_query = {'user_id': user_id}
                update_query = {'$set': {'user_point': new_user_point, 'user_review_cnt':new_user_review_cnt}}
                result = collection_user.update_one(filter_query, update_query)

                #새로운 review를 insert하기 위한 초기값들 설정
                filter_query = {'user_id': user_id}
                documentuser = collection_user.find_one(filter_query) #해당 user의 도큐먼트 검색
                cur_user_level = int(documentuser['user_level'])
                user_nm = documentuser['user_nm']
                place_seq = int(seq)
                review_status = int(10)

                #현재의 시간 저장, 이 때 string자료형인 datereview_created_date는 몽고DB에 저장시 자동으로 Date자료형으로 저장될 예정
                #current_time=str(datetime.datetime.now())
                current_time = datetime.datetime.now()
                updated_time = current_time + datetime.timedelta(hours=9)
                updated_time_str = updated_time.strftime("%Y-%m-%d %H:%M:%S")
                current_time=updated_time_str[0:19]
                datereview_created_date = current_time

                #review_seq 검색
                seq_max_document = collection_review.find().sort('review_seq', -1).limit(1) # seq를 내림차순으로 정렬
                seq_max_value = int(seq_max_document[0]['review_seq']) # review_seq 값만 저장

                #review콜렉션에 insert
                result = collection_review.insert_one({
                    'review_seq' : seq_max_value + 1,
                    'user_id' : user_id,
                    'user_level' : cur_user_level,
                    'user_nm' : user_nm,
                    'place_seq' : place_seq,
                    'datereview_created_date' : datereview_created_date,
                    'review_contents' : review_contents,
                    'review_score' : review_score,
                    'review_status' : review_status
                })

                filter_query = {'place_seq': place_seq}
                documentplace = collection_place.find_one(filter_query)
                cur_review_cnt = int(documentplace['place_review_count'])
                cur_review_avg = float(documentplace['place_score_avg'])
                total_score = float(cur_review_cnt * cur_review_avg) + review_score
                new_review_cnt = cur_review_cnt + 1
                new_review_avg = float(total_score/new_review_cnt)

                filter_query = {'place_seq': place_seq}
                update_query = {'$set': {'place_review_count': new_review_cnt, 'place_score_avg':new_review_avg}}
                result = collection_place.update_one(filter_query, update_query)

                return redirect(url_for('food_detail', seq=seq))

    if session.get('user_id'):
        return render_template('/place/placeDetail.html', data=data, review_list=review_list, level_list=level_list)
    else:
        return render_template('/place/placeDetail_nologin.html', data=data, review_list=review_list, level_list=level_list)

def cafe_list():
    #데이터 조회
    data=collection_place.find({
        "place_category":"cafe",
        "place_status" : 10
    })
    data_list=list(data)
    list_nm="카페"
    #템플릿 렌더링 및 데이터 전달
    return render_template('/place/placeList.html',data_list=data_list,list_nm=list_nm)

def cafe_detail(seq):
    data = collection_place.find_one({"place_seq" : seq, "place_status" : 10})
    reviews = collection_review.find({"place_seq": seq, "review_status" : 10})
    reviews.sort("datereview_created_date",-1)
    review_list = list(reviews)
    levels = collection_level.find()
    level_list = list(levels)
    score_value = data.get("place_score_avg", 0.0)
    limited_score_value = round(score_value, 2)
    data["place_score_avg"] = limited_score_value

    if request.method=='POST':
           if request.form['action'] == 'addreview':
                review_score = int(request.form['reviewscore'])
                #print(review_score)
                review_contents = request.form['review_content_area']
                #print(review_contents)

                user_id = session.get('user_id')
                filter_query = {'user_id': user_id}
                documentuser = collection_user.find_one(filter_query)
                cur_user_review_cnt = documentuser['user_review_cnt']
                new_user_review_cnt = cur_user_review_cnt + 1
                cur_user_level = int(documentuser['user_level'])
                cur_user_point = int(documentuser['user_point'])
                new_user_point = int(cur_user_point) + 50
                
                filter_query = {'level_seq': cur_user_level}
                leveldocument = collection_level.find_one(filter_query)
                level_condition = leveldocument['level_max']
                if (level_condition < new_user_point):
                    filter_query = {'user_id': user_id}
                    new_user_level = cur_user_level + 1
                    update_query = {'$set': {'user_level': new_user_level}}
                    result = collection_user.update_one(filter_query, update_query)

                filter_query = {'user_id': user_id}
                update_query = {'$set': {'user_point': new_user_point, 'user_review_cnt':new_user_review_cnt}}
                result = collection_user.update_one(filter_query, update_query)

                filter_query = {'user_id': user_id}
                documentuser = collection_user.find_one(filter_query)
                cur_user_level = int(documentuser['user_level'])
                user_nm = documentuser['user_nm']
                place_seq = int(seq)
                review_status = int(10)

                current_time=str(datetime.datetime.now())
                current_time=current_time[0:19]
                datereview_created_date = current_time

                seq_max_document = collection_review.find().sort('review_seq', -1).limit(1) # seq를 내림차순으로 정렬
                seq_max_value = int(seq_max_document[0]['review_seq']) # review_seq 값만 저장

                result = collection_review.insert_one({
                    'review_seq' : seq_max_value + 1,
                    'user_id' : user_id,
                    'user_level' : cur_user_level,
                    'user_nm' : user_nm,
                    'place_seq' : place_seq,
                    'datereview_created_date' : datereview_created_date,
                    'review_contents' : review_contents,
                    'review_score' : review_score,
                    'review_status' : review_status
                })

                filter_query = {'place_seq': place_seq}
                documentplace = collection_place.find_one(filter_query)
                cur_review_cnt = int(documentplace['place_review_count'])
                cur_review_avg = float(documentplace['place_score_avg'])
                total_score = float(cur_review_cnt * cur_review_avg) + review_score
                new_review_cnt = cur_review_cnt + 1
                new_review_avg = float(total_score/new_review_cnt)

                filter_query = {'place_seq': place_seq}
                update_query = {'$set': {'place_review_count': new_review_cnt, 'place_score_avg':new_review_avg}}
                result = collection_place.update_one(filter_query, update_query)

                return redirect(url_for('food_detail', seq=seq))

    if session.get('user_id'):
        return render_template('/place/placeDetail.html', data=data, review_list=review_list, level_list=level_list)
    else:
        return render_template('/place/placeDetail_nologin.html', data=data, review_list=review_list, level_list=level_list)

def place_recommend():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        place_name = request.form['place_name_input']
        place_type = request.form['inlineRadioOptions']
        place_info = request.form['place_info_area']
        user_id = session.get('user_id')

        # 데이터 MongoDB에 저장
        data = {
            'rec_pname': place_name,
            'rec_pcategory': place_type,
            'rec_pinfo': place_info,
            'rec_status' : 10
        }
        collection_recommend.insert_one(data)

        #user_id로 user콜렉션에서 user포인트와 레벨 검색
        filter_query = {'user_id': user_id}
        userdocument = collection_user.find_one(filter_query)
        current_user_point = userdocument['user_point']
        current_user_level = userdocument['user_level']
        new_user_point = int(current_user_point) + 100

        #포인트 100점을 추가하여, user 도큐먼트에 업데이트
        filter_query = {'user_id': user_id}
        update_query = {'$set': {'user_point': new_user_point}}
        result = collection_user.update_one(filter_query, update_query)

        #level_seq에 맞는 level의 최대 point값 검색
        filter_query = {'level_seq': current_user_level}
        leveldocument = collection_level.find_one(filter_query)
        level_condition = leveldocument['level_max']

        #만약에 user의 현재 포인트가 최대 포인트값을 초과했다면, user의 level 업데이트
        if (level_condition < new_user_point):
            filter_query = {'user_id': user_id}
            new_user_level = current_user_level + 1
            update_query = {'$set': {'user_level': new_user_level}}
            result = collection_user.update_one(filter_query, update_query)
        
        return redirect(url_for('place_recommend2'))

    return render_template('/place/placeRecommend.html')


def place_recommend2():
    return render_template('/place/placeRecommendsuc.html')