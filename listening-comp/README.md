## How to run frontend

```sh
streamlit run frontend/main.py
```

## How to run backend

```sh
cd backend
pip install -r requirements.txt
cd ..
python backend/main.py
```

## Setting up Gemini API Key

1. Create a `.env` file in the `backend` directory (you can copy from `.env.example`):
   ```sh
   cp backend/.env.example backend/.env
   ```

2. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. Edit the `.env` file and replace `your-gemini-api-key-here` with your actual API key:
   ```
   GOOGLE_API_KEY=your-actual-api-key
   ```

4. Make sure to keep your `.env` file secure and never commit it to version control.