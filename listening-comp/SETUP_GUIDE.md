# Setup Guide for JLPT Listening Practice App

## Setting up Google API Key

To run this application, you need to set up a Google API key for Gemini and Google Cloud Text-to-Speech:

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Create a `.env` file in the `backend` directory with the following content:
   ```
   GOOGLE_API_KEY=your-actual-api-key
   ```
   Replace `your-actual-api-key` with the API key you obtained from Google AI Studio.

3. Make sure the API key has access to:
   - Google Gemini API
   - Google Cloud Text-to-Speech API

## Running the Application

1. Set up a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required packages:
   ```sh
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

3. Start the Streamlit server:
   ```sh
   cd frontend
   streamlit run main.py --server.headless=true
   ```

4. Access the application at http://localhost:8501
