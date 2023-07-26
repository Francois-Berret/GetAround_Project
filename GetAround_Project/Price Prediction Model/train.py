import os
import pandas as pd
import time
import mlflow
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split 
from sklearn.preprocessing import  StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression


if __name__ == "__main__":

    # Set your variables for your environment
    EXPERIMENT_NAME="rental_pricing_regressor"

    # Set tracking URI to your Heroku application
    mlflow.set_tracking_uri(os.environ["APP_URI"])

    # Set experiment's info 
    mlflow.set_experiment(EXPERIMENT_NAME)

    # Get our experiment info
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

    print("training model...")
    
    # Time execution
    start_time = time.time()

    # Call mlflow autolog
    mlflow.sklearn.autolog(log_models=False)

    # Import dataset
    df = pd.read_csv("get_around_pricing_project.csv")

    df = df.iloc[:,1:]
    df['model_key'] = df['model_key'].replace("Citroën", "Citroen")

    model_key_counts = df['model_key'].value_counts()
    single_occurrences = model_key_counts[model_key_counts < 50]
    df['model_key'] = df['model_key'].replace(single_occurrences.index, 'Other')

    # X, y split 
    target = "rental_price_per_day"

    X = df.drop(target, axis=1)
    y = df.loc[:,target]

    # Train / test split 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

    print(df.columns)

    #Preprocessing 
    numeric_features = ["mileage", "engine_power"]
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
        ])
    
    categorical_features = ['model_key']

    categorical_transformer = Pipeline(steps=[
        ('encoder', OneHotEncoder(drop='first'))
        ])
    
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
        ])

    # Pipeline 
    model = Pipeline(steps=[
        ('preprocessing', preprocessor),
        ('regressor', LinearRegression())
    ])

    # Log experiment to MLFlow
    with mlflow.start_run(experiment_id = experiment.experiment_id) as run:
        model.fit(X_train, y_train)
        predictions = model.predict(X_train)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="pricing_regressor",
            registered_model_name="pricing_regressor_LinearRegBase2",
            signature=infer_signature(X_train, predictions)
        )
        
    print("...Done!")
    print(f"---Total training time: {time.time()-start_time}")