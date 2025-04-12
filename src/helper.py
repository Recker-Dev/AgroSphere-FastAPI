
import os
import torch
import torch.nn.functional  as F
import torchvision.transforms as transforms
from src.graph import chat_graph
import pandas as pd

import cv2
import numpy as np


from langchain_core.messages import HumanMessage, SystemMessage



def crop_recommendation_prediction(input_list, loaded_model, label_encoder, preprocessor):
    """
    Takes a list of 7 numeric features and returns the predicted class label.
    """
    print("Starting crop recommendation prediction...")
    print(f"Received input list: {input_list}")

    # Validate input length
    assert len(input_list) == 7, "Input must have exactly 7 features."

    # Convert to 2D DataFrame
    input_df = pd.DataFrame([input_list], columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])
    print("Converted input to DataFrame:")
    print(input_df)

    # Preprocess
    processed_input = preprocessor.transform(input_df)
    print("After preprocessing:")
    print(processed_input)

    # Convert to tensor
    input_tensor = torch.tensor(processed_input, dtype=torch.float32).to('cpu')
    print(f"Converted to tensor: {input_tensor.shape}")
    print(input_tensor)

    # Predict
    loaded_model.eval()
    with torch.no_grad():
        logits = loaded_model(input_tensor)
        print("Logits from model:")
        print(logits)
        probs = F.softmax(logits, dim=1)
        print("Probabilities after softmax:")
        print(probs)

    topk_probs, topk_indices = torch.topk(probs, k=3, dim=1)
    print(f"Top 3 indices: {topk_indices}")
    print(f"Top 3 probabilities: {topk_probs}")

    topk_indices = topk_indices.tolist()[0]
    topk_probs = topk_probs.tolist()[0]

    topk_labels = label_encoder.inverse_transform(topk_indices)
    print(f"Predicted top 3 labels: {topk_labels}")

    result = {
        "top_3_predictions": [
            {"label": label, "probability": round(float(prob), 4)}
            for label, prob in zip(topk_labels, topk_probs)
        ]
    }
    print("Final prediction response:")
    print(result)

    return result




def soil_type_prediction(img, soil_type_model):
    print("Starting soil_type_prediction...")

    class_names = ['Alluvial soil', 'Black Soil', 'Clay soil', 'Red soil']
    
    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])

    input_image = transform(img).unsqueeze(0)
    print(f"Input image shape: {input_image.shape}")

    soil_type_model.eval()
    with torch.no_grad():
        output = soil_type_model(input_image)
        print(f"Model output: {output}")
        probs = F.softmax(output, dim=1)
        print(f"Probabilities: {probs}")

    prob_dict = {
        class_names[i]: round(probs[0][i].item(), 6)
        for i in range(len(class_names))
    }

    print("Prediction successful.")
    return prob_dict


def query_historic_data_llm(agent_executor,llm_gemini,query):
    # Step 1: Agent tries to extract structured data
    agent_sys_msg = SystemMessage(content=(
        "Fetch State_Name, District_Name and other column names (if needed) before proceeding with any logic "
        "to prevent failure. If you fail to fetch the state-name or district-name or crop-name which leads to upcoming errors, "
        "let the user know for the given query you do not have the data to answer."
    ))
    user_msg = HumanMessage(content=query)


    try:
        agent_response = agent_executor.invoke([agent_sys_msg, user_msg])
        agent_output = agent_response.get("output", "")
    except Exception as e:
        agent_output = f"[Agent failed]: {e}"



    # Step 2: Gemini takes the agent's output + forms final reply
    gemini_sys_msg = SystemMessage(content=(
        "You're an expert assistant that helps answer user queries based on historical agriculture data. "
        "You are given the output from a data-extracting agent. If the agent failed to extract critical info like "
        "state, district, or crop name, let the user know that you cannot answer the query due to missing data. "
        "Otherwise, respond helpfully and clearly using the agent's extracted information."
    ))

    final_query_to_gemini = [
        gemini_sys_msg,
        HumanMessage(content=f"User Query: {query}\n\nAgent Output: {agent_output}")
    ]

    gemini_response = llm_gemini.invoke(final_query_to_gemini)
    return gemini_response.content



def chat_with_llm(config, query):

    for event in chat_graph.stream({"query":query}, config, stream_mode="updates"):
        print("--Node--")
        node_name = next(iter(event.keys()))
        print(node_name)

    return chat_graph.get_state(config).values["messages"][-1].content



def detect_weeds_from_image(image_bytes: bytes, weed_detector) -> bytes:
    # Convert image bytes to OpenCV format
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Run YOLO inference
    results = weed_detector(img)

    # Draw predictions
    for r in results:
        im_array = r.plot()

    # Encode image with predictions to JPEG
    _, buffer = cv2.imencode(".jpg", im_array)
    return buffer.tobytes()
