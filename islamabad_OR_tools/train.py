import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import xgboost as xgb
def train():
    df=pd.read_csv('islamabad_traffic_data.csv')
    X=df.drop(columns=['travel_time_minutes'])
    y=df['travel_time_minutes']
    #spliting data into test and train pairs  
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)
    #intializing the brain
    model=xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train,y_train)
    prediction=model.predict(X_test)
    error=mean_absolute_error(prediction, y_test)
    print(f"the main absolute error is{error}")
    #saving model
    model.save_model('islamabad_traffic_model.json')
    print("Model saved successfully!")
if __name__=="__main__":
    train()