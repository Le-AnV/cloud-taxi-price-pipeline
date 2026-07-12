# Problem Definition

## 1. Project Overview

Xây dựng một hệ thống Machine Learning có khả năng dự đoán giá cước (fare amount) của một chuyến taxi tại thành phố New York.

Hệ thống sử dụng dữ liệu lịch sử của bộ dữ liệu **Yellow Taxi Trip Records** để huấn luyện mô hình hồi quy (Regression Model). Sau khi triển khai, người dùng chỉ cần chọn điểm đón và điểm trả trên bản đồ cùng một số thông tin bổ sung, hệ thống sẽ dự đoán mức giá ước tính của chuyến đi.

Mục tiêu của hệ thống là cung cấp mức giá tham khảo nhanh chóng trước khi người dùng đặt chuyến.

---

# 2. Business Problem

Người dùng thường không biết trước giá của chuyến taxi trước khi đặt xe.

Việc xây dựng mô hình dự đoán giá giúp:

- Ước lượng chi phí trước chuyến đi.
- So sánh giá giữa các tuyến đường.
- Hỗ trợ lập kế hoạch chi tiêu.
- Minh họa khả năng ứng dụng Machine Learning vào bài toán thực tế.

---

# 3. Machine Learning Problem

## Problem Type

Regression

## Target Variable

```
fare_amount
```

Đây là giá cước của chuyến taxi cần được dự đoán.

---

# 4. Input Features

## Numerical Features

| Feature             | Description                      |
| ------------------- | -------------------------------- |
| trip_distance_miles | Quãng đường di chuyển (mile)     |
| duration_minutes    | Thời gian ước tính của chuyến đi |
| pickup_latitude     | Vĩ độ điểm đón                   |
| pickup_longitude    | Kinh độ điểm đón                 |
| dropoff_latitude    | Vĩ độ điểm trả                   |
| dropoff_longitude   | Kinh độ điểm trả                 |
| est_speed           | Vận tốc trung bình ước tính      |
| manhattan_dist      | Khoảng cách Manhattan            |
| haversine_dist      | Khoảng cách Haversine            |

---

## Categorical Features

| Feature        | Description    |
| -------------- | -------------- |
| rate_code_name | Loại giá cước  |
| vendor_name    | Hãng taxi      |
| weekday        | Thứ trong tuần |

---

# 5. User Input Flow

Người dùng sẽ không nhập trực tiếp các feature.

Thay vào đó, hệ thống sẽ tự động sinh các feature từ thao tác của người dùng trên website.

## Bước 1

Người dùng chọn:

- Điểm đón (Pickup)
- Điểm trả (Dropoff)

trên bản đồ.

---

## Bước 2

Hệ thống lấy:

- pickup_latitude
- pickup_longitude
- dropoff_latitude
- dropoff_longitude

---

## Bước 3

Từ hai tọa độ, hệ thống tính:

- Haversine Distance
- Manhattan Distance
- Trip Distance

Trip Distance có thể được lấy từ dịch vụ Routing API thay vì chỉ tính khoảng cách đường chim bay.

---

## Bước 4

Hệ thống ước lượng:

```
duration_minutes
```

Có thể sử dụng:

- Routing API
- OSRM
- Mapbox Directions API
- Google Directions API

Nếu không sử dụng API, có thể ước lượng bằng:

```
duration = distance / average_speed
```

---

## Bước 5

Sau khi có:

- trip_distance
- duration

Hệ thống tính:

```
est_speed =
trip_distance / (duration / 60)
```

---

## Bước 6

Người dùng lựa chọn:

- Vendor
- Rate Code

---

## Bước 7

Hệ thống tự lấy:

```
weekday
```

từ thời gian hiện tại của server.

---

# 6. Feature Generation Flow

```
Pickup Point
        │
        ▼
Coordinates
        │
        ▼
Calculate Distance
        │
        ├── Haversine Distance
        ├── Manhattan Distance
        └── Trip Distance
        │
        ▼
Estimate Duration
        │
        ▼
Calculate Estimated Speed
        │
        ▼
Collect Vendor
Collect Rate Code
Current Weekday
        │
        ▼
Feature Vector
        │
        ▼
ML Model
        │
        ▼
Predicted Fare
```

---

# 7. Machine Learning Pipeline

## Offline Training

Dataset

↓

Data Cleaning

↓

Feature Engineering

↓

Model Training

↓

Model Evaluation

↓

Save Best Model

↓

Model Registry

---

## Online Inference

User

↓

Frontend

↓

Collect Features

↓

Generate Additional Features

↓

Load Trained Model

↓

Predict Fare

↓

Return Estimated Fare

---

# 8. Model Training

Các mô hình được huấn luyện:

- Random Forest Regressor
- Gradient Boosting Regressor

Các mô hình được đánh giá trên cùng tập Test.

Các metric sử dụng:

- RMSE
- MAE
- R²

Sau khi so sánh, mô hình có hiệu năng tốt nhất sẽ được chọn để triển khai.

Trong trường hợp hiện tại:

**Gradient Boosting Regressor** được sử dụng làm Production Model.

Random Forest chỉ được giữ lại phục vụ mục đích so sánh và đánh giá.

---

# 9. Prediction Flow

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

Backend

↓

Calculate Coordinates

↓

Calculate Distance

↓

Estimate Duration

↓

Estimate Speed

↓

Get Current Weekday

↓

Build Feature Vector

↓

Gradient Boosting Model

↓

Predicted Fare

↓

Return Response
```

---

# 10. Functional Requirements

Hệ thống cần hỗ trợ các chức năng sau:

### Frontend

- Hiển thị bản đồ New York.
- Cho phép chọn điểm đón.
- Cho phép chọn điểm trả.
- Chọn Vendor.
- Chọn Rate Code.
- Hiển thị giá dự đoán.

---

### Backend

- Nhận request từ frontend.
- Sinh các feature cần thiết.
- Kiểm tra dữ liệu đầu vào.
- Chuẩn hóa dữ liệu theo pipeline đã huấn luyện.
- Thực hiện dự đoán.
- Trả kết quả về frontend.

---

### Machine Learning

- Load Production Model.
- Thực hiện inference.
- Trả về giá dự đoán.

---

# 11. Non-functional Requirements

- Thời gian phản hồi dưới 2 giây.
- Dự đoán ổn định.
- Có khả năng mở rộng.
- API dễ tích hợp.
- Có thể thay thế model mà không cần sửa frontend.

---

# 12. Input Example

```json
{
  "pickup_latitude": 40.758,
  "pickup_longitude": -73.9855,
  "dropoff_latitude": 40.7306,
  "dropoff_longitude": -73.9352,
  "trip_distance_miles": 4.7,
  "duration_minutes": 18,
  "est_speed": 15.6,
  "manhattan_dist": 5.3,
  "haversine_dist": 4.6,
  "vendor_name": "Creative Mobile Technologies",
  "rate_code_name": "Standard Rate",
  "weekday": "Monday"
}
```

---

# 13. Output Example

```json
{
  "predicted_fare": 21.84,
  "currency": "USD"
}
```

---

# 14. Scope

## Included

- Machine Learning Model
- Backend Prediction API
- Feature Engineering
- Map-based User Input
- Fare Prediction

## Excluded

- Thanh toán.
- Đặt xe.
- Theo dõi tài xế.
- Tối ưu tuyến đường.
- Dự đoán thời gian giao thông theo thời gian thực.

---

# 15. Future Improvements

Trong các phiên bản tiếp theo có thể mở rộng bằng cách bổ sung:

- Traffic Level.
- Weather Data.
- Holiday Indicator.
- Rush Hour Indicator.
- Airport Detection.
- Toll Estimation.
- Dynamic Pricing.
- ETA Prediction.
- Real-time Routing API.
