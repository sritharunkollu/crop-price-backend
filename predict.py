import joblib
import pandas as pd
import sys
import json
import os

def make_prediction(state, district, crop):
    try:
        model_dir = 'model_files'
        model_path = os.path.join(model_dir, 'gradient_boosting_model.joblib')
        if not os.path.exists(model_path):
            return {"error": "Model not found. Please train the model first."}
        pipeline = joblib.load(model_path)
        input_df = pd.DataFrame([[state, district, crop]], columns=['State', 'District', 'Commodity'])
        predicted_price = pipeline.predict(input_df)
        price = predicted_price[0]
        return {"predicted_price": f"{price:.2f}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(json.dumps({"error": "Invalid number of arguments."}))
    else:
        state_arg = sys.argv[1]
        district_arg = sys.argv[2]
        crop_arg = sys.argv[3]
        final_result = make_prediction(state_arg, district_arg, crop_arg)
        print(json.dumps(final_result))