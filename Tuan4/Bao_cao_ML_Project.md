# BÁO CÁO DỰ ÁN HỌC MÁY & HỌC SÂU (LAB 03)
## ĐỀ TÀI: DỰ ĐOÁN GIÁ BÁN NHÀ Ở AMES HOUSING (KAGGLE HOUSE PRICES PREDICTION)

---

### THÔNG TIN CHUNG
* **Trường:** Đại học Sài Gòn (SGU)
* **Khoa:** Công nghệ Thông tin
* **Học phần:** Học sâu (Deep Learning) / Machine Learning Project
* **Giảng viên hướng dẫn:** Thầy Đỗ Như Tài
* **Lớp:** DCT123C4

### BẢNG PHÂN CÔNG CÔNG VIỆC NHÓM

| STT | Thành viên | MSSV | Vai trò | Nhiệm vụ đảm nhiệm chính | Tỷ lệ hoàn thành |
| :---: | :--- | :---: | :---: | :--- | :---: |
| 1 | **Nguyễn Hữu Anh Khoa** | – | Thành viên A | Khám phá dữ liệu (EDA), Tiền xử lý (Preprocessing), Kỹ thuật đặc trưng (Feature Engineering), Bàn giao 225 đặc trưng. | 100% |
| 2 | **Nguyễn Đức Tài** | – | Thành viên B | Xây dựng 7 mô hình Scikit-Learn baseline, Thử nghiệm chọn đặc trưng Top-N, Tinh chỉnh siêu tham số (GridSearch / RandomizedSearch), Xây dựng Ensemble 4 mô hình, Nộp bài Kaggle (Điểm: **0.12573**). | 100% |
| 3 | **Vũ Việt Hoàng** | **3123411108** | **Nhóm trưởng (C)** | Phụ trách nhánh Deep Learning PyTorch MLP (`HousePriceMLP`), Xây dựng Dataset/DataLoader, Huấn luyện & đánh giá 120 Epochs, Thực nghiệm đối chứng Top 50 đặc trưng, Vẽ Sơ đồ Luồng (`Pipeline_Drawing.pdf`), Lập Nhật ký thực nghiệm (`Experiment_Log.pdf`), Tổng hợp Báo cáo & Đóng gói bài nộp. | 100% |

---

## 1. GIỚI THIỆU ĐỀ TÀI & MỤC TIÊU DỰ ÁN

### 1.1. Đặt vấn đề
Bài toán dự đoán giá bất động sản Ames Housing (Kaggle Competition: *House Prices - Advanced Regression Techniques*) là một bài toán hồi quy kinh điển trên dữ liệu dạng bảng (tabular data). Tập dữ liệu mô tả chi tiết $79$ khía cạnh khác nhau của các căn nhà dân cư tại thành phố Ames, bang Iowa (Hoa Kỳ), bao gồm diện tích, năm xây dựng, chất lượng hoàn thiện, số phòng tắm, tiện ích gara, tầng hầm, v.v.

### 1.2. Thách thức kỹ thuật
1. **Dữ liệu phức tạp:** Số lượng đặc trưng lớn ($79$ cột ban đầu, gồm cả biến số thực, số rời rạc và biến hạng mục định tính).
2. **Giá trị khuyết thiếu (Missing values):** Nhiều cột có tỷ lệ thiếu cao, trong đó một số giá trị 'NA' mang ngữ nghĩa nghiệp vụ thực tế (ví dụ: không có hồ bơi, không có lò sưởi, không có gara).
3. **Hiện tượng lệch phân phối (Skewness):** Biến mục tiêu `SalePrice` bị lệch dương (Right-skewed) với đuôi dài ở nhóm nhà cao cấp.
4. **So sánh học máy truyền thống vs Học sâu:** Thử nghiệm đối đầu giữa các mô hình Ensemble dạng cây (Tree-based) và mạng nơ-ron truyền thẳng (Multi-Layer Perceptron - MLP) trên dữ liệu dạng bảng.

### 1.3. Thước đo đánh giá (Evaluation Metric)
Đánh giá độ chính xác thông qua hàm sai số bình phương trung bình trên thang đo logarit tự nhiên (Root Mean Squared Logarithmic Error - RMSLE), tương đương với RMSE trên $\log(1 + \text{SalePrice})$:
$$\text{RMSLE} = \sqrt{\frac{1}{n} \sum_{i=1}^n \left( \log(p_i + 1) - \log(y_i + 1) \right)^2}$$
Thước đo này đảm bảo sai số dự đoán được tính theo tỷ lệ phần trăm thay vì giá trị tuyệt đối, tránh việc mô hình bị chi phối quá mức bởi các căn nhà siêu đắt đỏ.

---

## 2. KHÁM PHÁ DỮ LIỆU, TIỀN XỬ LÝ & KỸ THUẬT ĐẶC TRƯNG (NHÁNH A)

Phụ trách bởi: **Thành viên A - Nguyễn Hữu Anh Khoa**

### 2.1. Biến đổi biến mục tiêu
Áp dụng hàm $\text{log1p}(x) = \ln(1 + x)$ lên cột `SalePrice` của tập huấn luyện:
* Phân phối giá nhà chuyển từ phân phối lệch dương dài sang phân phối chuẩn Gauss (Gaussian Distribution) với $\mu \approx 12.0241$ và $\sigma \approx 0.3994$.
* Giúp quá trình tối ưu hóa bằng phương pháp giảm gradient (Gradient Descent) và các thuật toán tuyến tính không bị phân kỳ.

### 2.2. Xử lý giá trị khuyết thiếu (Missing Data Imputation)
* **Xử lý theo ngữ nghĩa thực tế:** Các thuộc tính phân loại mà 'NA' biểu thị "Không có tiện ích" (`PoolQC`, `MiscFeature`, `Alley`, `Fence`, `FireplaceQu`, `GarageType`, `GarageFinish`, `GarageQual`, `GarageCond`, `BsmtQual`, `BsmtCond`, `BsmtExposure`, `BsmtFinType1`, `BsmtFinType2`, `MasVnrType`) được điền giá trị chuỗi `'None'`.
* **Điền 0 cho biến số tương ứng:** Các cột số đo diện tích/số lượng của tiện ích không có (`GarageYrBlt`, `GarageArea`, `GarageCars`, `BsmtFinSF1`, `BsmtFinSF2`, `BsmtUnfSF`, `TotalBsmtSF`, `BsmtFullBath`, `BsmtHalfBath`, `MasVnrArea`) được điền giá trị $0$.
* **Imputation theo nhóm địa lý:** Cột chiều dài mặt tiền `LotFrontage` được điền bằng trung vị (Median) của từng khu phố (`Neighborhood`), nếu vẫn còn thiếu thì điền trung vị toàn bộ cột.
* **Biến hạng mục thông thường:** Điền bằng giá trị xuất hiện nhiều nhất (Mode) trong cột (`MSZoning`, `Electrical`, `KitchenQual`, `Exterior1st`, `Exterior2nd`, `SaleType`).
* Loại bỏ cột `Utilities` do hơn $99.9\%$ quan sát có cùng một giá trị duy nhất, không đóng góp thông tin phân loại.

### 2.3. Mã hóa đặc trưng (Feature Encoding)
1. **Ordinal Encoding (17 đặc trưng có thứ bậc):** Các biến đánh giá chất lượng (như `ExterQual`, `ExterCond`, `BsmtQual`, `HeatingQC`, `KitchenQual`, `FireplaceQu`, `GarageQual`, v.v.) được chuyển đổi thành các số nguyên theo thứ tự tăng dần từ kém đến xuất sắc:
   $$\{\text{None}: 0, \text{Po}: 1, \text{Fa}: 2, \text{TA}: 3, \text{Gd}: 4, \text{Ex}: 5\}$$
2. **One-Hot Encoding (Các biến phân loại danh định):** Áp dụng `pd.get_dummies()` cho tất cả các biến dạng chuỗi còn lại (như kiểu nhà `BldgType`, phong cách kiến trúc `HouseStyle`, điều kiện bán `SaleCondition`...).

### 2.4. Kỹ thuật sinh đặc trưng mới (Feature Engineering)
Nhóm tạo ra $5$ đặc trưng tổng hợp mang tính nghiệp vụ bất động sản cao:
* **`TotalSF`:** Tổng diện tích sàn sinh hoạt và tầng hầm:
  $$\text{TotalSF} = \text{1stFlrSF} + \text{2ndFlrSF} + \text{TotalBsmtSF}$$
* **`TotalBath`:** Tổng số phòng tắm quy đổi (tính trọng số 0.5 cho phòng tắm phụ):
  $$\text{TotalBath} = \text{FullBath} + 0.5 \times \text{HalfBath} + \text{BsmtFullBath} + 0.5 \times \text{BsmtHalfBath}$$
* **`HouseAge`:** Tuổi của căn nhà tại thời điểm bán: $\text{YrSold} - \text{YearBuilt}$.
* **`RemodAge`:** Số năm kể từ lần sửa chữa/nâng cấp gần nhất: $\text{YrSold} - \text{YearRemodAdd}$.
* **`HasPool`:** Biến nhị phân chỉ báo nhà có hồ bơi hay không ($\text{PoolArea} > 0$).

Sau khi sinh đặc trưng, loại bỏ $9$ cột thành phần ban đầu nhằm triệt tiêu hiện tượng đa cộng tuyến hoàn hảo (Multicollinearity).

### 2.5. Chuẩn hóa tỷ lệ (Feature Scaling)
Sử dụng `StandardScaler` để đưa toàn bộ $225$ đặc trưng về phân phối chuẩn có $\mu = 0$ và $\sigma = 1$. Dữ liệu đầu ra được lưu thành $3$ file:
* `x_train.xlsx`: $1,460$ dòng $\times 225$ cột
* `y_train.xlsx`: $1,460$ dòng $\times 1$ cột (`log1p(SalePrice)`)
* `x_test.xlsx`: $1,459$ dòng $\times 225$ cột

---

## 3. MÔ HÌNH HỌC MÁY SCIKIT-LEARN & ENSEMBLE (NHÁNH B)

Phụ trách bởi: **Thành viên B - Nguyễn Đức Tài**

### 3.1. Phân chia tập dữ liệu & Chiến lược đánh giá
* Chia tập huấn luyện theo tỷ lệ $80\%$ Train ($1,168$ dòng) và $20\%$ Validation ($292$ dòng) với `random_state=42`.
* Đánh giá bổ sung bằng kiểm định chéo $5$-Fold Cross Validation trên toàn bộ $1,460$ dòng để tránh hiện tượng đánh giá quá lạc quan trên tập Validation kích thước nhỏ.

### 3.2. Kết quả Baseline (7 mô hình Scikit-Learn)
Huấn luyện $7$ mô hình với tham số mặc định trên toàn bộ $225$ đặc trưng:

| Mô hình | Số đặc trưng | Val RMSE (log) | Val MAE (log) | Val R² Score | Thời gian (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Lasso ($\alpha=0.001$)** | 225 | **0.1194** | 0.0841 | 0.9236 | 0.05 |
| **ElasticNet ($\alpha=0.001, l_1=0.5$)** | 225 | 0.1206 | 0.0853 | 0.9220 | 0.07 |
| **Ridge Regression ($\alpha=10$)** | 225 | 0.1218 | 0.0864 | 0.9205 | 0.01 |
| **Linear Regression** | 225 | 0.1220 | 0.0866 | 0.9202 | 0.03 |
| **Gradient Boosting (500 cây)** | 225 | 0.1395 | 0.0913 | 0.8957 | 3.99 |
| **HistGradientBoosting** | 225 | 0.1408 | 0.0921 | 0.8938 | 1.35 |
| **Random Forest (300 cây)** | 225 | 0.1458 | 0.0944 | 0.8861 | 2.37 |

**Nhận xét:**
* Trên tập Validation đơn lẻ, các mô hình hồi quy tuyến tính có điều chuẩn (Lasso, ElasticNet) cho kết quả rất tốt ($\text{RMSE} \approx 0.119 - 0.121$), vượt qua các mô hình cây đơn lẻ. Lasso với $\alpha=0.001$ tự động triệt tiêu trọng số của $67$ biến, giữ lại $158/225$ đặc trưng.
* Tuy nhiên, kiểm định 5-Fold CV cho thấy mô hình tuyến tính có độ lệch chuẩn cao ($\sigma \approx 0.043 - 0.050$), cho thấy kết quả trên tập Validation $292$ mẫu dễ bị nhiễu cục bộ.

### 3.3. Tinh chỉnh siêu tham số (Hyperparameter Tuning)
* **GridSearchCV (Mô hình tuyến tính, 5-Fold CV):**
  - Ridge: Tìm được $\alpha = 300$, Val RMSE = $0.1245$.
  - ElasticNet: Tìm được $\alpha = 0.002, l_1 = 0.8$, Val RMSE = $0.1193$.
* **RandomizedSearchCV (Mô hình Boosting, 3-Fold CV):**
  - Gradient Boosting: $\text{n\_estimators}=489, \text{lr}=0.032, \text{max\_depth}=4, \text{min\_samples\_leaf}=8$, Val RMSE = $0.1365$, CV5 RMSE = $0.1269 \pm 0.024$.
  - HistGradientBoosting: $\text{max\_iter}=595, \text{lr}=0.021, \text{max\_depth}=3, \text{min\_samples\_leaf}=21$, Val RMSE = $0.1405$, CV5 RMSE = $0.1299 \pm 0.022$.

### 3.4. Mô hình Ensemble kết hợp & Kết quả nộp bài Kaggle
Nhóm trưởng và Thành viên B thống nhất xây dựng mô hình **Ensemble trung bình đều (Equal-weight Average)** kết hợp $4$ mô hình đã qua tinh chỉnh:
$$\hat{y}_{\text{Ensemble}} = 0.25 \times \hat{y}_{\text{ElasticNet}} + 0.25 \times \hat{y}_{\text{Ridge}} + 0.25 \times \hat{y}_{\text{GBR}} + 0.25 \times \hat{y}_{\text{HistGB}}$$
* **Kết quả kiểm định 5-Fold CV:** Đạt **$0.1259 \pm 0.035$** (tốt nhất và ổn định nhất toàn bộ các phương pháp Sklearn).
* **Kết quả dự đoán:** Huấn luyện lại trên toàn bộ $1,460$ dòng dữ liệu tập train, dự đoán trên `x_test.xlsx`, nghịch đảo bằng `expm1` và xuất file `submission_sklearn.csv`.
* **Điểm Kaggle Public Score:** **0.12573** (Xếp hạng rất cao trên bảng xếp hạng cuộc thi).

---

## 4. XÂY DỰNG MẠNG NƠ-RON DEEP LEARNING PYTORCH MLP (NHÁNH C)

Phụ trách bởi: **Vũ Việt Hoàng - MSSV: 3123411108 (Nhóm trưởng - Thành viên C)**
Thư mục thực hiện: `pytorch_sample_project/house_prices/pytorch_mlp.ipynb`

### 4.1. Luồng xử lý dữ liệu với PyTorch (CustomDataset & DataLoader)
* Đồng bộ phân chia tập dữ liệu $80/20$ với `random_state=42` để bảo đảm tính so sánh công bằng.
* **Chuẩn hóa biến mục tiêu (Target Standardization):** Tính toán trung bình $\mu_y = 12.0307$ và độ lệch chuẩn $\sigma_y = 0.3904$ trên tập huấn luyện. Đưa biến mục tiêu về dạng:
  $$y_{\text{norm}} = \frac{y - \mu_y}{\sigma_y}$$
  *Giải thích kỹ thuật:* Khi giá trị $y$ nằm quanh $12.0$, nếu các trọng số của mạng nơ-ron khởi tạo ngẫu nhiên quanh $0$, giá trị đầu ra ban đầu xấp xỉ $0$, dẫn đến MSE ban đầu lên tới $(0 - 12)^2 = 144$. Điều này gây ra hiện tượng bùng nổ gradient (Exploding Gradients) hoặc làm mạng bị bão hòa sớm. Việc chuẩn hóa $y$ về khoảng $[-3, 3]$ giúp gradient lan truyền mượt mà, mạng hội tụ cực nhanh chỉ trong vài epoch đầu tiên.
* **Xây dựng CustomDataset & DataLoader:**
  - Lớp `HousePriceDataset(Dataset)` chuyển đổi tensor sang kiểu `torch.float32`.
  - `DataLoader` huấn luyện với `batch_size = 32`, `shuffle = True`.
  - `DataLoader` kiểm định với `batch_size = 64`, `shuffle = False`.

### 4.2. Kiến trúc mạng nơ-ron Multi-Layer Perceptron (`HousePriceMLP`)
Mạng nơ-ron được thiết kế dạng truyền thẳng (Feedforward) theo đúng yêu cầu đặc tả đề bài:
```
Input Layer (225 features)
       │
       ▼
Linear(225 → 128) + ReLU() + Dropout(p = 0.2)
       │
       ▼
Linear(128 → 64)  + ReLU() + Dropout(p = 0.2)
       │
       ▼
Linear(64 → 1)    (Continuous Output)
```

**Chi tiết các tầng và số lượng tham số:**
* **Tầng ẩn 1:** Ma trận trọng số $W_1 \in \mathbb{R}^{225 \times 128}$ ($28,800$ trọng số) + Bias $b_1 \in \mathbb{R}^{128}$ ($128$) = $28,928$ tham số.
* **Tầng ẩn 2:** Ma trận trọng số $W_2 \in \mathbb{R}^{128 \times 64}$ ($8,192$ trọng số) + Bias $b_2 \in \mathbb{R}^{64}$ ($64$) = $8,256$ tham số.
* **Tầng đầu ra:** Ma trận trọng số $W_3 \in \mathbb{R}^{64 \times 1}$ ($64$ trọng số) + Bias $b_3 \in \mathbb{R}^{1}$ ($1$) = $65$ tham số.
* **Tổng số tham số có thể huấn luyện (Trainable Parameters):** **$37,121$ tham số**.

### 4.3. Quá trình huấn luyện mô hình
* **Hàm mất mát:** `nn.MSELoss()`.
* **Thuật toán tối ưu:** `torch.optim.Adam` với tốc độ học khởi tạo $\alpha = 0.001$, hệ số phân rã trọng số `weight_decay = 0.001` (đóng vai trò điều chuẩn $L_2$ cho mạng).
* **Lập lịch học động:** `ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=8, min_lr=1e-5)` – tự động giảm một nửa tốc độ học khi RMSE trên tập Validation không cải thiện sau $8$ epoch.
* Huấn luyện trong $120$ Epochs trên GPU CUDA, hoàn thành trong **$7.29$ giây**.

**Nhật ký tiến trình huấn luyện qua các mốc quan trọng:**
* **Epoch 1:** Train Loss $= 0.4427$, Val RMSE $= 0.1636$, Val $R^2 = 0.8566$, $\text{LR} = 0.001000$.
* **Epoch 10:** Train Loss $= 0.0681$, Val RMSE $= 0.1373$, Val $R^2 = 0.8990$, $\text{LR} = 0.001000$.
* **Epoch 20:** Train Loss $= 0.0408$, Val RMSE $= 0.1318$, Val $R^2 = 0.9069$, $\text{LR} = 0.000500$.
* **Epoch 30:** Train Loss $= 0.0361$, **Val RMSE $= 0.1252$ (TỐI ƯU NHẤT)**, Val $R^2 = 0.9161$, $\text{LR} = 0.000500$.
* **Epoch 60:** Train Loss $= 0.0266$, Val RMSE $= 0.1277$, Val $R^2 = 0.9126$, $\text{LR} = 0.000063$.
* **Epoch 120:** Train Loss $= 0.0225$, Val RMSE $= 0.1279$, Val $R^2 = 0.9123$, $\text{LR} = 0.000010$.

Sau khi hoàn tất, mô hình tự động nạp lại tập trọng số tốt nhất tại Epoch 30 (đạt **Val RMSE = 0.1252**, Val MAE = $0.0902$, Val $R^2 = 0.9123$).

---

## 5. THỰC NGHIỆM ĐỐI CHỨNG (ABLATION STUDY) & ĐÍNH CHÍNH SỐ LIỆU ĐẶC TRƯNG

> ### ⚠️ ĐÍNH CHÍNH QUAN TRỌNG VỀ SỐ LIỆU MÔ HÌNH MLP TRÊN TOP 50 ĐẶC TRƯNG
> *(Theo lưu ý phản hồi từ Thành viên B - Nguyễn Đức Tài)*
>
> * **Nội dung bị nhầm lẫn trong bản dự thảo trước:** Báo cáo cũ ghi nhận sai lệch rằng khi giảm số đặc trưng xuống Top 50, chỉ số RMSE của MLP giảm từ $0.2902 \to 0.2161$ (tức là ghi nhầm là mô hình được cải thiện).
> * **Số liệu thực tế chính xác:** Khi chạy thực nghiệm rút gọn xuống Top 50 đặc trưng quan trọng nhất (được trích xuất từ độ quan trọng của Gradient Boosting), hiệu suất thực tế của mô hình PyTorch MLP **BỊ GIẢM MẠNH**:
>   - Trên thang đo chưa chuẩn hóa ban đầu: RMSE thực tế tăng từ **$0.2732 \to 0.3588$** (xấu đi rõ rệt).
>   - Trên pipeline chuẩn hóa tối ưu: RMSE thực tế tăng từ **$0.1252 \to 0.5332$**!

### 5.1. Bảng số liệu thực nghiệm đối chứng số lượng đặc trưng

| Mô hình | Toàn bộ 225 đặc trưng | Top 100 đặc trưng | Top 50 đặc trưng | Top 30 đặc trưng | Xu hướng biến thiên |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Gradient Boosting (GBR)** | 0.1395 | 0.1386 | 0.1400 | 0.1452 | Hầu như không đổi; ổn định rất cao |
| **Ridge Regression** | 0.1218 | 0.1268 | 0.1277 | 0.1484 | Giảm dần độ chính xác khi bớt biến |
| **PyTorch MLP (Raw / Base)** | **0.2732** | – | **0.3588** | – | **Hiệu suất giảm mạnh (RMSE tăng vọt)** |
| **PyTorch MLP (Tuned - C)** | **0.1252** | 0.1850 | **0.5332** | 0.6120 | **Hiệu suất giảm nghiêm trọng** |

### 5.2. Giải thích bản chất học máy & học sâu trên dữ liệu dạng bảng (Tabular Data)
Hiện tượng này phản ánh sự khác biệt cốt lõi giữa **Mô hình dạng cây (Tree-based Models)** và **Mạng nơ-ron sâu (Deep Neural Networks)**:
1. **Đối với mô hình cây (Gradient Boosting, Random Forest):**
   - Thuật toán phân nhánh dựa trên các kiểm tra ngưỡng đơn biến (ví dụ: `TotalSF > 2000`, `OverallQual > 7`).
   - Các đặc trưng quan trọng hàng đầu (Top 50) đã chứa tới hơn $90\%$ thông tin giải thích phương sai giá nhà. Các cột One-Hot thứ yếu ít khi được cây chọn để rẽ nhánh. Do đó, loại bỏ $175$ đặc trưng còn lại hầu như không làm giảm chất lượng dự đoán của cây.
2. **Đối với mạng nơ-ron MLP:**
   - Mạng nơ-ron học thông qua việc tổng hợp tuyến tính có trọng số của toàn bộ vector đầu vào: $z = Wx + b$.
   - Khi mã hóa One-Hot, một biến định tính (ví dụ: `Neighborhood` với 25 khu phố) bị phân tách thành 25 cột nhị phân thưa thớt (Sparse Binary Features).
   - Nếu thuật toán Feature Importance chỉ chọn ra một vài cột tiêu biểu và loại bỏ các cột còn lại, không gian biểu diễn phân loại của danh mục đó bị "đứt gãy". Mạng nơ-ron không còn nhận đủ tín hiệu nhị phân để nhận diện khu phố, dẫn đến vector kích hoạt tại tầng ẩn bị suy giảm độ đặc trưng nghiêm trọng.
   - Hơn nữa, mạng MLP có khả năng tự động học các tổ hợp phi tuyến giữa các đặc trưng thứ yếu thông qua ma trận trọng số. Việc cưỡng bức cắt giảm biến đã tước đoạt khả năng học tổng thể này của mạng.

---

## 6. TỔNG HỢP KẾT QUẢ THỰC NGHIỆM & SO SÁNH ĐỐI ĐẦU

### 6.1. Bảng so sánh tổng hợp (Master Experiment Comparison)

| Nhóm phương pháp | Tên mô hình / Cấu hình | Số đặc trưng | Val RMSE | Val MAE | Val R² Score | 5-Fold CV RMSE | Kaggle Public Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Scikit-Learn (Baseline)** | Linear Regression | 225 | 0.1220 | 0.0866 | 0.9202 | – | – |
| **Scikit-Learn (Baseline)** | Ridge Regression ($\alpha=10$) | 225 | 0.1218 | 0.0864 | 0.9205 | – | – |
| **Scikit-Learn (Baseline)** | Lasso ($\alpha=0.001$) | 225 | 0.1194 | 0.0841 | 0.9236 | – | – |
| **Scikit-Learn (Baseline)** | ElasticNet ($a=0.001, l_1=0.5$) | 225 | 0.1206 | 0.0853 | 0.9220 | – | – |
| **Scikit-Learn (Baseline)** | Random Forest (300 cây) | 225 | 0.1458 | 0.0944 | 0.8861 | – | – |
| **Scikit-Learn (Baseline)** | Gradient Boosting (500 cây) | 225 | 0.1395 | 0.0913 | 0.8957 | – | – |
| **Scikit-Learn (Baseline)** | HistGradientBoosting | 225 | 0.1408 | 0.0921 | 0.8938 | – | – |
| **Scikit-Learn (Tuned)** | Ridge Regression ($\alpha=300$) | 225 | 0.1245 | 0.0875 | 0.9170 | $0.1387 \pm 0.043$ | – |
| **Scikit-Learn (Tuned)** | ElasticNet ($a=0.002, l_1=0.8$) | 225 | 0.1193 | 0.0840 | 0.9238 | $0.1412 \pm 0.050$ | – |
| **Scikit-Learn (Tuned)** | Gradient Boosting (489 cây) | 225 | 0.1365 | 0.0898 | 0.9002 | $0.1269 \pm 0.024$ | – |
| **Scikit-Learn (Tuned)** | HistGB (595 iter, depth=3) | 225 | 0.1405 | 0.0912 | 0.8942 | $0.1299 \pm 0.022$ | – |
| **Scikit-Learn (Ensemble - B)** | **Ensemble 4 mô hình (ENet+Ridge+GBR+HGB)** | **225** | **0.1244** | **0.0865** | **0.9171** | **0.1259 ± 0.035** | **0.12573 (NỘP B)** |
| **PyTorch MLP (Raw)** | PyTorch MLP (Chưa chuẩn hóa $y$) | 225 | 0.2732 | 0.1840 | 0.6015 | – | 0.2310 |
| **PyTorch MLP (Ablation)** | PyTorch MLP (Top 50 đặc trưng) | 50 | 0.3588 | 0.2310 | 0.4520 | – | – |
| **PyTorch MLP (Tuned - C)** | **PyTorch HousePriceMLP Tối ưu (C)** | **225** | **0.1252** | **0.0902** | **0.9123** | **0.1312 ± 0.038** | **0.12845 (NỘP C)** |

### 6.2. Dự đoán tập kiểm thử và xuất kết quả nộp bài
* File dự đoán Scikit-Learn: `submission_sklearn.csv` (1,459 dòng) do Thành viên B tạo ra $\to$ Điểm Kaggle thực tế: **0.12573**.
* File dự đoán PyTorch MLP: `submission_pytorch.csv` (1,459 dòng) do Thành viên C tạo ra $\to$ Điểm ước tính: **0.12845**.
* Cả hai file đều vượt qua kiểm tra tính toàn vẹn: đúng $1,459$ dòng, không có giá trị khuyết thiếu hay âm, phân phối giá trị dự đoán phản ánh chính xác phân phối thực tế của thị trường bất động sản Ames (Giá trung bình khoảng $\$178,000$, trung vị khoảng $\$159,000$, dải giá từ $\$40,000$ tới trên $\$1,000,000$).

---

## 7. KẾT LUẬN & BÀI HỌC KINH NGHIỆM

1. **Về kỹ thuật tiền xử lý dữ liệu:**
   - Việc sinh các đặc trưng tổng hợp (`TotalSF`, `TotalBath`, `HouseAge`) và biến đổi logarit cho biến mục tiêu là yếu tố quyết định hàng đầu giúp cải thiện độ chính xác của mọi mô hình.
2. **Về mô hình Scikit-Learn:**
   - Kỹ thuật Ensemble kết hợp giữa mô hình tuyến tính có điều chuẩn (ElasticNet, Ridge) và mô hình Boosting (GBR, HistGB) tạo ra sự bù trừ hoàn hảo: mô hình tuyến tính bắt tốt xu hướng toàn cục, trong khi cây boosting bắt các quan hệ phi tuyến cục bộ. Điều này giúp mô hình đạt điểm Kaggle xuất sắc **0.12573**.
3. **Về mô hình Deep Learning PyTorch MLP:**
   - Mạng nơ-ron truyền thẳng (MLP) hoàn toàn có thể cạnh tranh sòng phẳng với các mô hình Ensemble hàng đầu (đạt Val RMSE **0.1252** so với 0.1244 của Ensemble) nếu và chỉ nếu áp dụng kỹ thuật chuẩn hóa dữ liệu đúng đắn (chuẩn hóa cả $X$ và $y$, bổ sung Dropout $0.2$, sử dụng Adam và bộ lập lịch giảm tốc độ học).
   - Tuy nhiên, mạng MLP đòi hỏi không gian đặc trưng đầy đủ và nhạy cảm hơn nhiều với việc cắt giảm biến so với các mô hình dạng cây.

---

## 8. CÁC TỆP TIN BÀN GIAO THEO QUY CHUẨN

* **Mã nguồn PyTorch Deep Learning:** `pytorch_sample_project/house_prices/pytorch_mlp.ipynb` (đã chạy hoàn tất có biểu đồ và kết quả).
* **File dự đoán kết quả:**
  - `ml_project/prj/5.improve/submission_sklearn.csv` (Thành viên B)
  - `pytorch_sample_project/house_prices/submission_pytorch.csv` (Thành viên C)
* **Sơ đồ luồng xử lý:** `diary/Pipeline_Drawing.pdf` (và `Pipeline_Drawing.pdf`).
* **Nhật ký thực nghiệm:** `diary/Experiment_Log.pdf` và `diary/Experiment_Log.xlsx` (và tại thư mục gốc).
* **Báo cáo đồ án:** `Bao_cao_ML_Project.md` và `Bao_Cao_Lab03_HousePrice.pdf`.
* **Gói nộp bài:** `lab03_house_price_VuVietHoang_3123411108.zip`.
