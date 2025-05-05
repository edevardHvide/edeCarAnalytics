# Car Cost Comparison Tool

A Streamlit web application to analyze the 3-year cost difference between a Tesla Model Y and a Jaguar I-Pace.

## Features

- Interactive heatmap that shows cost differences across scenarios
- Adjustable parameters via sliders for Tesla depreciation and Jaguar repair costs
- Detailed cost breakdown with visualizations
- Responsive design that works on desktop and mobile devices

## Live Demo

The application is deployed on Render. You can access it here: [Car Cost Comparison Tool](https://your-render-url.onrender.com)

## Local Development

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/car-cost-comparison.git
   cd car-cost-comparison
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:
   ```
   streamlit run car_analyze_altair.py
   ```

5. Open your browser and navigate to http://localhost:8501

## Deployment on Render

1. Create a new Web Service on Render.
2. Connect your GitHub repository.
3. Use the following settings:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run car_analyze_altair.py`
4. Set the following environment variables:
   - `PYTHON_VERSION`: 3.10.0 (or your preferred version)

## Customization

You can customize the application by modifying the following:

- Default values for car costs in the sidebar
- Range of values for the sliders
- Color schemes for visualizations
- Additional analysis features

## Technologies Used

- Streamlit: Web application framework
- Altair: Data visualization library for interactive charts
- NumPy: For numerical calculations
- Pandas: For data manipulation

## License

MIT License

## Acknowledgments

- Thanks to Streamlit for making web app creation with Python so simple
- The Altair team for their excellent visualization library 