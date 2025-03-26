import os
import joblib
import pandas as pd
import seaborn as sns

from prometheus_client import start_http_server, Guage
from prometheus_client import make_wsgi_app
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler 
from werkzeug.middleware.dispatcher import DispatchedMiddleware
from data_drift import detect_data_drift
from concept_drift import detect_concept_drift

app=Flask(__name__=="__main__")

# Load the model pipeline
try:
    modelPipeline=joblib.load("model_pipeline.joblib")
    print("Model Pipeline Loaded Successfully")
except:
    print("Error Loading Model Pipeline")
    print(f"Current Working Directtory:{os.getcwd()}")
    print(f"Contents of current directory:{os.listdir()}")
    modelPipeline=None

@app.route(rule="/predict",methods=["POST"])
def predict():
    if modelPipeline is None:
        return jsonify({"error":"Model not Loaded Properly"}),500
    data=request.json
    df=pd.DataFrame(data=data,index=[0])
    prediction=modelPipeline.predict(X=df)
    return jsonify({"prediction":prediction.tolist()}),200

# Create Prometheus Metrics for Data Drift
data_drift_guage=Guage("data_drift","Data Drift Score")
# Create Prometheus Metrics for Concept Drift
concept_drift_guage=Guage("concept_drift","Concept Drift Score")

# Load Reference Data
diamonds=sns.load_dataset(name="diamonds")

X_reference=diamonds[["carat","cut","color","clarity","depth","table"]]
y_reference=diamonds["price"]

def monitorDrifts():
    newDiamonds=sns.load_dataset(name="diamonds").sample(n=1000,replace=True)
    X_current=newDiamonds[["carat","cut","color","clarity","depth","table"]]
    y_current=newDiamonds["price"]

    # Data Drift Detection
    is_data_drift,_,data_drift_score=detect_data_drift(
        reference_data=X_reference,current_data=X_current)
    data_drift_guage.set(data_drift_score)

    # Concept Drift Detection
    is_concept_drift, concept_drift_score=detect_concept_drift(model_pipeline=modelPipeline,
                                                       X_reference=X_reference,y_reference=y_reference,
                                                       X_current=X_current,y_current=y_current)
    concept_drift_guage.set(concept_drift_score)

    if is_data_drift:
        print("Data Drift Detected")
    if is_concept_drift:
        print("Concept Drift Detected")


# Schedule the Monitoring Job
app.wsgi_app=DispatchedMiddleware(app.wsgi_app,{"metrics":make_wsgi_app()})

if __name__=="__main__":
    # Start Prometheus Metric Server
    start_http_server(port=8000)

    # schedule the drift monitoring
    scheduler=BackgroundScheduler()
    scheduler.add_job(func=monitorDrifts,trigger="interval",seconds=60)
    scheduler.start()

    # Run the Flask App
    app.run(port=5000,host="0.0.0.0")
