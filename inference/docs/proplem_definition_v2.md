# Problem Definition

# 1. Project Overview

## Project Name

NYC Taxi Fare Prediction System

## Description

Dự án xây dựng một hệ thống dự đoán giá cước taxi tại thành phố New York bằng mô hình Machine Learning đã được huấn luyện trước.

Người dùng lựa chọn điểm đón và điểm trả trực tiếp trên bản đồ. Hệ thống sẽ tự động thu thập dữ liệu, tạo các đặc trưng cần thiết, tiền xử lý dữ liệu theo đúng pipeline đã sử dụng trong quá trình huấn luyện và sử dụng mô hình Gradient Boosting để dự đoán giá chuyến đi.

Mục tiêu của dự án là triển khai một mô hình Machine Learning thành một ứng dụng web hoàn chỉnh phục vụ học phần Big Data.

---

# 2. Project Scope

Hệ thống chỉ phục vụ việc:

- dự đoán giá taxi
- minh họa quy trình triển khai Machine Learning
- triển khai API phục vụ inference

Hệ thống **không** hỗ trợ:

- đặt xe
- tìm tài xế
- thanh toán
- theo dõi chuyến đi

---

# 3. Machine Learning Problem

## Problem Type

Regression

## Target

fare_amount

## Production Model

Gradient Boosting Regressor (.pkl)

Random Forest chỉ được sử dụng trong giai đoạn so sánh mô hình và không được triển khai trong production.

---

# 4. Dataset

Dataset sử dụng:

Yellow Taxi Trip Records

Target:

fare_amount

---

# 5. Features

## Numerical Features

- trip_distance_miles
- duration_minutes
- pickup_latitude
- pickup_longitude
- dropoff_latitude
- dropoff_longitude
- est_speed
- manhattan_dist
- haversine_dist

## Categorical Features

- vendor_name
- rate_code_name
- weekday

---

# 6. System Architecture

Frontend

↓

Backend API

↓

Input Validation

↓

Feature Engineering

↓

Encoder

↓

Gradient Boosting Model (.pkl)

↓

Prediction

↓

Response

---

# 7. Frontend Requirements

Frontend có nhiệm vụ thu thập dữ liệu đầu vào từ người dùng.

## 7.1 Interactive Map

Sử dụng

- Leaflet
- OpenStreetMap

để hiển thị bản đồ.

---

## 7.2 Default Location

Website mở ra với vị trí mặc định là thành phố New York.

---

## 7.3 New York Boundary

Hiển thị ranh giới hành chính của thành phố New York (Polygon Boundary).

Mục đích:

- giúp người dùng biết phạm vi dự đoán
- tránh chọn điểm ngoài vùng dữ liệu huấn luyện

---

## 7.4 Location Restriction

Pickup và Dropoff chỉ được phép nằm trong ranh giới thành phố New York.

Nếu người dùng chọn ngoài khu vực này, hệ thống hiển thị thông báo lỗi và không cho phép gửi yêu cầu dự đoán.

Ví dụ:

Pickup location must be inside New York City.

---

## 7.5 Route Visualization

Sau khi chọn hai điểm:

- hiển thị tuyến đường
- hiển thị khoảng cách
- hiển thị thời gian di chuyển ước tính

Tuyến đường được lấy từ Routing API.

---

## 7.6 User Input

Frontend chỉ gửi:

Pickup Coordinate

Dropoff Coordinate

Vendor

Rate Code

Frontend không thực hiện bất kỳ phép tính feature engineering nào.

---

# 8. Backend Responsibilities

Backend chịu trách nhiệm toàn bộ quá trình xử lý dữ liệu.

Bao gồm:

- validate dữ liệu
- gọi Routing API
- tính toán feature
- encode dữ liệu
- load model
- dự đoán
- trả kết quả

---

# 9. Routing Service

Hệ thống sử dụng

OSRM (Open Source Routing Machine)

để lấy:

- tuyến đường
- khoảng cách thực tế
- thời gian di chuyển

OSRM được ưu tiên vì:

- miễn phí
- không cần trả phí
- phù hợp đồ án học tập

---

# 10. Feature Engineering Flow

Backend nhận:

pickup_latitude

pickup_longitude

dropoff_latitude

dropoff_longitude

↓

OSRM

↓

trip_distance_miles

↓

duration_minutes

↓

Tính:

haversine_dist

↓

manhattan_dist

↓

est_speed

↓

Lấy weekday hiện tại

↓

Ghép vendor

↓

Ghép rate_code

↓

Feature Vector

---

# 11. Model Inference

Backend load:

GradientBoosting.pkl

↓

Predict

↓

Fare Amount

---

# 12. Prediction Pipeline

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

Submit

↓

Backend

↓

Routing API

↓

Generate Features

↓

Gradient Boosting

↓

Predicted Fare

↓

Frontend

---

# 13. Functional Requirements

## Frontend

- Hiển thị bản đồ New York
- Hiển thị ranh giới New York
- Chọn Pickup
- Chọn Dropoff
- Hiển thị route
- Hiển thị khoảng cách
- Hiển thị thời gian
- Chọn Vendor
- Chọn Rate Code
- Gửi yêu cầu dự đoán
- Hiển thị giá dự đoán

---

## Backend

- Validate request
- Kiểm tra vị trí
- Gọi OSRM
- Sinh feature
- Encode dữ liệu
- Load model
- Thực hiện inference
- Trả kết quả JSON

---

# 14. API Input

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

# 15. API Output

```json
{
  "predicted_fare": 18.73,
  "currency": "USD",
  "trip_distance_miles": 4.86,
  "duration_minutes": 17.4
}
```

---

# 16. Technologies

## Frontend

- React
- Leaflet
- OpenStreetMap

## Backend

- FastAPI
- Scikit-learn
- Joblib / Pickle

## Routing

- OSRM API

## Machine Learning

- Gradient Boosting Regressor

---

# 17. Non-functional Requirements

- Response time < 2 seconds
- Chỉ hỗ trợ khu vực New York
- Có thể thay thế model mới mà không cần sửa frontend
- API độc lập với giao diện
- Feature engineering được xử lý hoàn toàn tại backend
