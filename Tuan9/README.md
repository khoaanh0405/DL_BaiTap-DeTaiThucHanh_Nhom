# BTL01 – Xấp xỉ hàm bằng mạng MLP trong PyTorch

## 1. Giới thiệu dự án

Dự án sử dụng mạng MLP được xây dựng bằng PyTorch để xấp xỉ hàm mật độ phân phối Gaussian hai biến theo đề bài trong file `MLP_Exercise - Yeu Cau.pdf`.

Dự án bao gồm:

- Tạo dữ liệu và phân tích dữ liệu (EDA).
- Chuẩn hóa dữ liệu đầu vào, chỉ dùng tập huấn luyện để tính tham số chuẩn hóa.
- Xây dựng mô hình `torch.nn.Module` có thể tùy chỉnh.
- Huấn luyện và đánh giá mô hình trên tập train/validation.
- Lưu mô hình và thực hiện các thử nghiệm A, B, C.
- Lưu kết quả dưới dạng CSV và biểu đồ.
- Đánh giá cuối cùng trên tập test chưa từng sử dụng.
- Tạo file Excel ghi chép thí nghiệm, báo cáo và slide.

## 2. Bài toán

Hàm cần xấp xỉ là mật độ phân phối Gaussian hai biến:

Các tham số:

- Trung bình: `mu = [0, 0]`
- Ma trận hiệp phương sai: `C = [[0.3, -0.5], [-0.5, 2.0]]`
- Miền giá trị của `x1`: `-2 <= x1 <= 2`
- Miền giá trị của `x2`: `-4 <= x2 <= 4`

Đầu ra của mô hình là một giá trị mật độ (scalar). Cả hai biến đầu vào đều được giữ lại vì chúng cùng xác định hàm mục tiêu.

## 4. Tạo và chia dữ liệu

Ba tập dữ liệu được tạo độc lập từ cùng một miền đầu vào:

| Tập dữ liệu | Số mẫu | Seed | Mục đích                                  |
|---          |---     |---   |---                                        |
| Train       | 2.000  | 2026 | Huấn luyện mô hình                        |
| Validation  | 500    | 2027 | Dừng sớm và chọn mô hình                  |
| Test        | 100    | 2028 | Đánh giá cuối cùng sau khi chọn kiến trúc |

Trong thử nghiệm A, các tập con có số lượng mẫu tăng dần được lấy từ một hoán vị cố định của tập train.

Ba seed dùng trong các thử nghiệm là `42`, `123` và `2026`. 

## 5. Môi trường và cài đặt

Yêu cầu khuyến nghị:

- Python 3.10 trở lên
- PyTorch 2.x
- NumPy, Pandas, SciPy, Matplotlib
- Jupyter / IPython (không bắt buộc, dùng cho notebook)
- `python-docx` và `python-pptx` để tạo lại báo cáo và slide
- LibreOffice hoặc phần mềm văn phòng tương thích để xuất DOCX/PPTX sang PDF
- Các file Excel `.xlsx` đã được tạo bằng `artifact_tool` và có sẵn trong gói dự án

Cài đặt các thư viện cần thiết:

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## 6. Chạy các thử nghiệm

Chạy riêng từng nhóm để dễ kiểm tra kết quả:

```bash
python src/run_experiments.py A
python src/run_experiments.py B
python src/run_experiments.py C
python src/run_experiments.py finalize
python src/make_figures.py
python tests/test_core.py
```

Kiểm tra mô hình đã chọn với các điểm đầu vào tùy ý:

```bash
python src/predict_example.py --points "0,0;1,1;-1,2"
```

Hoặc chạy toàn bộ quy trình theo thứ tự:

```bash
python run_all.py
```

### Cách chọn và huấn luyện mô hình cuối cùng

Lệnh `finalize` chọn kiến trúc dựa trên **MSE trung bình của tập validation** qua ba seed. Nếu hai kiến trúc có kết quả bằng nhau, ưu tiên kiến trúc có ít tham số cần huấn luyện hơn.

Sau khi chọn kiến trúc, chương trình huấn luyện lại mô hình với thời gian dài hơn và đánh giá một lần trên tập test chưa sử dụng.

Cấu hình cho các thử nghiệm A/B/C:

- Số epoch tối đa: 100
- Batch size: 256
- Bộ tối ưu: Adam
- Learning rate: 0.02
- Weight decay: `1e-5`
- Hàm kích hoạt ở các lớp ẩn: `tanh`
- Lớp đầu ra: tuyến tính
- Early stopping patience: 20

Cấu hình huấn luyện lại mô hình cuối cùng:

- Số epoch tối đa: 400
- Early stopping patience: 40

## 7. Cấu trúc thư mục

```text
BTL01_Nhom_HoTen_MSSV/
├── data/                      # Các file CSV train/validation/test độc lập
├── exps_/data/                # Workbook và dữ liệu xuất phục vụ kiểm tra dữ liệu
├── exps_/feature1/             # Kết quả chuẩn hóa và ghi chú
├── prj/
│   ├── 1.EDA/                 # Notebook phân tích dữ liệu
│   ├── 2.pre-processing/      # Notebook tiền xử lý dữ liệu
│   ├── 3.feature_selection/   # Notebook phân tích và giải thích đặc trưng
│   ├── 4.model/               # Notebook mô hình MLP cơ sở
│   └── 5.improve/             # Notebook thử nghiệm A/B/C
├── src/                       # Mã nguồn, dự đoán và tạo tài liệu
├── logs/                      # Chỉ số và lịch sử huấn luyện
├── results/                   # Kết quả tổng hợp và dự đoán trên tập test
├── models/                    # Các checkpoint và mô hình cuối cùng
├── figures/                   # Biểu đồ dùng trong báo cáo
├── reports/                   # Báo cáo, slide và file Excel ghi chép
├── tests/                     # Kiểm tra mô hình và tính toán
├── config.json                # File cấu hình thí nghiệm
├── requirements.txt           # Danh sách thư viện
└── run_all.py                 # Chạy toàn bộ quy trình
```

## 8. Các file kết quả

Sau khi chạy chương trình, các kết quả chính gồm:

- `data/*.csv`: Dữ liệu đã tạo và cố định.
- `logs/experiment_runs.csv`: 72 lượt chạy (24 cấu hình × 3 seed), gồm chỉ số train/validation và thời gian huấn luyện.
- `logs/epoch_history_all_runs.csv`: Loss train và validation theo từng epoch của tất cả lượt chạy A/B/C.
- `results/experiment_[A-C]_summary.csv`: Giá trị trung bình và độ lệch chuẩn của ba seed.
- `models/experiment_checkpoints/*.pt`: Checkpoint tốt nhất trên validation của từng lượt thử nghiệm.
- `models/best_model.pt`: Checkpoint của mô hình cuối cùng được chọn.
- `models/best_model_metadata.json`: Thông tin mô hình được chọn.
- `src/predict_example.py`: File nạp checkpoint và dự đoán mật độ tại các cặp tọa độ do người dùng nhập.
- `results/final_test_predictions.csv`: Kết quả dự đoán cho 100 mẫu test.
- `reports/experiment_journal.xlsx`: File Excel ghi chép thí nghiệm và bảng kết quả.
- `reports/MLP_Function_Approximation_Report.docx/.pdf`: Báo cáo.
- `reports/MLP_Function_Approximation_Slides.pptx/.pdf`: Slide thuyết trình.

## 9. Lưu ý khi so sánh kết quả

- **Thử nghiệm A:** Chỉ thay đổi số lượng mẫu train. Mô hình có một lớp ẩn với 10 neuron.
- **Thử nghiệm B:** Chỉ thay đổi số neuron ở lớp ẩn từ 1 đến 10. Mô hình có một lớp ẩn.
- **Thử nghiệm C:** Chỉ thay đổi số lớp ẩn từ 1 đến 4. Mỗi lớp ẩn có 10 neuron.
- Tập validation được dùng để dừng sớm và chọn kiến trúc. Tập test chỉ dùng để đánh giá cuối cùng.
- Kết quả được báo cáo dưới dạng trung bình ± độ lệch chuẩn qua ba seed. Một tập mẫu nhỏ có thể cho thấy mức dao động lớn hơn giữa các seed.
- Tập test cuối cùng chỉ có 100 điểm. Vì vậy, các chỉ số trên tập này là ước lượng dựa trên số mẫu hữu hạn, không đảm bảo sai số tương tự tại mọi điểm trong miền đầu vào.

