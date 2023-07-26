import mlflow 
import uvicorn
import pandas as pd 
from fastapi import FastAPI, Body, HTTPException, Query
from enum import Enum
from pydantic import BaseModel, Field
from typing import List
import mlflow.pyfunc

description = """
## Welcome to this tool designed to help you determine the rental price of your vehicle on GetAround.
Designed for vehicle owners, this helper works simply : you enter the characteristics of your vehicle, and it compares market prices to provide you with the most suitable one for your vehicle. The price obtained is given as an indication in order to give you a precise and realistic view of the market, then you are free to set it according to your wishes.

### Insights

Endpoints to get some insights on the vehicle rental market 

* `/price_stats`

* `/vehicle_characteristics_distribution`


### Prediction

Endpoint that predict le rental price of your vehicle

* `/predict`
"""

tags_metadata = [
    {"name": "Introduction Endpoint", "description": "Welcome endpoint that give you path to the API"},
    {"name": "GetAround Market", "description": "Informational endpoints that give you some insights"},
    {"name": "Prediction", "description": "Prediction by Machine Learning endpoint"}
]

app = FastAPI(
    title="🚗 GetAround Rental Price Helper",
    description=description,
    openapi_tags=tags_metadata
)

df = pd.read_csv('get_around_pricing_project.csv')

class ValuesModelKey(str, Enum):
    Citroen = "Citroen"
    Renault = "Renault"
    BMW = "BMW"
    Peugeot = "Peugeot"
    Audi = "Audi"
    Nissan = "Nissan"
    Mitsubishi = "Mitsubishi"
    Mercedes = "Mercedes"
    Volkswagen = "Volkswagen"
    Toyota = "Toyota"
    Other = "Other"

class ValuesFuel(str, Enum):
    diesel = "diesel"
    petrol = "petrol"
    hybrid_petrol = "hybrid_petrol"
    electro = "electro"

class ValuesPaintColor(str, Enum):
    black = "black"
    grey = "grey"
    blue = "blue"
    white = "white"
    brown = "brown"
    silver = "silver"
    red = "red"
    beige = "beige"
    green = "green"
    orange = "orange"

class ValuesCarType(str, Enum):
    estate = "estate"
    sedan = "sedan"
    suv = "suv"
    hatchback = "hatchback"
    subcompact = "subcompact"
    coupe = "coupe"
    convertible = "convertible"
    van = "van"

class VehiculesCharacteristics(str, Enum):
    model_key = "model_key"
    mileage = "mileage"
    engine_power = "engine_power"
    fuel = "fuel"
    paint_color = "paint_color"
    car_type = "car_type"
    private_parking_available = "private_parking_available"
    has_gps = "has_gps"
    has_air_conditioning = "has_air_conditioning"
    automatic_car = "automatic_car"
    has_getaround_connect = "has_getaround_connect"
    has_speed_regulator = "has_speed_regulator"
    winter_tires = "winter_tires"

class PredictInput(BaseModel):
    model_key: ValuesModelKey = Field(..., title="Model key of your vehicle", description="Model Key")
    mileage: int = Field(..., title="Mileage", description="Mileage", ge=0)
    engine_power: int = Field(..., title="Engine Power", description="Engine Power", ge=0)
    fuel: ValuesFuel = Field(..., title="Fuel type of your vehicle", description="Fuel")
    paint_color: ValuesPaintColor = Field(..., title="Paint color of your vehicle", description="Paint Color")
    car_type: ValuesCarType = Field(..., title="Car type of your vehicle", description="Car Type")
    private_parking_available: bool = Field(..., title="Private Parking Available", description="Private Parking Available")
    has_gps: bool = Field(..., title="Has GPS", description="Has GPS")
    has_air_conditioning: bool = Field(..., title="Has Air Conditioning", description="Has Air Conditioning")
    automatic_car: bool = Field(..., title="Automatic Car", description="Automatic Car")
    has_getaround_connect: bool = Field(..., title="Has Getaround Connect", description="Has Getaround Connect")
    has_speed_regulator: bool = Field(..., title="Has Speed Regulator", description="Has Speed Regulator")
    winter_tires: bool = Field(..., title="Winter Tires", description="Winter Tires")

@app.get("/", tags=["Introduction Endpoint"])
async def index():
    message = "Welcome to the GetAround rental price helper! Get access to the API documentation at `https://getaroundprojectapi-0e8eaaf2ae82.herokuapp.com/docs`"
    return message

@app.get("/price_stats", tags=["GetAround Market"])
async def get_stats_on_rental_prices():
    stats = {
        "min": int(df['rental_price_per_day'].min()),
        "mean": int(df['rental_price_per_day'].mean()),
        "max": int(df['rental_price_per_day'].max()),
        "q1": int(df['rental_price_per_day'].quantile(0.25)),
        "q3": int(df['rental_price_per_day'].quantile(0.75))
    }
    return stats

@app.get("/counts/", tags=["GetAround Market"])
async def place_your_vehicle_among_all(
    characteristic: VehiculesCharacteristics = Query(
        ..., 
        title="Vehicles Characteristisc",
        description="Select a vehicle characteristic"
    )
):
    """
    See the distribution of the selected vehicle characteristic on the GetAround market.
    """
    if characteristic not in df.columns:
        raise HTTPException(status_code=404, detail="Characteristic not found")

    if pd.api.types.is_bool_dtype(df[characteristic]):
        result = df[characteristic].value_counts().reset_index()
        result.columns = [characteristic, 'count']
        return result.to_dict(orient='records')
    elif pd.api.types.is_numeric_dtype(df[characteristic]):
        result = df[characteristic].mean()
        return {"average": result}
    else:
        result = df[characteristic].value_counts().reset_index()
        result.columns = [characteristic, 'count']
        return result.to_dict(orient='records')


@app.post("/predict", tags=["Prediction"])
async def predict_rental_price(predict_input: PredictInput):
    """
    Predict the rental price of your vehicle based on prices set by other vehicle owners.

    
    ⚠️ Please checkout the Schema index to see format and possible values for each category ⚠️
    """
    model_key = predict_input.model_key
    mileage = predict_input.mileage
    engine_power = predict_input.engine_power
    fuel = predict_input.fuel
    paint_color = predict_input.paint_color
    car_type = predict_input.car_type
    private_parking_available = predict_input.private_parking_available
    has_gps = predict_input.has_gps
    has_air_conditioning = predict_input.has_air_conditioning
    automatic_car = predict_input.automatic_car
    has_getaround_connect = predict_input.has_getaround_connect
    has_speed_regulator = predict_input.has_speed_regulator
    winter_tires = predict_input.winter_tires

    # Create input data
    input_data = pd.DataFrame({
        "model_key": [model_key],
        "mileage": [mileage],
        "engine_power": [engine_power],
        "fuel": [fuel],
        "paint_color": [paint_color],
        "car_type": [car_type],
        "private_parking_available": [private_parking_available],
        "has_gps": [has_gps],
        "has_air_conditioning": [has_air_conditioning],
        "automatic_car": [automatic_car],
        "has_getaround_connect": [has_getaround_connect],
        "has_speed_regulator": [has_speed_regulator],
        "winter_tires": [winter_tires]
    })

    # Load model from mlflow
    logged_model = 'runs:/b645b358f34545f2956b81e3c2f57500/pricing_regressor'
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    try:
        # Make prediction
        prediction = loaded_model.predict(input_data)

        # Format response
        response = {"prediction": prediction.tolist()[0]}
        return response

    except Exception as e:
        # Handle any exception that might occur during prediction
        raise HTTPException(status_code=500, detail="Prediction error: " + str(e))

def run_app():
    uvicorn.run(app, host="0.0.0.0", port=4000)

if __name__ == "__main__":
    run_app()