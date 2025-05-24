
# AgroSphere-FastAPI

## Overview

AgroSphere-FastAPI is a FastAPI-based application designed to provide various agricultural services, including crop recommendation, soil type detection, interaction with historical data via a language model, and weed detection. This application leverages machine learning models and APIs to assist farmers and agricultural enthusiasts in making informed decisions.

## Features

-   **Crop Recommendation:** This feature takes soil parameters such as Nitrogen, Phosphorus, Potassium, temperature, humidity, pH, and rainfall as input and recommends the most suitable crops to grow in that soil.
-   **Soil Type Detection:** This feature allows users to upload an image of soil, and the application will identify the type of soil present in the image.
-   **Historical Data Interaction:** This feature enables users to query historical agricultural data using natural language. It leverages a language model to understand the query and provide relevant information from a dataset of historical agricultural data.
-   **Weed Detection:** This feature allows users to upload an image of a field or crop, and the application will detect the presence of weeds in the image, highlighting them for removal.
-   **General Purpose LLM:** This is a general purpose LLM that is connected to a multi-modal chat interface. You can upload images and ask questions about agriculture. 

## Technologies Used

-   FastAPI
-   PIL (Pillow)
-   Pytorch (for machine learning models)
-   Langchain (for LLM)
-   uvicorn

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Recker-Dev/AgroSphere-FastAPI.git
    cd AgroSphere-FastAPI
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\\Scripts\\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## API Endpoints

### 1. `/predictCrop`

-   **Description:** Recommends the most suitable crop based on the provided soil parameters.
-   **Input:** JSON payload with soil parameters (N, P, K, temperature, humidity, pH, rainfall).
-   **Example:**

    ```json
    {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 20.87974371,
        "humidity": 82.00274423,
        "ph": 6.502985292,
        "rainfall": 202.9355362
    }
    ```

### 2. `/predictSoil`

-   **Description:** Identifies the type of soil from an uploaded image.
-   **Input:** An image file of soil.

### 3. `/chatHistoricModel`

-   **Description:** Allows users to query historical agricultural data using natural language.
-   **Input:** Text query.
-   **Example:** `"What was the average rainfall in 2020?"`

### 4. `/chatWithLLM`

-   **Description:** Allows users to chat with a general purpose LLM with capabilities to upload images.
-   **Input:**
    -   `thread_id`: Thread ID for chat history.
    -   `query`: User's query to the LLM.
    -   `image` (optional): Upload an image file.

### 5. `/detect-weeds`

-   **Description:** Detects weeds in an uploaded image.
-   **Input:** An image file of a field or crop.

## Running the Application

1.  **Start the FastAPI server:**

    ```bash
    uvicorn main:app --reload
    ```

    This command starts the server on `http://localhost:8000`.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them.
4.  Submit a pull request.

## License

[Choose a license and add it here]
