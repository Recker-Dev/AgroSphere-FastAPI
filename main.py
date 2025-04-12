from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO

from src.schema import SoilInput
from src.model_arch import load_crop_recommendation_model, load_soil_type_detection_model, load_gemini,load_csv_executor, load_weed_detector
from src.helper import crop_recommendation_prediction,soil_type_prediction,query_historic_data_llm,chat_with_llm, detect_weeds_from_image

## Pre-Load necessary items.
crop_recommendation_model, label_encoder, preprocessor = load_crop_recommendation_model()
soil_detection_model = load_soil_type_detection_model()
llm_gemini = load_gemini()
agent_executor = load_csv_executor(llm_gemini)
weed_detector = load_weed_detector()


# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def root():
    return "Online"


@app.post("/predictCrop")
def predict(data: SoilInput):
    try:
        data = data.to_list()
        return crop_recommendation_prediction(data,crop_recommendation_model,label_encoder,preprocessor)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/predictSoil")
async def predict_soil(file: UploadFile = File(...)):
    try:
        image = Image.open(file.file).convert("RGB")
        result = soil_type_prediction(image, soil_detection_model)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()  # Optional, logs full traceback in backend
        raise HTTPException(status_code=500, detail="Prediction failed. Please try again.")


@app.post("/chatHistoricModel")
async def chat_with_historic_data_model(text: str = Form(...)):

    async def generate_response():
        try:
            # simulate streaming (you should modify query_historic_data_llm to yield tokens or chunks)
            for chunk in query_historic_data_llm(agent_executor,llm_gemini, text):
                yield chunk
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"\n\n[Error] {str(e)}"

    return StreamingResponse(generate_response(), media_type="text/plain")
        

@app.post("/chatWithLLM")
async def chat_with_chat_model(thread_id: str = Form(...), query:str = Form(...)):

    async def generate_response():
        try:
            config = {'configurable': {'thread_id': thread_id}}
            for chunk in chat_with_llm(config, query):
                yield chunk
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"\n\n[Error] {str(e)}"

    return StreamingResponse(generate_response(), media_type="text/plain")
        

@app.post("/detect-weeds")
async def detect_weeds(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        result_image_bytes = detect_weeds_from_image(image_bytes,weed_detector)
        return StreamingResponse(BytesIO(result_image_bytes), media_type="image/jpeg")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": "Weed detection failed. Please try again."}