from flask import Flask, render_template, request, Response, redirect, url_for , session , jsonify , flash
from flask_bootstrap import Bootstrap

from object_detection import *
import object_detection

from flask_sqlalchemy import SQLAlchemy # import sqlalchemy
from database import db , Vehicle , DB_Manager

import webbrowser

from threading import Timer #Debug Autostart


application = Flask(__name__)
application.config.update(
    TESTING = True,
    SECRET_KEY = "password"
)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/vehicle_db.sqlite3' # Config to use sqlalchemy
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)
db_manager = DB_Manager()

VIDEO = VideoStreaming(camera_src = 0)


@application.route('/')
def home():
    page_title = 'HuaweiOCR | Home'
    current_plate = ""
    current_owner = ""
    return render_template('index.html', TITLE=page_title , PLATE = current_plate, OWNER = current_owner)

@application.route('/update_plate' , methods=['POST'])
def updateplate():
    current_plate = object_detection.current_plate 
    db_manager.get_db_data() # Not sure
    try:
        current_owner = db_manager.search_owner(current_plate)
    except:
        current_owner = "Not Verified"

    return jsonify('' , render_template('dynamic_plate.html', PLATE = current_plate , OWNER = current_owner))


@application.route('/update_gate' , methods=['POST'])
def updategate():
    # current_plate = object_detection.current_plate 
    # current_g_status = False
    current_g_status = "Closed"
    return jsonify('' , render_template('dynamic_gate.html', GATE = current_g_status ))

@application.route('/video_feed')
def video_feed():
    '''
    Video streaming route.
    '''
    return Response(
        VIDEO.show(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@application.route('/request_model_switch')
def request_model_switch():
    #TODO: On toggle OFF turn current-plate to XXX-XXXX
    # if VIDEO.detect == True:
    #     # current_plate = "XXX-XXXX"
    #     object_detection.current_plate = "XXX-XXXX"
    VIDEO.detect = not VIDEO.detect

    try:
        print("This is a return function from VideoStreaming class " + str(VIDEO.lblret))
    except:
        pass
    return "nothing"

@application.route("/database" , methods=["POST","GET"])
def data_mode():
    page_title = 'HuaweiOCR | Database Mode'
    db_man = DB_Manager()
    error = False
    error_message = ""

    try:
        if request.method =="POST":
            session.permanent = True
            car_to_delete = request.form["delete_plate_input"].upper()
            if car_to_delete:
                db_man.delete_car_and_all_entries(car_to_delete)
                flash(f"Deleted Vehicle:  [{car_to_delete}] and all Entries ", "info")

            else:
                error = True
                error_message = "Input Plate isn't registered or Input is empty"
            
            return redirect(url_for('data_mode'))

            
    except Exception as e:
        print(f"EXCEPTION AT /database route: {e}")
        error = True
        error_message = "Vehicle Plate is invalid or not existing"

    return render_template("data_mode.html" , db_data = db_man.db_data, TITLE=page_title , error = error , error_msg = error_message) 

@application.route("/register", methods=["POST","GET"])
def register_mode():
    page_title = 'HuaweiOCR | Register Mode'
    error = False
    error_message = ""
    try:
        if request.method =="POST":
            session.permanent = True
            plate_input = request.form["plate_input"].upper()
            owner_input = request.form["owner_input"].title()
            if plate_input:
                current_registering = Vehicle(plate_num = plate_input , owner_name = owner_input)
                db.session.add(current_registering)
                db.session.commit()
                db_manager.get_db_data()
                flash(f"Successfully Registered [{plate_input}]", "info")
            else:
                error = True
                error_message = "Input Box Empty"
    except Exception as e:
        error = True
        error_message = "Error Input Box Value"
    return render_template("register_mode.html", TITLE=page_title , error = error , error_msg = error_message) 

@application.route("/logs")
def log_mode():
    db_man = DB_Manager()
    page_title = 'HuaweiOCR | Log Mode'
    return render_template("log_mode.html", db_data = db_man.db_data_entries, TITLE=page_title) 

def open_browser():
    ''' Debug autostartt'''
    webbrowser.open_new('http://127.0.0.1:2000/')


if __name__ == '__main__':
    # Timer(3, open_browser).start() # Auto open browser
    # db.create_all() # Create db when it doesnt exist
    application.run(port = 2000 , debug = True)