# weather_forecast
Weather forecast for Stockholm using machine learning

Plan:
  1. Gather data from the SMHI database: temperature (deg C), pressure (Pa), humidity (%), rain (mm)
  2. Do some simple predictions using only Stockholm's data and simple time series prediction algorithms (using each variable separately)
    - Naive approach
    - Holts winters seasonal method (able to capture level trend and seasonal components)
  3. Try those with daily and hourly data
  4. Use all variables to predict the next value of a given variable -> multiple linear regression, neural network. Try daily and hourly
  5. Add the data from several weather stations around Stockholm and do more stuff...
  
  
