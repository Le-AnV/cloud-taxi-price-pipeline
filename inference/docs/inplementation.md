# Implementation Design

# 1. Overview

## Objective

Triển khai mô hình Machine Learning đã được huấn luyện thành một hệ thống Web Application có khả năng dự đoán giá cước taxi tại thành phố New York.

Người dùng chỉ cần lựa chọn điểm đón, điểm trả và một số thông tin bổ sung trên giao diện web. Hệ thống sẽ tự động thu thập dữ liệu, tạo các đặc trưng cần thiết và sử dụng Machine Learning Pipeline đã được huấn luyện để dự đoán giá chuyến đi.

Machine Learning Model không được huấn luyện lại trong quá trình triển khai. Hệ thống chỉ thực hiện inference.

---

# 2. System Architecture

```

┌──────────────────────────┐
│        Frontend          │
│ React + Leaflet + OSM    │
└────────────┬─────────────┘
│
│ HTTP Request
▼
┌──────────────────────────┐
│       FastAPI API        │
└────────────┬─────────────┘
│
├───────────────┐
│               │
▼               ▼
Routing API   Feature Engineering
(OSRM)
│
└───────────────┘
│
▼
Input DataFrame
│
▼
Machine Learning Pipeline (.pkl)
│
▼
Prediction
│
▼
JSON Response
│
▼
Frontend

```

---

# 3. Technology Stack

## Frontend

- React
- React Leaflet
- OpenStreetMap
- Axios

---

## Backend

- FastAPI
- Uvicorn
- Pandas
- NumPy
- Joblib
- Scikit-learn

---

## Routing Service

OSRM (Open Source Routing Machine)

Sử dụng để:

- lấy tuyến đường
- khoảng cách thực tế
- thời gian di chuyển

---

## Machine Learning

Machine Learning Pipeline

```
gradient_boosting_pipeline.pkl
```

Pipeline đã bao gồm:

- preprocessing
- encoding
- trained model

Backend chỉ cần truyền DataFrame vào pipeline.

---

# 4. Project Structure

```

project/

│

├── frontend/

│ ├── pages/

│ ├── components/

│ ├── services/

│ └── utils/

│

├── backend/

│ ├── api/

│ ├── services/

│ ├── models/

│ ├── schemas/

│ ├── utils/

│ ├── main.py

│ └── requirements.txt

│

├── model/

│ └── gradient_boosting_pipeline.pkl

│

└── docs/

├── problem_definition.md

└── implementation.md

```

---

# 5. Frontend Implementation

## Responsibilities

Frontend chỉ chịu trách nhiệm:

- hiển thị bản đồ
- nhận thao tác người dùng
- gửi request
- hiển thị kết quả

Frontend không thực hiện:

- Feature Engineering
- Encode
- Machine Learning

---

## Components

### Map Component

Hiển thị:

- OpenStreetMap
- New York Boundary
- Pickup Marker
- Dropoff Marker
- Route

---

### Control Panel

Bao gồm:

Vendor

Rate Code

Predict Button

---

### Result Panel

Hiển thị:

Estimated Fare

Trip Distance

Estimated Duration

---

# 6. Backend Implementation

Backend là nơi xử lý toàn bộ nghiệp vụ.

Bao gồm:

- Validation
- Routing
- Feature Engineering
- Model Inference
- Response

---

# 7. Routing Service

Sau khi frontend gửi:

```

pickup_lat

pickup_lon

dropoff_lat

dropoff_lon

```

Backend gọi:

OSRM Route API

Nhận về:

```

route

distance

duration

```

Frontend sử dụng route để hiển thị tuyến đường.

Backend sử dụng distance và duration để sinh feature.

---

# 8. Feature Engineering

Sau khi nhận dữ liệu từ OSRM.

Backend sinh:

## trip_distance_miles

Chuyển đổi từ mét sang miles.

---

## duration_minutes

Chuyển đổi từ giây sang phút.

---

## haversine_dist

Tính từ:

pickup

↓

dropoff

---

## manhattan_dist

Tính Manhattan Distance từ hai tọa độ.

---

## est_speed

```

est_speed =
trip_distance_miles /
(duration_minutes / 60)

```

---

## weekday

Lấy từ thời gian hiện tại của hệ thống.

---

Cuối cùng tạo DataFrame đúng schema:

```

FEATURE_NUMERIC_COLS

FEATURE_CATEGORICAL_COLS

```

---

# 9. Machine Learning Inference

Load:

```

models/random_forest_model_v2.pkl

```

Sau đó:

```

prediction =
pipeline.predict(input_dataframe)

```

Không cần:

- encode
- scale
- transform

vì toàn bộ preprocessing đã nằm trong Pipeline.

---

# 10. Request Flow

```

User

↓

Select Pickup

↓

Select Dropoff

↓

Choose Vendor

↓

Choose Rate Code

↓

Predict

↓

Frontend gửi request

↓

FastAPI

↓

Validate Input

↓

OSRM

↓

Generate Features

↓

Build DataFrame

↓

Pipeline.predict()

↓

Predicted Fare

↓

JSON

↓

Frontend

↓

Display Result

```

---

# 11. API Design

## Endpoint

POST

```

/predict

```

---

## Request

```json
{
  "pickup_latitude": 40.758896,
  "pickup_longitude": -73.98513,
  "dropoff_latitude": 40.73061,
  "dropoff_longitude": -73.935242,
  "vendor_name": "Creative Mobile Technologies",
  "rate_code_name": "Standard Rate"
}
```

---

## Response

```json
{
  "predicted_fare": 18.73,
  "trip_distance_miles": 4.83,
  "duration_minutes": 17.52
}
```

---

# 12. Validation

Backend kiểm tra:

- Có đủ dữ liệu
- Latitude hợp lệ
- Longitude hợp lệ
- Pickup nằm trong New York
- Dropoff nằm trong New York
- Vendor hợp lệ
- Rate Code hợp lệ

Nếu không hợp lệ:

HTTP 400

---

# 13. Error Handling

## Routing API Error

Trả về:

```
Unable to calculate route.
```

---

## Invalid Location

```
Pickup or Dropoff must be inside New York City.
```

---

## Invalid Vendor

```
Invalid vendor.
```

---

## Invalid Rate Code

```
Invalid rate code.
```

---

## Model Error

```
Prediction failed.
```

---

# 14. Sequence Diagram

```

Frontend

│

│ POST /predict

▼

Backend

│

├── Validate

│

├── Call OSRM

│

├── Feature Engineering

│

├── Create DataFrame

│

├── Pipeline.predict()

│

└── Return JSON

│

▼

Frontend

│

Display Result

```

---

# 15. Future Improvements

## Routing

- Self-hosted OSRM
- GraphHopper
- Valhalla

---

## Machine Learning

- Model Versioning
- MLflow
- Explainable AI (SHAP)

---

## Backend

- Docker
- Redis Cache
- Logging
- Monitoring
- Unit Test

---

## Frontend

- Dark Mode
- Search Address
- Current Location
- Responsive UI
- Loading Animation

---

# 16. Deployment Workflow

```

User

↓

React Frontend

↓

FastAPI

↓

OSRM

↓

Feature Engineering

↓

Machine Learning Pipeline

↓

Prediction

↓

Frontend

↓

Estimated Fare

```

---

# 17. Expected User Experience

1. Người dùng mở website.

2. Bản đồ New York được hiển thị.

3. Người dùng chọn Pickup.

4. Người dùng chọn Dropoff.

5. Hệ thống hiển thị tuyến đường.

6. Người dùng chọn Vendor.

7. Người dùng chọn Rate Code.

8. Người dùng nhấn **Predict Fare**.

9. Backend xử lý dữ liệu và thực hiện dự đoán.

10. Website hiển thị:

- Giá dự đoán (USD)
- Quãng đường (mile)
- Thời gian di chuyển (phút)
- Tuyến đường trên bản đồ
