from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from pymongo import MongoClient
from routes import index, login, signup, logout, check_login
from routes2 import food_list, food_detail, cafe_list, cafe_detail, place_recommend, place_recommend2
from routes3 import  admin_user, admin_user2, admin_user3, admin_user3suc, admin_user3fail, admin_userprofile
from routes4 import admin_post, admin_post2, admin_post3, admin_post4, admin_post5, admin_post6 
import bcrypt
import functools

app = Flask(__name__)
app.secret_key = '7684d16e188311e10cf5653c8f86ce22233f3ee591d5bed84cbab91db66b42ec'

app.route('/')(index)


app.route('/login', methods = ['GET', 'POST'])(login)
app.route('/check_login', methods = ['GET'])(check_login)
app.route('/')(index)
app.route('/signup', methods = ['GET', 'POST'])(signup)
app.route('/logout')(logout)
app.route('/food/foodList', methods = ['GET', 'POST'])(food_list)
app.route('/food/foodDetail/<int:seq>', methods = ['GET', 'POST'])(food_detail)
app.route('/cafe/cafeList', methods = ['GET', 'POST'])(cafe_list)
app.route('/cafe/cafeDetail/<int:seq>', methods = ['GET', 'POST'])(cafe_detail)
app.route('/placeRecommend', methods=['GET', 'POST'])(place_recommend)
app.route('/placeRecommend2')(place_recommend2)
app.route('/admin/post')(admin_post)
app.route('/admin/post2', methods=['GET', 'POST'])(admin_post2)
app.route('/admin/post3', methods=['GET', 'POST'])(admin_post3)
app.route('/admin/post4', methods=['GET', 'POST'])(admin_post4)
app.route('/admin/post5', methods=['GET', 'POST'])(admin_post5)
app.route('/admin/post6', methods=['GET', 'POST'])(admin_post6)
app.route('/admin/userprofile', methods=['GET', 'POST'])(admin_userprofile)
app.route('/admin/user', methods=['GET', 'POST'])(admin_user)
app.route('/admin/user2', methods=['GET', 'POST'])(admin_user2)
app.route('/admin/user3', methods=['GET', 'POST'])(admin_user3)
app.route('/admin/user3suc')(admin_user3suc)
app.route('/admin/user3fail')(admin_user3fail)

if __name__ == "__main__":
    app.run(host="142.93.167.2", port=80, debug=True)