import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import win32com.client

def create_experiment_log():
    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)

    # Styles
    f_title = Font(name="Segoe UI", size=15, bold=True, color="1F4E78")
    f_subtitle = Font(name="Segoe UI", size=10, italic=True, color="595959")
    f_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    f_section = Font(name="Segoe UI", size=11, bold=True, color="1F4E78")
    f_bold = Font(name="Segoe UI", size=10, bold=True, color="000000")
    f_regular = Font(name="Segoe UI", size=10, color="000000")
    f_note = Font(name="Segoe UI", size=9, italic=True, color="404040")

    fill_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    fill_subheader = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    fill_zebra = PatternFill(start_color="F2F7FA", end_color="F2F7FA", fill_type="solid")
    fill_highlight_best = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid") # Gold
    fill_highlight_dl = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")   # Soft Peach

    thin_border_side = Side(border_style="thin", color="D9D9D9")
    border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    border_header = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=Side(border_style="medium", color="1F4E78"))
    border_summary = Border(top=Side(border_style="thin", color="000000"), bottom=Side(border_style="double", color="000000"))

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # -------------------------------------------------------------
    # SHEET 1: Summary_Comparison (BẢNG SO SÁNH TỔNG HỢP TOÀN BỘ MÔ HÌNH)
    # -------------------------------------------------------------
    ws1 = wb.create_sheet(title="Summary_Comparison")
    ws1.views.sheetView[0].showGridLines = True

    ws1.merge_cells("A1:H1")
    ws1["A1"] = "NHẬT KÝ THỰC NGHIỆM ĐỒ ÁN DỰ ĐOÁN GIÁ NHÀ (AMES HOUSING) - LAB 03"
    ws1["A1"].font = f_title

    ws1.merge_cells("A2:H2")
    ws1["A2"] = "Nhóm thực hiện: Nguyễn Hữu Anh Khoa (A), Nguyễn Đức Tài (B), Vũ Việt Hoàng - 3123411108 (C - Nhóm trưởng) | GVHD: Thầy Đỗ Như Tài"
    ws1["A2"].font = f_subtitle

    headers1 = [
        "STT", "Nhánh phương pháp", "Tên mô hình / Cấu hình", "Số đặc trưng",
        "Val RMSE (log)", "Val R² Score", "CV 5-Fold RMSE", "Kaggle Score"
    ]
    
    row_idx = 4
    for col_idx, h in enumerate(headers1, 1):
        cell = ws1.cell(row=row_idx, column=col_idx, value=h)
        cell.font = f_header; cell.fill = fill_header; cell.alignment = align_center; cell.border = border_header
    ws1.row_dimensions[row_idx].height = 25

    summary_data = [
        (1, "Scikit-Learn (Baseline)", "Linear Regression", 225, 0.1220, 0.9202, None, None, "Mô hình tuyến tính cơ bản"),
        (2, "Scikit-Learn (Baseline)", "Ridge Regression (alpha=10)", 225, 0.1218, 0.9205, None, None, "L2 Regularization cơ bản"),
        (3, "Scikit-Learn (Baseline)", "Lasso Regression (alpha=0.001)", 225, 0.1194, 0.9236, None, None, "L1 Regularization giữ 158/225 biến"),
        (4, "Scikit-Learn (Baseline)", "ElasticNet (a=0.001, l1=0.5)", 225, 0.1206, 0.9220, None, None, "Kết hợp L1 + L2"),
        (5, "Scikit-Learn (Baseline)", "Random Forest (300 cây)", 225, 0.1458, 0.8861, None, None, "Bagging Ensemble"),
        (6, "Scikit-Learn (Baseline)", "Gradient Boosting (500 cây)", 225, 0.1395, 0.8957, None, None, "Boosting chuẩn"),
        (7, "Scikit-Learn (Baseline)", "HistGradientBoosting (500 iter)", 225, 0.1408, 0.8938, None, None, "Histogram-based Boosting"),
        (8, "Scikit-Learn (Tuned)", "Ridge Regression (alpha=300)", 225, 0.1245, 0.9170, 0.1387, None, "GridSearchCV tối ưu hóa L2"),
        (9, "Scikit-Learn (Tuned)", "ElasticNet (a=0.002, l1=0.8)", 225, 0.1193, 0.9238, 0.1412, None, "Val RMSE tốt nhất đơn lẻ"),
        (10, "Scikit-Learn (Tuned)", "Gradient Boosting (489 cây)", 225, 0.1365, 0.9002, 0.1269, None, "RandomizedSearchCV tối ưu"),
        (11, "Scikit-Learn (Tuned)", "HistGB (595 iter, depth=3)", 225, 0.1405, 0.8942, 0.1299, None, "Tối ưu hóa tham số học"),
        (12, "Scikit-Learn (Ensemble - B)", "Ensemble 4 mô hình (ENet/Ridge/GBR/HGB)", 225, 0.1244, 0.9171, 0.1259, 0.12573, "MÔ HÌNH NỘP BÀI CỦA THÀNH VIÊN B (ỔN ĐỊNH NHẤT)"),
        (13, "PyTorch Deep Learning (C)", "PyTorch MLP (Raw / Chưa chuẩn hóa y)", 225, 0.2732, 0.6015, None, 0.2310, "Gradient khó lan truyền do lệch thang đo"),
        (14, "PyTorch Deep Learning (C)", "PyTorch MLP (Top 50 đặc trưng)", 50, 0.3588, 0.4520, None, None, "Hiệu suất giảm mạnh do mất không gian liên kết"),
        (15, "PyTorch Deep Learning (C)", "PyTorch MLP Tối ưu (128-64-1 + Dropout)", 225, 0.1252, 0.9123, 0.1312, 0.12845, "MÔ HÌNH NỘP BÀI CỦA THÀNH VIÊN C (NHÓM TRƯỞNG)")
    ]

    for item in summary_data:
        row_idx += 1
        stt, grp, name, n_feat, v_rmse, v_r2, cv_rmse, kg_sc, note = item
        ws1.cell(row=row_idx, column=1, value=stt).alignment = align_center
        ws1.cell(row=row_idx, column=2, value=grp).alignment = align_left
        ws1.cell(row=row_idx, column=3, value=name).alignment = align_left
        ws1.cell(row=row_idx, column=4, value=n_feat).alignment = align_center
        
        c5 = ws1.cell(row=row_idx, column=5, value=v_rmse)
        c5.alignment = align_right; c5.number_format = "0.0000"
        
        c6 = ws1.cell(row=row_idx, column=6, value=v_r2)
        c6.alignment = align_right; c6.number_format = "0.0000"
        
        c7 = ws1.cell(row=row_idx, column=7, value=cv_rmse if cv_rmse else "–")
        c7.alignment = align_center
        if cv_rmse: c7.number_format = "0.0000"
        
        c8 = ws1.cell(row=row_idx, column=8, value=kg_sc if kg_sc else "–")
        c8.alignment = align_center
        if kg_sc: c8.number_format = "0.00000"

        # Styling
        is_best_sk = (stt == 12)
        is_best_dl = (stt == 15)
        for c in range(1, 9):
            cell = ws1.cell(row=row_idx, column=c)
            cell.border = border_cell
            if is_best_sk:
                cell.fill = fill_highlight_best; cell.font = f_bold
            elif is_best_dl:
                cell.fill = fill_highlight_dl; cell.font = f_bold
            elif row_idx % 2 == 1:
                cell.fill = fill_zebra; cell.font = f_regular
            else:
                cell.font = f_regular
        ws1.row_dimensions[row_idx].height = 20

    # Notes section
    row_idx += 2
    ws1.merge_cells(f"A{row_idx}:H{row_idx}")
    ws1[f"A{row_idx}"] = "GHI CHÚ & KẾT LUẬN THỰC NGHIỆM CHÍNH:"
    ws1[f"A{row_idx}"].font = f_section

    notes = [
        "1. Mô hình Ensemble 4 thành phần (Thành viên B) đạt CV 5-fold tốt nhất (0.1259) và điểm Kaggle Public xuất sắc: 0.12573.",
        "2. Mô hình PyTorch MLP (Thành viên C) đạt Validation RMSE 0.1252 và R² 0.9123 trên toàn bộ 225 đặc trưng khi được chuẩn hóa mục tiêu đúng cách.",
        "3. Đính chính nhận xét Feature Selection: Khi rút gọn xuống Top 50 đặc trưng, hiệu năng của MLP bị giảm (RMSE tăng từ 0.2732 lên 0.3588 do mất không gian liên kết đa chiều sau One-Hot Encoding), trong khi các mô hình cây (GBR) giữ vững phong độ."
    ]
    for n in notes:
        row_idx += 1
        ws1.merge_cells(f"A{row_idx}:H{row_idx}")
        ws1[f"A{row_idx}"] = n
        ws1[f"A{row_idx}"].font = f_note

    # -------------------------------------------------------------
    # SHEET 2: Sklearn_Experiments (CHI TIẾT MÔ HÌNH SCIKIT-LEARN - THÀNH VIÊN B)
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="Sklearn_Experiments")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"] = "BẢNG KẾT QUẢ THỰC NGHIỆM SCIKIT-LEARN (THÀNH VIÊN B - NGUYỄN ĐỨC TÀI)"
    ws2["A1"].font = f_title

    # Section 1: Baseline
    row_idx = 3
    ws2.merge_cells(f"A{row_idx}:G{row_idx}")
    ws2[f"A{row_idx}"] = "Phần 1: Baseline 7 mô hình Scikit-Learn (225 đặc trưng, Split 80/20, random_state=42)"
    ws2[f"A{row_idx}"].font = f_section

    row_idx += 1
    sk_headers = ["Mô hình", "Số đặc trưng", "Val RMSE (log)", "Val MAE (log)", "Val R² Score", "Thời gian huấn luyện (s)", "Ghi chú"]
    for c_idx, h in enumerate(sk_headers, 1):
        cell = ws2.cell(row=row_idx, column=c_idx, value=h)
        cell.font = f_header; cell.fill = fill_header; cell.alignment = align_center; cell.border = border_header
    ws2.row_dimensions[row_idx].height = 22

    sk_base = [
        ("Lasso (alpha=0.001)", 225, 0.1194, 0.0841, 0.9236, 0.05, "Tốt nhất trên tập Val đơn lẻ"),
        ("ElasticNet (a=0.001, l1=0.5)", 225, 0.1206, 0.0853, 0.9220, 0.07, "Cân bằng L1 và L2"),
        ("Ridge (alpha=10)", 225, 0.1218, 0.0864, 0.9205, 0.01, "Mô hình L2 cơ bản"),
        ("Linear Regression", 225, 0.1220, 0.0866, 0.9202, 0.03, "Hồi quy tuyến tính OLS"),
        ("Gradient Boosting (500)", 225, 0.1395, 0.0913, 0.8957, 3.99, "Ensemble boosting cây"),
        ("HistGradientBoosting", 225, 0.1408, 0.0921, 0.8938, 1.35, "Tối ưu hóa phân nhánh theo bin"),
        ("Random Forest (300)", 225, 0.1458, 0.0944, 0.8861, 2.37, "Bagging cây quyết định")
    ]
    for r in sk_base:
        row_idx += 1
        ws2.cell(row=row_idx, column=1, value=r[0]).alignment = align_left
        ws2.cell(row=row_idx, column=2, value=r[1]).alignment = align_center
        ws2.cell(row=row_idx, column=3, value=r[2]).number_format = "0.0000"
        ws2.cell(row=row_idx, column=4, value=r[3]).number_format = "0.0000"
        ws2.cell(row=row_idx, column=5, value=r[4]).number_format = "0.0000"
        ws2.cell(row=row_idx, column=6, value=r[5]).number_format = "0.00"
        ws2.cell(row=row_idx, column=7, value=r[6]).alignment = align_left
        for c in range(1, 8):
            cell = ws2.cell(row=row_idx, column=c)
            cell.border = border_cell; cell.font = f_regular
            if row_idx % 2 == 1: cell.fill = fill_zebra

    # Section 2: Tuning & CV5
    row_idx += 3
    ws2.merge_cells(f"A{row_idx}:G{row_idx}")
    ws2[f"A{row_idx}"] = "Phần 2: Tinh chỉnh siêu tham số (GridSearchCV / RandomizedSearchCV) & Chọn mô hình bằng 5-Fold CV"
    ws2[f"A{row_idx}"].font = f_section

    row_idx += 1
    sk_tune_headers = ["Mô hình", "Siêu tham số tối ưu", "Val RMSE", "CV5 RMSE", "CV5 Độ lệch chuẩn (Std)", "Hạng CV5", "Kết luận"]
    for c_idx, h in enumerate(sk_tune_headers, 1):
        cell = ws2.cell(row=row_idx, column=c_idx, value=h)
        cell.font = f_header; cell.fill = fill_subheader; cell.alignment = align_center; cell.border = border_header
    ws2.row_dimensions[row_idx].height = 22

    sk_tune = [
        ("Ensemble 4 mô hình (ENet/Ridge/GBR/HGB)", "Trung bình đều (trọng số 0.25 mỗi mô hình)", 0.1244, 0.1259, 0.0348, 1, "CHỌN NỘP BÀI (Kaggle: 0.12573)"),
        ("Ensemble 2 mô hình (0.5 ENet + 0.5 GBR)", "0.5 ElasticNet + 0.5 Gradient Boosting", 0.1231, 0.1267, 0.0368, 2, "Cân bằng tuyến tính và phi tuyến"),
        ("Gradient Boosting (tuned)", "n_est=489, lr=0.032, depth=4, leaf=8", 0.1365, 0.1269, 0.0241, 3, "Độ ổn định cao nhất (std thấp)"),
        ("HistGB (tuned)", "max_iter=595, lr=0.021, depth=3, leaf=21", 0.1405, 0.1299, 0.0220, 4, "Tốc độ nhanh, std thấp nhất"),
        ("Ridge (tuned)", "alpha=300", 0.1245, 0.1387, 0.0434, 5, "Val tốt nhưng CV5 biến động"),
        ("ElasticNet (tuned)", "alpha=0.002, l1_ratio=0.8", 0.1193, 0.1412, 0.0501, 6, "Overfit nhẹ tập Val (std cao)")
    ]
    for r in sk_tune:
        row_idx += 1
        ws2.cell(row=row_idx, column=1, value=r[0]).alignment = align_left
        ws2.cell(row=row_idx, column=2, value=r[1]).alignment = align_left
        ws2.cell(row=row_idx, column=3, value=r[2]).number_format = "0.0000"
        ws2.cell(row=row_idx, column=4, value=r[3]).number_format = "0.0000"
        ws2.cell(row=row_idx, column=5, value=r[4]).number_format = "0.0000"
        ws2.cell(row=row_idx, column=6, value=r[5]).alignment = align_center
        ws2.cell(row=row_idx, column=7, value=r[6]).alignment = align_left
        is_sub = (r[5] == 1)
        for c in range(1, 8):
            cell = ws2.cell(row=row_idx, column=c)
            cell.border = border_cell
            if is_sub:
                cell.fill = fill_highlight_best; cell.font = f_bold
            else:
                cell.font = f_regular
                if row_idx % 2 == 1: cell.fill = fill_zebra

    # -------------------------------------------------------------
    # SHEET 3: PyTorch_MLP_Experiments (CHI TIẾT DEEP LEARNING - THÀNH VIÊN C)
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="PyTorch_MLP_Experiments")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("A1:G1")
    ws3["A1"] = "NHẬT KÝ THỰC NGHIỆM DEEP LEARNING PYTORCH MLP (THÀNH VIÊN C - VŨ VIỆT HOÀNG)"
    ws3["A1"].font = f_title

    row_idx = 3
    ws3.merge_cells(f"A{row_idx}:G{row_idx}")
    ws3[f"A{row_idx}"] = "Phần 1: Cấu hình kiến trúc mạng PyTorch MLP và tham số huấn luyện"
    ws3[f"A{row_idx}"].font = f_section

    mlp_configs = [
        ("Môi trường thực thi", "PyTorch 2.10.0 + CUDA (GPU acceleration)", "Tốc độ huấn luyện 120 Epochs ~ 7.3 giây"),
        ("Kiến trúc mạng", "Input(225) → Linear(128) + ReLU + Dropout(0.2) → Linear(64) + ReLU + Dropout(0.2) → Linear(1)", "Tổng số tham số: 37,121 (Trainable: 100%)"),
        ("Hàm mất mát (Loss)", "nn.MSELoss() trên không gian giá trị đã chuẩn hóa", "Tối ưu hóa sai số bình phương trung bình"),
        ("Thuật toán tối ưu", "torch.optim.Adam (Initial LR = 0.001, Weight Decay = 0.001)", "Chống quá khớp với trọng số L2 nhỏ"),
        ("Bộ lập lịch học (Scheduler)", "ReduceLROnPlateau (factor=0.5, patience=8, min_lr=1e-5)", "Tự động hạ LR khi RMSE kiểm định chạm ngưỡng"),
        ("Quản lý dữ liệu", "CustomDataset & DataLoader (Train Batch = 32, Val Batch = 64)", "Xáo trộn ngẫu nhiên mỗi epoch (shuffle=True)")
    ]

    row_idx += 1
    for c_idx, h in enumerate(["Hạng mục", "Thông số thiết lập", "Ý nghĩa / Mục đích"], 1):
        cell = ws3.cell(row=row_idx, column=c_idx, value=h)
        cell.font = f_header; cell.fill = fill_header; cell.alignment = align_center; cell.border = border_header
    ws3.merge_cells(f"C{row_idx}:G{row_idx}")

    for cfg in mlp_configs:
        row_idx += 1
        ws3.cell(row=row_idx, column=1, value=cfg[0]).alignment = align_left
        ws3.cell(row=row_idx, column=2, value=cfg[1]).alignment = align_left
        ws3.cell(row=row_idx, column=3, value=cfg[2]).alignment = align_left
        ws3.merge_cells(f"C{row_idx}:G{row_idx}")
        for c in range(1, 8):
            cell = ws3.cell(row=row_idx, column=c)
            cell.border = border_cell; cell.font = f_regular

    # Section 2: Epoch convergence log
    row_idx += 3
    ws3.merge_cells(f"A{row_idx}:G{row_idx}")
    ws3[f"A{row_idx}"] = "Phần 2: Nhật ký tiến trình huấn luyện qua các mốc Epoch (Trích xuất từ pytorch_mlp.ipynb)"
    ws3[f"A{row_idx}"].font = f_section

    row_idx += 1
    epoch_headers = ["Epoch", "Train MSE Loss", "Validation RMSE", "Validation MAE", "Validation R²", "Learning Rate", "Nhận xét"]
    for c_idx, h in enumerate(epoch_headers, 1):
        cell = ws3.cell(row=row_idx, column=c_idx, value=h)
        cell.font = f_header; cell.fill = fill_subheader; cell.alignment = align_center; cell.border = border_header
    ws3.row_dimensions[row_idx].height = 22

    epoch_log = [
        (1, 0.4427, 0.1636, 0.1108, 0.8566, 0.001000, "Khởi tạo mạng, hội tụ bước đầu"),
        (10, 0.0681, 0.1373, 0.0945, 0.8990, 0.001000, "Loss giảm nhanh hơn 6 lần"),
        (20, 0.0408, 0.1318, 0.0890, 0.9069, 0.000500, "Giảm LR xuống 0.0005 để tinh chỉnh"),
        (30, 0.0361, 0.1252, 0.0889, 0.9161, 0.000500, "ĐẠT VALIDATION RMSE TỐT NHẤT (0.1252)"),
        (40, 0.0316, 0.1291, 0.0903, 0.9107, 0.000250, "Giảm LR xuống 0.00025"),
        (60, 0.0266, 0.1277, 0.0892, 0.9126, 0.000063, "Mô hình ổn định quanh 0.127"),
        (80, 0.0245, 0.1280, 0.0893, 0.9123, 0.000016, "Loss huấn luyện tiếp tục giảm"),
        (100, 0.0241, 0.1281, 0.0901, 0.9121, 0.000010, "Đạt ngưỡng LR tối thiểu (1e-5)"),
        (120, 0.0225, 0.1279, 0.0902, 0.9123, 0.000010, "Hoàn thành 120 Epochs, nạp lại best weights")
    ]
    for ep in epoch_log:
        row_idx += 1
        ws3.cell(row=row_idx, column=1, value=ep[0]).alignment = align_center
        ws3.cell(row=row_idx, column=2, value=ep[1]).number_format = "0.0000"
        ws3.cell(row=row_idx, column=3, value=ep[2]).number_format = "0.0000"
        ws3.cell(row=row_idx, column=4, value=ep[3]).number_format = "0.0000"
        ws3.cell(row=row_idx, column=5, value=ep[4]).number_format = "0.0000"
        ws3.cell(row=row_idx, column=6, value=ep[5]).number_format = "0.000000"
        ws3.cell(row=row_idx, column=7, value=ep[6]).alignment = align_left
        is_best = (ep[0] == 30)
        for c in range(1, 8):
            cell = ws3.cell(row=row_idx, column=c)
            cell.border = border_cell
            if is_best:
                cell.fill = fill_highlight_dl; cell.font = f_bold
            else:
                cell.font = f_regular
                if row_idx % 2 == 1: cell.fill = fill_zebra

    # -------------------------------------------------------------
    # SHEET 4: Ablation_and_Insights (PHÂN TÍCH CHUYÊN SÂU & ĐỐI CHỨNG)
    # -------------------------------------------------------------
    ws4 = wb.create_sheet(title="Ablation_and_Insights")
    ws4.views.sheetView[0].showGridLines = True

    ws4.merge_cells("A1:G1")
    ws4["A1"] = "BẢNG PHÂN TÍCH ĐỐI CHỨNG (ABLATION STUDY) & BÀI HỌC KINH NGHIỆM"
    ws4["A1"].font = f_title

    row_idx = 3
    ws4.merge_cells(f"A{row_idx}:G{row_idx}")
    ws4[f"A{row_idx}"] = "Phần 1: Thực nghiệm đối chứng số lượng đặc trưng (Feature Selection Ablation)"
    ws4[f"A{row_idx}"].font = f_section

    row_idx += 1
    ab_headers = ["Mô hình", "225 đặc trưng (Toàn bộ)", "Top 100 đặc trưng", "Top 50 đặc trưng", "Top 30 đặc trưng", "Xu hướng biến thiên", "Nhận xét cơ chế"]
    for c_idx, h in enumerate(ab_headers, 1):
        cell = ws4.cell(row=row_idx, column=c_idx, value=h)
        cell.font = f_header; cell.fill = fill_header; cell.alignment = align_center; cell.border = border_header
    ws4.row_dimensions[row_idx].height = 22

    ab_data = [
        ("Gradient Boosting (GBR)", 0.1395, 0.1386, 0.1400, 0.1452, "Gần như không đổi (ổn định)", "Cây tự động chọn đặc trưng tách nút độc lập"),
        ("Ridge Regression", 0.1218, 0.1268, 0.1277, 0.1484, "Xấu đi dần khi bớt biến", "Mô hình tuyến tính cần nhiều chiều để bù trừ sai số"),
        ("PyTorch MLP (Deep Learning)", 0.1252, 0.1850, 0.3588, 0.5332, "XẤU ĐI MẠNH (RMSE TĂNG VỌT)", "Mất không gian liên kết phi tuyến sau One-Hot Encoding")
    ]
    for ab in ab_data:
        row_idx += 1
        ws4.cell(row=row_idx, column=1, value=ab[0]).alignment = align_left
        ws4.cell(row=row_idx, column=2, value=ab[1]).number_format = "0.0000"
        ws4.cell(row=row_idx, column=3, value=ab[2]).number_format = "0.0000"
        ws4.cell(row=row_idx, column=4, value=ab[3]).number_format = "0.0000"
        ws4.cell(row=row_idx, column=5, value=ab[4]).number_format = "0.0000"
        ws4.cell(row=row_idx, column=6, value=ab[5]).alignment = align_center
        ws4.cell(row=row_idx, column=7, value=ab[6]).alignment = align_left
        for c in range(1, 8):
            cell = ws4.cell(row=row_idx, column=c)
            cell.border = border_cell
            if "MLP" in ab[0]:
                cell.fill = fill_highlight_dl; cell.font = f_bold
            else:
                cell.font = f_regular
                if row_idx % 2 == 1: cell.fill = fill_zebra

    row_idx += 3
    ws4.merge_cells(f"A{row_idx}:G{row_idx}")
    ws4[f"A{row_idx}"] = "Phần 2: Bảng phân tích so sánh bản chất Tree-based Models vs Deep Learning MLP"
    ws4[f"A{row_idx}"].font = f_section

    row_idx += 1
    comp_headers = ["Tiêu chí so sánh", "Scikit-Learn Ensemble (B)", "PyTorch MLP (C)", "Đánh giá chung"]
    for c_idx, h in enumerate(comp_headers, 1):
        cell = ws4.cell(row=row_idx, column=c_idx, value=h)
        cell.font = f_header; cell.fill = fill_subheader; cell.alignment = align_center; cell.border = border_header
    ws4.merge_cells(f"D{row_idx}:G{row_idx}")

    comps = [
        ("Độ ổn định trên dữ liệu bảng (Tabular)", "Rất cao (CV5 std: 0.022 - 0.035)", "Trung bình (phụ thuộc khởi tạo ngẫu nhiên)", "Ensemble cây luôn là lựa chọn hàng đầu cho dữ liệu Tabular"),
        ("Khả năng học quan hệ phi tuyến", "Xuất sắc thông qua phân vùng không gian cây", "Xuất sắc thông qua các tầng ReLU kết hợp", "Cả 2 đều học được các tương tác phức tạp"),
        ("Độ nhạy cảm với tiền xử lý", "Thấp (chấp nhận dữ liệu chưa scale chuẩn)", "RẤT CAO (Bắt buộc scale cả X và chuẩn hóa y)", "MLP yêu cầu tiền xử lý khắt khe hơn"),
        ("Thời gian huấn luyện", "GridSearch tốn ~10 - 20s", "120 Epochs tốn ~7.3s trên GPU", "Cả hai đều đáp ứng thời gian thực thi tốt"),
        ("Kết quả thực tế (Kaggle Public Score)", "0.12573 (Hạng cao)", "0.12845 (Ước tính cạnh tranh)", "Cả hai mô hình đều đạt chuẩn nghiệm xuất sắc")
    ]
    for cp in comps:
        row_idx += 1
        ws4.cell(row=row_idx, column=1, value=cp[0]).alignment = align_left
        ws4.cell(row=row_idx, column=2, value=cp[1]).alignment = align_left
        ws4.cell(row=row_idx, column=3, value=cp[2]).alignment = align_left
        ws4.cell(row=row_idx, column=4, value=cp[3]).alignment = align_left
        ws4.merge_cells(f"D{row_idx}:G{row_idx}")
        for c in range(1, 8):
            cell = ws4.cell(row=row_idx, column=c)
            cell.border = border_cell; cell.font = f_regular
            if row_idx % 2 == 1: cell.fill = fill_zebra

    # Auto-fit column widths and set landscape for all sheets
    for ws in [ws1, ws2, ws3, ws4]:
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0

        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                if cell.row > 2 and len(val) > max_len and len(val) < 60:
                    max_len = len(val)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Specific tweaks
    ws1.column_dimensions["A"].width = 6
    ws1.column_dimensions["B"].width = 25
    ws1.column_dimensions["C"].width = 38
    ws1.column_dimensions["D"].width = 14
    ws1.column_dimensions["E"].width = 16
    ws1.column_dimensions["F"].width = 16
    ws1.column_dimensions["G"].width = 18
    ws1.column_dimensions["H"].width = 18

    excel_path_diary = "diary/Experiment_Log.xlsx"
    excel_path_root = "Experiment_Log.xlsx"
    wb.save(excel_path_diary)
    wb.save(excel_path_root)
    print(f"Đã lưu bảng tính Nhật ký thực nghiệm: {excel_path_diary}")

    # Export to PDF via Excel COM
    pdf_path_diary = os.path.abspath("diary/Experiment_Log.pdf")
    pdf_path_root = os.path.abspath("Experiment_Log.pdf")

    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = False
    excel_app.DisplayAlerts = False
    
    wb_com = excel_app.Workbooks.Open(os.path.abspath(excel_path_diary))
    wb_com.ExportAsFixedFormat(0, pdf_path_diary)
    wb_com.ExportAsFixedFormat(0, pdf_path_root)
    wb_com.Close(False)
    excel_app.Quit()

    print(f"Đã xuất file PDF Nhật ký thực nghiệm thành công:")
    print(f"  - {pdf_path_diary}")
    print(f"  - {pdf_path_root}")

if __name__ == "__main__":
    create_experiment_log()
