# Automatic-Data-Analytics-with-NLP

**AI-Powered Data Analytics Platform with NLP Chatbot for Interactive Insights.**

This project provides a web platform for data analysis, allowing users to upload datasets, generate visualizations, and interact with their data using natural language queries powered by an AI chatbot.

**Features:**

*   Data Upload & Processing (CSV, Excel, JSON formats) with automatic schema detection and type inference.
*   Automated Analysis: Summary statistics, visualizations, pattern and anomaly detection.
*   AI-Powered Data Summarization: Generates concise summaries using the OpenRouter API.
*   Advanced Filtering: Apply complex, multi-condition filters via natural language or structured queries.
*   NLP Chatbot: Natural language interaction for data exploration and manipulation.
*   Interactive Dashboard: Real-time filtering, sorting, and export options with various chart types.
*   Secure API Integration: AI and data operations are performed securely.
*   User Reviews: Collect and display user feedback.
*   Extensible Architecture: Modular design for easy integration of new features.

### Setup and API Key Configuration

This project uses the OpenRouter API for AI functionalities. You need to obtain your own API key and configure it for the application to work.

1.  **Get your OpenRouter API Key:**
    *   Visit the [OpenRouter website](https://openrouter.ai).
    *   Sign up or log in.
    *   Generate a new API key.
    *   Replace the key in 3 files.

2.  **Configure the API Key:**
    *   Create a file named `.env` in the root directory of this project (where `main.py` is located).
    *   Add the following line to the `.env` file, replacing `YOUR_OPENROUTER_API_KEY` with the key you obtained:

        ```
        OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
        ```

    *   This key is used in `backend/utils/openrouter_client.py` (which is called by `backend/utils/nlp_routes.py`).

3.  **Test the API Connection (Optional but Recommended):**
    *   Navigate to the `backend/utils` directory.
    *   You can test the API connection by running the `testapi.py` script.
    *   **Note:** The `testapi.py` script currently has a hardcoded API key for simple testing. For this script to work after setting up your `.env` file, you should also replace the hardcoded key in `backend/utils/testapi.py` with your new key.

    ```bash
    python backend/utils/testapi.py
    ```

    *   If the connection is successful, you should receive a simple response from the API.

### Running the Application

To run the application, follow these steps:

1. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Run the main Flask application file:

    ```bash
    python main.py
    ```
