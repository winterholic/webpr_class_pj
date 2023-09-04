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

def admin_post():
    
    user_id = session.get('user_id')
    #print(user_id)
    filter_query = {'user_id': user_id}
    document = collection_user.find_one(filter_query)
    user_role = document['user_role']

    return render_template('/admin/adminPost.html')

def admin_post2():
    places = collection_place.find({ #검색은 활성화된 도큐먼트에만 시행
        "place_status" : 10
    })

    if request.method == 'POST':
        #print(request.form['action'])
        place_numb = int(request.form['placesequence']) # string으로 오기때문에, 정수로 변환
        place_name = request.form['placename']
        place_cate = request.form['placecategory']
        place_lonum = int(request.form['placelocnum'])
        delete_num = int(40)
        #print("내용들 :", place_numb, place_name, place_cate, place_lonum)

        if request.form['action'] == 'update':
        # Update 버튼이 클릭된 경우의 처리

            # 데이터 MongoDB에 업데이트, 기본적으로 다른값들에 영향을 미치는 값들은 아니다.
            filter_query = {'place_seq': place_numb}
            update_query = {'$set': {'place_nm': place_name, 'place_category': place_cate, 'place_locate_num': place_lonum}}
            result = collection_place.update_one(filter_query, update_query) #플레이스 콜렉션의 업데이트
            #print(result.modified_count)

            return redirect(url_for('admin_post2'))

        elif request.form['action'] == 'delete':
        # Delete 버튼이 클릭된 경우의 처리

            # 해당 place비활성화 처리
            filter_query = {"place_seq": place_numb}
            update_query = {'$set': {'place_status': delete_num}}
            result = collection_place.update_one(filter_query, update_query) #플레이스 콜렉션의 업데이트
            
            #해당 place의 번호를 가진 모든 활성화된 review 검색
            filter_query = {'place_seq': place_numb, 'review_status' : 10}
            cursor = collection_review.find(filter_query)
            #모든 리뷰를 확인하면서, 비활성화처리
            for document in cursor:
                review_seq = int(document['review_seq'])
                filter_query = {'review_seq' : review_seq}
                update_query = {'$set': {'review_status': delete_num}}
                result = collection_review.update_one(filter_query, update_query) #리뷰콜렉션의 업데이트
                #그 과정에서 그 리뷰를 작성한 유저의 review개수 감소
                user_id = document['user_id'] #user_id는 숫자값이 아니라 괜찮다
                filter_query = {'user_id' : user_id}
                documentuser = collection_user.find_one(filter_query)
                cur_user_review_cnt = int(documentuser['user_review_cnt']) # document가 아니라 documentuser에서 가져와야한다.
                new_user_review_cnt = cur_user_review_cnt - 1
                filter_query = {'user_id' : user_id}
                update_query = {'$set': {'user_review_cnt': new_user_review_cnt}}
                result = collection_user.update_one(filter_query, update_query)            

            return redirect(url_for('admin_post2')) #현재 url 리다이렉트
        
    return render_template('/admin/adminPost_pm.html', places=places)      

    

def admin_post3():
    reviews = collection_review.find({  #검색은 활성화된 도큐먼트에만 시행
        "review_status" : 10
    })

    if request.method == 'POST':
        #print(request.form['action'])
        review_numb = int(request.form['reviewsequence']) # string으로 오기때문에, 정수로 변환
        review_scor = int(request.form['reviewscore']) # string으로 오기때문에, 정수로 변환
        review_con = request.form['reviewcontents']
        delete_num = int(40)
        #print(review_numb, review_scor, review_con)

        if request.form['action'] == 'update2':
        # Update 버튼이 클릭된 경우의 처리

            # 해당 리뷰번호에 해당하는 리뷰 도큐먼트를 불러와서, 그 리뷰의 place_seq를 찾는 과정
            filter_query = {'review_seq': review_numb}
            documentreview = collection_review.find_one(filter_query) #리뷰콜렉션에서 검색
            place_seq = int(documentreview['place_seq']) # string으로 오기때문에, 정수로 변환

            # 해당 리뷰번호에 새로운 리뷰점수와 리뷰내용 업데이트
            filter_query = {'review_seq': review_numb}
            update_query = {'$set': {'review_contents': review_con, 'review_score': review_scor}}
            result = collection_review.update_one(filter_query, update_query) #리뷰콜렉션에서 업데이트

            #해당 place의 현재 리뷰점수와 리뷰개수를 불러오는 과정, 리뷰업데이트와는 순서가 상관없음.
            filter_query = {'place_seq': place_seq}
            total_score = 0
            documentplace = collection_place.find_one(filter_query) #place콜렉션에서 검색해야한다.
            place_review_count = int(documentplace['place_review_count'])
            cur_place_score_avg = float(documentplace['place_score_avg'])

            #해당 place의 번호를 가진 활성화된 모든 리뷰를 불러와 그 리뷰들이 가진 점수를 total_score에 합산하여 새로운 평균 계산
            #해당 place를 찾아서 새로운 평균 업데이트
            filter_query = {'place_seq': place_seq, 'review_status' : 10} #활성화된 리뷰만 검색
            cursor = collection_review.find(filter_query)
            for document in cursor:
                total_score += document['review_score']
            new_place_score_avg = float(total_score/place_review_count)
            filter_query = {'place_seq': place_seq}
            update_query = {'$set': {'place_score_avg': new_place_score_avg}}
            result = collection_place.update_one(filter_query, update_query) #place콜렉션에 업데이트가 필요하다
            
            return redirect(url_for('admin_post3'))

        elif request.form['action'] == 'delete2':
        # Delete 버튼이 클릭된 경우의 처리

            # 해당 리뷰번호에 해당하는 리뷰 도큐먼트를 불러와서, 그 리뷰의 place_seq를 찾는 과정
            filter_query = {'review_seq': review_numb}
            documentreview = collection_review.find_one(filter_query)
            place_seq = int(documentreview['place_seq']) # string으로 오기때문에, 정수로 변환
            review_user_id = documentreview['user_id']

            # 해당 리뷰번호의 review_status를 비활성화
            filter_query = {'review_seq': review_numb}
            update_query = {'$set': {'review_status': delete_num}}
            result = collection_review.update_one(filter_query, update_query) #리뷰콜렉션에서 업데이트

            #해당 리뷰를 작성한 user의 user_review_cnt 업데이트
            filter_query = {'user_id': review_user_id}
            documentuser = collection_user.find_one(filter_query)
            cur_user_review_cnt = documentuser['user_review_cnt']
            new_user_review_cnt = cur_user_review_cnt - 1
            update_query = {'$set': {'user_review_cnt': new_user_review_cnt}}
            result = collection_user.update_one(filter_query, update_query)

            #해당 place의 현재 리뷰점수와 리뷰개수를 불러오는 과정, 리뷰업데이트와는 순서가 상관없음.
            filter_query = {'place_seq': place_seq}
            total_score = 0
            documentplace = collection_place.find_one(filter_query) #place콜렉션에서 검색해야한다.
            place_review_count = int(documentplace['place_review_count'])
            new_place_review_count = place_review_count - 1
            cur_place_score_avg = float(documentplace['place_score_avg'])

            #해당 place의 번호를 가진 활성화된 모든 리뷰를 불러와 그 리뷰들이 가진 점수를 total_score에 합산하여 새로운 평균 계산
            #해당 place를 찾아서 새로운 평균 업데이트
            filter_query = {'place_seq': place_seq, 'review_status' : 10} #활성화된 리뷰만 검색
            cursor = collection_review.find(filter_query) 
            for document in cursor:
                total_score += document['review_score']
            if(new_place_review_count == 0) :
                new_place_score_avg = float(0.0)
            else :
                new_place_score_avg = float(total_score/new_place_review_count)
            filter_query = {'place_seq': place_seq}
            update_query = {'$set': {'place_score_avg': new_place_score_avg, 'place_review_count' : new_place_review_count}}
            result = collection_place.update_one(filter_query, update_query) #place콜렉션에 업데이트가 필요하다

            return redirect(url_for('admin_post3'))

    return render_template('/admin/adminPost_rm.html', reviews=reviews)

def admin_post4():
    users = collection_user.find({ #검색은 활성화된 도큐먼트에만 시행
        "user_status" : 10
    })

    if request.method == 'POST':
        #print(request.form['action'])
        user_id = request.form['userID']
        delete_num = int(40)

        if request.form['action'] == 'delete3':
        # Delete 버튼이 클릭된 경우의 처리

            #해당 유저 비활성화 처리
            filter_query = {'user_id': user_id}
            update_query = {'$set': {'user_status': delete_num}}
            result = collection_user.update_one(filter_query, update_query) #user 콜렉션에서 업데이트해야한다.


            #해당 유저가 작성하였던 모든 활성화된 review 검색
            filter_query = {'user_id': user_id, 'review_status' : 10}
            cursor = collection_review.find(filter_query)
            #모든 리뷰를 확인하면서, 비활성화처리
            for document in cursor:
                review_seq = int(document['review_seq']) 
                filter_query = {'review_seq' : review_seq}
                update_query = {'$set': {'review_status': delete_num}}
                minus_review_score = int(document['review_score']) #place의 review점수의 재연산을 위한 값 중 하나
                result = collection_review.update_one(filter_query, update_query) #리뷰콜렉션의 업데이트
                #그 과정에서 그 리뷰에 해당하는 place를 찾아서, 해당 place의 리뷰개수와 리뷰평균값 재연산
                place_seq = int(document['place_seq']) # string으로 오기때문에, 정수로 변환
                filter_query = {'place_seq' : place_seq}
                documentplace = collection_place.find_one(filter_query) #place 콜렉션에서 검색해야한다
                cur_place_review_count = int(documentplace['place_review_count']) #검색한 documnetplace에서 현재의 review개수 저장
                cur_place_review_avg = float(documentplace['place_score_avg']) #검색한 documnetplace에서 현재의 review점수 평균 저장
                temp_total_score = cur_place_review_count*cur_place_review_avg # 두 값을 합해서 총 값의 임시값 저장
                new_place_review_count = cur_place_review_count - 1 #새로운 place리뷰개수는 현재 개수에서 -1
                new_total_score = temp_total_score - minus_review_score #총 값의 임시값에서 아까 저장한 제거할 리뷰의 점수 저장
                if(new_place_review_count == 0) :
                    new_place_review_avg = float(0.0)
                else :
                    new_place_review_avg = float(new_total_score/new_place_review_count)
                filter_query = {'place_seq' : place_seq}
                update_query = {'$set': {'place_review_count': new_place_review_count, 'place_score_avg' : new_place_review_avg}}
                result = collection_place.update_one(filter_query, update_query)

            return redirect(url_for('admin_post4'))

    return render_template('/admin/adminPost_um.html', users=users)

def admin_post5():
    recommends = collection_recommend.find({ #활성화된 콜렉션만 검색
        "rec_status" : 10
    })

    if request.method == 'POST':
        #print(request.form['action'])
        place_name = request.form['recplacename']
        delete_num = int(40)

        if request.form['action'] == 'delete4':
        #Delete 버튼이 클릭된 경우의 처리
            #다른 콜렉션과 관계가 없는 독립적인 도큐먼트들이라 비활성화만 시키면된다.
            #print(request.form['action'])
            filter_query = {'rec_pname': place_name}
            update_query = {'$set': {'rec_status': delete_num}}
            result = collection_recommend.update_one(filter_query, update_query)
            #print(result.raw_result)
            return redirect(url_for('admin_post5'))

    return render_template('/admin/adminPost_rec.html', recommends=recommends)

def admin_post6():
    if request.method == 'POST':
        seq_max_document = collection_place.find().sort('place_seq', -1).limit(1)
        seq_max_value = int(seq_max_document[0]['place_seq'])

        place_seq = seq_max_value + int(1)
        place_name = request.form['placename']
        place_info = request.form['placeinfo']
        place_url = request.form['placeurl']
        place_img = request.form['placeimg']
        place_locate_info = request.form['placelocateinfo']
        place_locate_num = int(request.form['placelocatenum'])
        place_category = request.form['placecategory']
        place_thema = request.form['placethema']
        place_review_count = 0
        place_status = int(10)
        place_score_avg = float(0.0)
        place_map = request.form['placemap']


        # 데이터 MongoDB에 저장
        createdata = {
            'place_seq' : place_seq,
            'place_nm' : place_name,
            'place_info' : place_info,
            'place_url' : place_url,
            'place_img' : place_img,
            'place_locate_info' : place_locate_info,
            'place_locate_num' : place_locate_num,
            'place_category' : place_category,
            'place_thema' : place_thema,
            'place_review_count' : place_review_count,
            'place_status' : place_status,
            'place_score_avg' : place_score_avg,
            'place_map' : place_map
        }

        if request.form['action'] == 'create':
            collection_place.insert_one(createdata)
            return redirect(url_for('admin_post6'))

    return render_template('/admin/adminPost_ap.html')