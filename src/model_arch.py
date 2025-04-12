import os
import torch
import torch.nn as nn
import joblib
import timm
import pandas as pd


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from dotenv import load_dotenv
from ultralytics import YOLO
load_dotenv()






## CROP RECOMMENDATION MODEL

class TabularNet(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(TabularNet, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        return self.net(x)


def load_crop_recommendation_model():
    torch.manual_seed(42)
    crop_recommendation_model = TabularNet(input_dim=7, output_dim=22).to("cpu")
    crop_recommendation_model.load_state_dict(torch.load('./models/crop_recommendation_model.pt',map_location=torch.device('cpu'), weights_only=True)) 
    label_encoder = joblib.load('./artifacts/label_encoder.joblib')
    preprocessor = joblib.load('./artifacts/preprocessor.joblib')
    return crop_recommendation_model, label_encoder, preprocessor
    

## SOIL TYPE RECOGNITION MODEL

class MobileeNetV2(nn.Module):
    def __init__(self, num_classes: int):
        super(MobileeNetV2, self).__init__()

        # Load EfficientNetB3 base model
        self.base_model = timm.create_model(
            'mobilenetv2_100',
            pretrained=True,
            num_classes=0  # Remove original classification head
        )

        # Add custom classification head
        self.classifier = nn.Sequential(
            nn.Linear(self.base_model.num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.base_model(x)
        x = self.classifier(x)
        return x


def load_soil_type_detection_model():
    torch.manual_seed(42)
    soil_detect_model=MobileeNetV2(num_classes=4).to('cpu')
    soil_detect_model.load_state_dict(torch.load('./models/soiltype_mobilenet_CNN.pt',map_location=torch.device('cpu'), weights_only=True))
    return soil_detect_model


def load_gemini():
    return ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"),
                            model="gemini-2.0-flash")


def load_csv_executor(llm_gemini):

    df = pd.read_csv("./dataset/crop_historic_data.csv")
    agent_executor = create_pandas_dataframe_agent(
    llm_gemini,
    df,
    agent_type="zero-shot-react-description",
    verbose=True,
    return_intermediate_steps=True,
    allow_dangerous_code=True,
    handle_parsing_errors=True
    )

    return agent_executor


def load_weed_detector():
    weed_detector = YOLO("./models/weed_detector.pt")
    return weed_detector