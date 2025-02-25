# Diabetes Food Advisor

A web application that helps individuals with diabetes understand the nutritional value of meals by analyzing food through image recognition or text input, providing personalized advice based on sugar content and insulin levels.

## Features

- **Dual Input Methods:**
  - Upload food images for AI-powered recognition
  - Enter food names as text
- **Nutritional Analysis:**
  - Sugar content analysis using USDA FoodData Central API
  - Combined sugar content calculation for multiple foods
- **Personalized Advice:**
  - Insulin level-adjusted recommendations
  - 5-level advice system (Danger, Caution, Average, Good, Great)
- **Modern UI:**
  - Responsive design with Tailwind CSS
  - Real-time updates with AJAX
  - Loading indicators and error handling

## Prerequisites

- Docker and Docker Compose
- USDA FoodData Central API key (get it from: https://fdc.nal.usda.gov/api-key-signup.html)
- Clarifai API key (get it from: https://portal.clarifai.com/signup)

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd diabetes-food-advisor
   ```

2. **Configure API Keys:**
   - Create a `.env` file in the root directory:
     ```
     USDA_API_KEY=your_usda_api_key_here
     CLARIFAI_API_KEY=your_clarifai_api_key_here
     ```

3. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```

4. **Apply database migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Access the application:**
   - Open your browser and navigate to `http://localhost:8000`

## Usage

1. **Text Input Method:**
   - Enter food names in the text input field, separated by commas
   - Select your current insulin level
   - Click "Analyze Food"

2. **Image Upload Method:**
   - Click the image upload field
   - Select a clear photo of the food
   - Select your current insulin level
   - Click "Analyze Food"

3. **View Results:**
   - See recognized foods (from image) or entered foods
   - View total sugar content
   - Read personalized advice based on sugar content and insulin level

## Error Handling

The application handles various error cases:
- Image upload failures
- Food recognition errors
- USDA API errors
- Missing nutrition data

## Development Notes

This is an MVP (Minimum Viable Product) version. The accuracy of food recognition and nutritional advice may be limited and should be improved in future iterations.

## Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- In production, implement proper security measures:
  - Rate limiting
  - Input validation
  - HTTPS
  - Secure headers

## API Key Setup Guide

1. **USDA FoodData Central API Key:**
   - Visit https://fdc.nal.usda.gov/api-key-signup.html
   - Fill out the registration form
   - Copy the API key from your email
   - Add it to your `.env` file as `USDA_API_KEY`

2. **Clarifai API Key:**
   - Visit https://portal.clarifai.com/signup
   - Create a new account
   - Create a new application
   - Navigate to API Keys section
   - Create a new API key with 'food-recognition' scope
   - Add it to your `.env` file as `CLARIFAI_API_KEY`

## Troubleshooting

1. **Image Upload Issues:**
   - Ensure image is in a supported format (JPG, PNG)
   - Check image size is under 10MB
   - Verify image is clear and well-lit

2. **API Errors:**
   - Verify API keys are correctly set in `.env` file
   - Check API quotas and limits
   - Ensure internet connectivity

3. **Docker Issues:**
   - Ensure Docker and Docker Compose are installed
   - Try rebuilding containers: `docker-compose down && docker-compose up --build`
   - Check Docker logs: `docker-compose logs`

## License

[MIT License](LICENSE)

## Disclaimer

This application is for informational purposes only and should not be used as a substitute for professional medical advice. Always consult with healthcare providers regarding dietary decisions. 