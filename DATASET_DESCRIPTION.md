# Dataset Description of the Commute Health Study

## Dataset Structure
- **Records**: 713 individuals
- **Variables**: 8 (5 continuous and 3 categorical variables)

## Overview
This document provides a comprehensive description of the synthetic dataset contained in `syn_dataset.csv`. The dataset contains 713 observations across 8 variables, with a focus on physical activity metrics and commuting patterns.

## Variables

### VO2max
- **Type**: Float
- **Description**: Maximum oxygen consumption during exercise, measured in milliliters of oxygen per kilogram of body weight per minute (ml/kg/min). VO2max is a key indicator of cardiorespiratory fitness and aerobic endurance. Higher values indicate better cardiovascular fitness.

### CommToSch
- **Type**: String
- **Description**: Mode of commuting to school. Contains the categorical values "walk", "wheels", "car" and "public".

### CommHome
- **Type**: String
- **Description**: Mode of commuting from school to home. Contains the categorical values "walk", "wheels", "car" and "public". This may differ from CommToSch if students use different transportation methods for their return journey.

### gender
- **Type**: String
- **Description**: Gender of the participant. Contains categories "male" and "female".

### age
- **Type**: Float
- **Description**: Age of the participant in years. The float type suggests precision beyond whole years (e.g., 12.5 years).

### MVPAsqrt
- **Type**: Float
- **Description**: Square root transformed value of Moderate to Vigorous Physical Activity. The square root transformation is commonly applied to normalize skewed physical activity data. This represents the amount of meaningful physical activity performed, transformed for statistical analysis.

### DistFromHome
- **Type**: Integer
- **Description**: Distance from participant's home to their school, measured in meters.

### DistFromSchool
- **Type**: Integer
- **Description**: Distance from school to participants homes, measured in meters.


