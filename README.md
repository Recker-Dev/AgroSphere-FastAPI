# 🌾 AgroSphere-FastAPI

AgroSphere-FastAPI is a backend application built with FastAPI to empower the agricultural ecosystem through intelligent automation. It assists farmers and researchers by recommending crops, detecting soil and weed types from images, and enabling interactive access to historical agricultural data using generative AI.

---

## 🧠 Key Features

* **🌱 Crop Recommendation**
    Input soil parameters like Nitrogen, Phosphorus, Potassium, temperature, humidity, pH, and rainfall to receive tailored crop suggestions for your land.

* **🧪 Soil Type Detection**
    Upload an image of soil, and the model will classify the type of soil, aiding in better agricultural decisions.

* **📊 Historical Data Interaction** (Need Work, breaks a lot)
    Query past agricultural data using natural language. A language model understands your question and retrieves insightful responses from historical datasets.

* **🌿 Weed Detection**
    Upload an image of a field, and the system will detect and highlight weed-infested regions for targeted removal.

* **💬 Multi-Modal LLM Chat**
    Chat with a general-purpose language model using both text and image inputs. Ideal for agricultural Q&A, support, and education.

---

## ⚙️ Tech Stack

* **PyTorch** – For model development and inference.
* **FastAPI** – High-performance API framework
* **Langgraph** – Integrating Agentic Workflows for interaction
* **Docker / Docker Compose** – Containerization for deployment
* **Cloudflare Tunnel** – Secure remote access for deployed environments

---

## 🚀 Getting Started

### 🔧 Installation (Local Development)

This section guides you through setting up and running the application directly on your machine, **without using Docker**, ideal for local development and testing.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Recker-Dev/AgroSphere-FastAPI.git
    cd AgroSphere-FastAPI
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables:**
    Create a `.env` file in the root of your `AgroSphere-FastAPI` directory.
    ```env
    # Example .env file content
    GOOGLE_API_KEY=your_google_api_key_here
    GROQ_API_KEY=your_groq_api_key_here
    HF_TOKEN=your_hugging_face_api_key
    
    ## Google Service accounts details (JSON) in a Base64 format.
    ## (OPTIONAL -> if using on local machine/ self-deployed local server,
    ## needed for using Gemini in OnRender or equivalent services)
    ## Just do not pass credentials=creds for {ChatGoogleGenerativeAI(...,credentials=creds)}
    ## wherever llm_gemini is defined in the project. Need active editing done in src folder.
    
    ## But why base64?? Just upload the JSON?? I couldn't figure our how to upload the JSON
    ## on-render(yes i tried still couldn't), kinda pissed me off and took a lot of time to figure the alternative (self-hosting).
    ## But ye it works without needing creds in local setup, or atleast if you can upload the service-account json somehow in cloud infra.
    
    GOOGLE_CREDENTIALS_BASE64=your_google_service_account_detais_in_b64
    ```
4. **Running the server:**
   ```bash
   uvicorn main:app --reload
   ```
---

### 🐳 Deployment with Docker Locally
You can also run the AgroSphere-FastAPI application locally using Docker Compose, without relying on Cloudflare Tunnel. This exposes the application's port directly to your host machine, making it accessible via `localhost`.

1.  **Ensure Docker and Docker Compose are installed** on your local machine.

2.  **Configure Environment Variables:**
    Ensure your `.env` file is present in the root of your `AgroSphere-FastAPI` directory (as described in the "Deployment" section).

3.  **Modify `docker-compose.yml` for Local Exposure:**
    Open your `docker-compose.yml` file and **uncomment** the `ports` section for the `api` service. Also, **comment out** the `networks` sections, as they are not needed for a simple local direct exposure.

    ```yaml
    # docker-compose.yml (for local Docker testing)
    version: '3.8'

    services:
      api:
        build:
          context: .
          dockerfile: Dockerfile
        container_name: agrosphere-api
        # Uncomment this section to expose port 8000 to your host machine
        ports:
          - "8000:8000"
        env_file:
          - .env
        command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        # Comment out the networks section for direct local exposure
        # networks:
        #   - projects-net 

    # Comment out the top-level networks section for direct local exposure
    # networks:
    #   projects-net:
    #     external: true
    ```

4.  **Build and Run the Docker Container:**
    Navigate to the `AgroSphere-FastAPI` directory and run:
    ```bash
    sudo docker compose build
    sudo docker compose up -d
    ```
    This will build the image and start the container, making the API accessible at `http://localhost:8000` on your host machine.

---

### 🐳 Deployment with Docker & Cloudflare Tunnel (Recommended for Production)

For deploying AgroSphere-FastAPI securely to a server (like a Raspberry Pi) and making it accessible remotely **using Docker**, without exposing ports directly to the internet, we recommend integrating with a Cloudflare Tunnel.

1.  **Ensure Docker and Docker Compose are installed** on your target server and Cloudflare Tunnel is setup between your domain and server, research the topic on your own, or use can use this Guide from [TechDox](https://youtu.be/gpWo94XXrhU?si=OKePPdHe3MTqgr9d) as a starting point.

2.  **Create your shared Docker network:**
    Why Shared Network? -> It's better than exposing ports, but this will only work when your cloudflare tunnel container is in the same network, as your project container.
    This network (`projects-net`) acts as an internal communication channel for your Dockerized applications and your Cloudflare Tunnel client. You only need to run this command once on your server:
    ```bash
    sudo docker network create projects-net
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root of your `AgroSphere-FastAPI` directory. This file will be automatically picked up by Docker Compose.
    

4.  **Build and Run the AgroSphere-FastAPI Container:**
    Navigate to the `AgroSphere-FastAPI` directory on your server and use Docker Compose:
    ```bash
    sudo docker compose build
    sudo docker compose up -d
    ```
    This command will build the Docker image (if not already built) and start the `agrosphere-api` container. It will be connected to the `projects-net` network, but **its port will NOT be exposed to the host machine's network**, ensuring a secure deployment.

5.  **Set up your Cloudflare Tunnel (Separate Configuration):**
    You will need your own domain name, before even beginning and it needs to be configured to your cloudflare account, and namespaces need to be as given by cloudflare.
    Once setup of a tunnel is done, you will get a TUNNEL_TOKEN. Ex: docker run cloudflare/cloudflared:latest tunnel --no-autoupdate run --token <TUNNEL_TOKEN>. U can run this command with a -d flag, but i like to copy my token and carry the steps below.
    Your Cloudflare Tunnel client should be configured in its *own* Docker Compose setup (e.g., `cloudflare-tunnel` service in a separate `docker-compose.yml`). This tunnel container must also be connected to the `projects-net` network.

    Inside your Cloudflare Tunnel's `config.yml` (which you'd typically mount as a volume to your tunnel container), you would define rules to route public traffic to your `agrosphere-api` service. For example:
    ```yaml
    services:
      cf-tunnel-projects:
        image: cloudflare/cloudflared:latest
        container_name: cf-tunnel-projects-container
        restart: unless-stopped
        ## Remove  --protocol http2 to have a UDP connection over TCP, TCP tunnels generally dont face firewalls.
        command: tunnel --no-autoupdate run --protocol http2 
        environment:
          - TUNNEL_TOKEN=${TUNNEL_TOKEN}
        networks:
          - projects-net

    networks:
      projects-net:
        external: true
    ```
    Then run (same folder as docker compose):
    ```bash
    sudo TUNNEL_TOKEN=your_token docker compose up -d
    ```
---

## 📡 API Endpoints

* **Method**: POST
* **Description:** Recommends the most suitable crop based on the provided soil parameters.
* **Input:** JSON payload with soil parameters (N, P, K, temperature, humidity, pH, rainfall).
* **Example:**

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

* **Method**: POST
* **Description:** Identifies the type of soil from an uploaded image.
* **Input:** An image file of soil.

### 🗃️ `/chatHistoricModel`

* **Method**: POST
* **Description:** Allows users to query historical agricultural data using natural language.
* **Input:** Text query.
* **Example:** `"What was the average rainfall in 2020?"`

### 🤖 `/chatWithLLM`

* **Method**: POST
* **Description:** Allows users to chat with a general purpose LLM with capabilities to upload images.
* **Input:**
    * `thread_id`: Thread ID for chat history.
    * `query`: User's query to the LLM.
    * `image` (optional): Upload an image file.

### 🌱 `/detect-weeds`

* **Method**: POST
* **Description:** Detects weeds in an uploaded image.
* **Input:** An image file of a field or crop.

---

## 🧪 Running the Application

### Running Locally (for Development)

1.  **Activate your virtual environment:**
    ```bash
    source venv/bin/activate # On Linux/macOS
    venv\Scripts\activate   # On Windows
    ```

2.  **Start the FastAPI server:**
    ```bash
    uvicorn main:app --reload
    ```
    This command starts the server on `http://localhost:8000`, accessible directly from your machine.

### Running in Production (via Docker & Cloudflare Tunnel)

Once deployed via Docker Compose as described in the "Deployment" section above, your application will be running inside the `projects-net` Docker network. It will not be directly accessible via `localhost:8000` on your server, unless you comment out the networks part and expose ports directly in the docker-compose file.

Instead, you will access the API endpoints through the public domain configured with your Cloudflare Tunnel (e.g., `https://agrosphere.yourdomain.com/predictCrop`).

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.

2.  Create a new branch for your feature or bug fix.

3.  Make your changes and commit them.

4.  Submit a pull request.

## 📄 License

This project is licensed under the MIT License.
