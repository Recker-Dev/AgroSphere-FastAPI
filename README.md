# 🌾 AgroSphere-FastAPI

AgroSphere-FastAPI is a backend application built with FastAPI to empower the agricultural ecosystem through intelligent automation. It assists farmers and researchers by recommending crops, detecting soil and weed types from images, and enabling interactive access to historical agricultural data using generative AI.

---

## 🧠 Key Features

- **🌱 Crop Recommendation**  
  Input soil parameters like Nitrogen, Phosphorus, Potassium, temperature, humidity, pH, and rainfall to receive tailored crop suggestions for your land.

- **🧪 Soil Type Detection**  
  Upload an image of soil, and the model will classify the type of soil, aiding in better agricultural decisions.

- **📊 Historical Data Interaction**  
  Query past agricultural data using natural language. A language model understands your question and retrieves insightful responses from historical datasets.

- **🌿 Weed Detection**  
  Upload an image of a field, and the system will detect and highlight weed-infested regions for targeted removal.

- **💬 Multi-Modal LLM Chat**  
  Chat with a general-purpose language model using both text and image inputs. Ideal for agricultural Q&A, support, and education.

---

## ⚙️ Tech Stack

- **FastAPI** – High-performance API framework
- **PyTorch** – For model inference
- **PIL (Pillow)** – Image preprocessing
- **LangChain** – Integrating LLMs for interaction
- **Uvicorn** – ASGI server for running FastAPI

---

## 🚀 Getting Started

### 🔧 Installation

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

## 📡 API Endpoints

### 🔍 `/predictCrop`

-   **Method**: POST
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

### 🧭 `/predictSoil`

-   **Method**: POST
-   **Description:** Identifies the type of soil from an uploaded image.
-   **Input:** An image file of soil.

### 🗃️ `/chatHistoricModel`

-   **Method**: POST
-   **Description:** Allows users to query historical agricultural data using natural language.
-   **Input:** Text query.
-   **Example:** `"What was the average rainfall in 2020?"`

### 🤖 `/chatWithLLM`

-   **Method**: POST
-   **Description:** Allows users to chat with a general purpose LLM with capabilities to upload images.
-   **Input:**
    -   `thread_id`: Thread ID for chat history.
    -   `query`: User's query to the LLM.
    -   `image` (optional): Upload an image file.

### 🌱 `/detect-weeds`

-   **Method**: POST
-   **Description:** Detects weeds in an uploaded image.
-   **Input:** An image file of a field or crop.

## 🧪 Running the Application

1.  **Start the FastAPI server:**

    ```bash
    uvicorn main:app --reload
    ```

    This command starts the server on `http://localhost:8000`.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them.
4.  Submit a pull request.

## 📄 License

This project is licensed under the MIT License.
