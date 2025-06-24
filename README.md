Project Title – AIR QUALITY PREDICTOR AND ANALYZER 

https://aqi-predictor-and-analyazer-27dsjpydrtqsqd5ieuwpuh.streamlit.app/ to run a app in streamlit.
<b><u>Problem Statement:</u></b>
Air pollution poses a serious threat to human health, especially in urban environments where 
industrial emissions, vehicular exhaust, and climate factors can cause a spike in harmful air 
pollutants. In India, the Air Quality Index (AQI) is a key metric used to assess the health impact 
of ambient air. 
However, most people don’t have real-time or localized access to AQI data, nor do they 
understand the implications of different pollutant levels. There is a need for an intelligent, 
accessible system that can predict, analyze, and visualize AQI based on location and time, and 
provide actionable advisory. 
<b><u>Statement:</u><b>
Design and develop an AI-powered web-based application using Machine Learning to predict, 
analyze, and visualize the Air Quality Index (AQI) across Indian cities using historical pollutant 
data, and offer public health insights with interactive advisory.

<b><u>Methodology Used: </u></b>
1.  Data Collection & Preprocessing: 
  • Source: Historical AQI and pollutant data from various Indian cities (from Jan 
  2023 to May 2025). 
  • Attributes: PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, 
  Toluene, Xylene, AQI Level, AQI Value, City, Date. 
2. Model Training: 
  • Features selected: All pollutants except AQI and AQI Level. 
  • Target variable: AQI value (numeric). 
  • Scaler: Standard Scaler applied for normalization. 
  • ML Model: Random Forest Regressor trained to predict AQI. 
  • Evaluation: Achieved R² score ≈ 0.9998 (indicating excellent performance). 
  • Exported model and scaler using joblib (.pkl files). 
3. Streamlit Web Application: 
  • Developed an interactive frontend where users can: 
  ▪ Select Year, Date, City. 
  ▪ View pollutant data and AQI level. 
  ▪ See a pie chart of pollutant concentrations (PM2.5, PM10, NO2, CO, O3). 
  ▪ Receive a health notification based on AQI level. 
  • Optional ML integration: Use live inputs to predict AQI using the trained model. 
4.  Visualization: 
  • Pie charts to show pollutant proportions. 
  • Bar charts, 3D charts, radar, scatter, and bubble charts for deeper insights. 
  • Visual alerts and textual advisory based on AQI categories (Good to Severe).
![Screenshot (7)](https://github.com/user-attachments/assets/f9d51b1d-db67-4cf4-bd97-fb448d1d085f)
![Screenshot (6)](https://github.com/user-attachments/assets/c27216f6-a094-4c2f-8f0f-02936f4d6f98)
![Screenshot (5)](https://github.com/user-attachments/assets/866bd317-760b-47f4-9efc-d53cf1eaee86)
![Screenshot (4)](https://github.com/user-attachments/assets/77fa237b-2b97-47b6-8406-9645509dff86)
![Screenshot (3)](https://github.com/user-attachments/assets/c9adc614-5b08-4051-a8aa-b4406fe90ad9)


![Screenshot (7)](https://github.com/user-attachments/assets/153e58ed-2ab0-4e4c-87f6-672876f960c2)

