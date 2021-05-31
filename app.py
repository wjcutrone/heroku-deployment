from flask import Flask, jsonify, render_template, request, g, redirect
from tensorflow.keras.models import load_model
import pandas as pd
import psycopg2
import os
import json
import numpy as np
import h5py

x_categorical_columns = ['Hospital_type_code',
                            'Hospital_region_code',
                            'Department',
                            'Ward_Type',
                            'Ward_Facility_Code',
                            'Type of Admission',
                            'Severity of Illness',
                            'Age',
                            'Bed Grade',
                            'Hospital_code',
                            'City_Code_Hospital',
                            'City_Code_Patient']
x_numerical_columns = ['Available Extra Rooms in Hospital',
                            'Visitors with Patient',
                            'Admission_Deposit']


#########################################
# Flask Setup
#########################################
app = Flask(__name__)

# Create the route that renders the index.html template
@app.route("/")
def home():
    return render_template("index.html")

# Create a route to get the user inputs and send them to the model
@app.route("/", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        Admission_Deposit = float(request.form["Admission_Deposit"])
        Age = request.form["Age"]
        Available_Extra_Rooms_in_Hospital = float(request.form["Available Extra Rooms in Hospital"])
        Bed_Grade = request.form["Bed Grade"]
        City_Code_Hospital = request.form["City_Code_Hospital"]
        City_Code_Patient = request.form["City_Code_Patient"]
        Department = request.form["Department"]
        Hospital_code = request.form["Hospital_code"]
        Hospital_region_code = request.form["Hospital_region_code"]
        Hospital_type_code = request.form["Hospital_type_code"]
        Severity_of_Illness = request.form["Severity of Illness"]
        Type_of_Admission = request.form["Type of Admission"]
        Visitors_with_Patient = float(request.form["Visitors with Patient"])
        Ward_Facility_Code = request.form["Ward_Facility_Code"]
        Ward_Type = request.form["Ward_Type"]

        input = {"Admission_Deposit": Admission_Deposit,
                 "Age": Age,
                 "Available Extra Rooms in Hospital": Available_Extra_Rooms_in_Hospital,
                 "Bed Grade": Bed_Grade,
                 "City_Code_Hospital": City_Code_Hospital,
                 "City_Code_Patient": City_Code_Patient,
                 "Department": Department,
                 "Hospital_code": Hospital_code,
                 "Hospital_region_code": Hospital_region_code,
                 "Hospital_type_code": Hospital_type_code,
                 "Severity of Illness": Severity_of_Illness,
                 "Type of Admission": Type_of_Admission,
                 "Visitors with Patient": Visitors_with_Patient,
                 "Ward_Facility_Code": Ward_Facility_Code,
                 "Ward_Type": Ward_Type}
        
    print(input)
    with open('translators.json', 'r') as f:
        translators=json.load(f)

  
    X_translator = translators['X_translator']
    scale_translator = translators['scale_translator']
    order = translators['data_order']
    y_translator = translators['y_translator']
    input_t = {}
    for (category, value) in input.items():
        print(category, value)
        if category in x_categorical_columns:
            try:
               input_t[category] = X_translator[category][str(value)]
            except:
                pass
        elif category in x_numerical_columns:
            mean = scale_translator[category]['mean']
            std = scale_translator[category]['standard_deviation']
            value = (value - mean)/std
            input_t[category] = value
        else:
            print(f'ERROR: Unsupported parameter found! {category}') 

    input_t = np.array([input_t[i] for i in order]).reshape(1, 15)
    model_1 = load_model('model_1.h5', compile=False)
    prediction = model_1.predict(input_t).argmax()
    prediction = y_translator[str(prediction)]
    return render_template("index.html", prediction=prediction)


if __name__ == "__main__":
    app.run()
