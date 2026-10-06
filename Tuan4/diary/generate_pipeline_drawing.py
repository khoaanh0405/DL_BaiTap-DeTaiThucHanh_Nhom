import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import win32com.client

def create_pipeline_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # blank layout

    # Color Palette
    c_navy = RGBColor(26, 54, 93)       # #1a365d
    c_blue = RGBColor(43, 108, 176)     # #2b6cb0
    c_light_blue = RGBColor(235, 248, 255)
    c_teal = RGBColor(49, 151, 149)     # #319795
    c_light_teal = RGBColor(230, 255, 250)
    c_orange = RGBColor(221, 107, 32)   # #dd6b20
    c_light_orange = RGBColor(254, 235, 226)
    c_purple = RGBColor(107, 70, 193)   # #6b46c1
    c_light_purple = RGBColor(250, 245, 255)
    c_gray = RGBColor(74, 85, 104)      # #4a5568
    c_dark = RGBColor(45, 55, 72)
    c_white = RGBColor(255, 255, 255)
    c_border_gray = RGBColor(203, 213, 225)
    c_green = RGBColor(40, 167, 69)

    # -------------------------------------------------------------
    # SLIDE 1: TỔNG QUAN PIPELINE HỆ THỐNG (END-TO-END WORKFLOW)
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)

    # Header Bar
    header = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.4), Inches(12.333), Inches(0.9))
    header.fill.solid()
    header.fill.fore_color.rgb = c_navy
    header.line.fill.background()
    tf = header.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "SƠ ĐỒ PIPELINE TOÀN DIỆN DỰ ÁN AMES HOUSING (LAB 03)"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = c_white
    p.alignment = PP_ALIGN.LEFT
    p2 = tf.add_paragraph()
    p2.text = "Luồng dữ liệu tích hợp: Dữ liệu thô → Tiền xử lý & Kỹ thuật đặc trưng (A) → Nhánh Sklearn (B) & Nhánh PyTorch MLP (C) → Dự đoán Kaggle"
    p2.font.size = Pt(11)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.alignment = PP_ALIGN.LEFT

    # Helper function to add card
    def add_card(slide, left, top, width, height, title, bg_color, border_color, title_color=c_white):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        
        # Header strip
        title_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, Inches(0.45))
        title_box.fill.solid()
        title_box.fill.fore_color.rgb = border_color
        title_box.line.fill.background()
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = title_color
        p.alignment = PP_ALIGN.CENTER
        
        # Content box
        content = slide.shapes.add_textbox(left + Inches(0.1), top + Inches(0.48), width - Inches(0.2), height - Inches(0.5))
        tf_c = content.text_frame
        tf_c.word_wrap = True
        return tf_c

    # Card 1: Dữ liệu thô (Raw Data)
    tf1 = add_card(s1, Inches(0.5), Inches(1.5), Inches(2.2), Inches(5.5), "1. DỮ LIỆU GỐC (RAW)", c_light_blue, c_navy)
    p = tf1.paragraphs[0]
    p.text = "Tập dữ liệu Ames Housing:"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = c_navy
    bullets1 = [
        "train.csv: 1,460 dòng × 81 cột",
        "test.csv: 1,459 dòng × 80 cột",
        "Biến mục tiêu: SalePrice (Giá bán nhà thực tế)",
        "Biến đổi log1p: y = log(1 + SalePrice) giúp phân phối đối xứng chuẩn (Skewed → Normal).",
        "Đặc trưng đa dạng: 36 số thực/rời rạc, 43 định danh/phân loại."
    ]
    for b in bullets1:
        p = tf1.add_paragraph()
        p.text = "• " + b; p.font.size = Pt(9.5); p.font.color.rgb = c_dark

    # Card 2: Tiền xử lý & Feature Engineering (A)
    tf2 = add_card(s1, Inches(2.9), Inches(1.5), Inches(2.7), Inches(5.5), "2. PREPROCESSING & FE (A)", c_light_teal, c_teal)
    p = tf2.paragraphs[0]
    p.text = "Thành viên A: Nguyễn Hữu Anh Khoa"
    p.font.bold = True; p.font.size = Pt(10.5); p.font.color.rgb = c_teal
    bullets2 = [
        "Xử lý Missing Values:",
        "  - Số diện tích/phòng: điền 0",
        "  - Hạng mục NA = None (PoolQC, Garage...)",
        "  - LotFrontage: Median theo Neighborhood",
        "Mã hóa biến (Encoding):",
        "  - Ordinal Encoding: 17 cột thứ tự chất lượng (Ex, Gd, TA, Fa, Po → 5..1)",
        "  - One-Hot Encoding: pd.get_dummies()",
        "StandardScaler: Chuẩn hóa Z-score toàn bộ biến",
        "Feature Engineering:",
        "  - TotalSF = 1stFlrSF + 2ndFlrSF + TotalBsmtSF",
        "  - TotalBath, HouseAge, RemodAge, HasPool",
        "  - Drop 9 cột thành phần chống đa cộng tuyến",
        "Bàn giao: 225 đặc trưng (x_train, y_train, x_test)"
    ]
    for b in bullets2:
        p = tf2.add_paragraph()
        p.text = ("• " if not b.startswith("  ") else "") + b
        p.font.size = Pt(9.5); p.font.color.rgb = c_dark

    # Nhánh B: Scikit-Learn
    tf_b = add_card(s1, Inches(5.8), Inches(1.5), Inches(3.4), Inches(2.65), "3A. SKLEARN MODELS (B)", c_light_blue, c_blue)
    p = tf_b.paragraphs[0]
    p.text = "Thành viên B: Nguyễn Đức Tài"
    p.font.bold = True; p.font.size = Pt(10.5); p.font.color.rgb = c_blue
    bullets_b = [
        "Split: 80% Train (1168) / 20% Val (292), seed=42",
        "Baseline 7 mô hình: Linear, Ridge, Lasso, ElasticNet, Random Forest, GBR, HistGB",
        "Feature Selection: Thử nghiệm Top 100, 50, 30 theo GBR importance",
        "Tuning: GridSearchCV & RandomizedSearchCV",
        "Ensemble 4 mô hình: ElasticNet + Ridge + GBR + HistGB (Trung bình đều)",
        "Đánh giá: 5-Fold CV RMSE = 0.1259 | Val = 0.1244"
    ]
    for b in bullets_b:
        p = tf_b.add_paragraph()
        p.text = "• " + b; p.font.size = Pt(9); p.font.color.rgb = c_dark

    # Nhánh C: PyTorch MLP
    tf_c = add_card(s1, Inches(5.8), Inches(4.35), Inches(3.4), Inches(2.65), "3B. PYTORCH MLP (C - NHÓM TRƯỞNG)", c_light_orange, c_orange)
    p = tf_c.paragraphs[0]
    p.text = "Thành viên C: Vũ Việt Hoàng (MSSV: 3123411108)"
    p.font.bold = True; p.font.size = Pt(10.5); p.font.color.rgb = c_orange
    bullets_c = [
        "Split: 80/20 (seed=42) đồng bộ; CustomDataset & DataLoader (Batch 32)",
        "Kiến trúc MLP: Input(225) → Linear(128)+ReLU+Dropout(0.2) → Linear(64)+ReLU+Dropout(0.2) → Linear(1)",
        "Huấn luyện: Adam (lr=0.001) + MSELoss + ReduceLROnPlateau (120 epochs)",
        "Chuẩn hóa y (Zero-mean, unit-var) giúp hội tụ nhanh",
        "Thực nghiệm đối chứng: Top 50 đặc trưng làm RMSE tăng vọt từ 0.1252 lên 0.5332 (khẳng định mạng nơ-ron cần không gian đầy đủ)",
        "Đánh giá: Val RMSE = 0.1252 | Val R² = 0.9123"
    ]
    for b in bullets_c:
        p = tf_c.add_paragraph()
        p.text = "• " + b; p.font.size = Pt(9); p.font.color.rgb = c_dark

    # Card 4: Kết quả nộp bài & Kaggle (Prediction & Submission)
    tf4 = add_card(s1, Inches(9.4), Inches(1.5), Inches(3.433), Inches(5.5), "4. PREDICTION & KAGGLE SCORE", c_light_purple, c_purple)
    p = tf4.paragraphs[0]
    p.text = "ĐÁNH GIÁ & XUẤT SUBMISSION"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = c_purple
    bullets4 = [
        "Xử lý tập kiểm thử x_test.xlsx (1459 dòng):",
        "  - Điền giá trị rỗng (fillna 0)",
        "  - Dự đoán log1p(SalePrice)",
        "  - Nghịch đảo biến đổi bằng expm1()",
        "submission_sklearn.csv (Thành viên B):",
        "  - Mô hình Ensemble 4 thành phần",
        "  - CV5 RMSE: 0.1259",
        "  - Kaggle Public Score: 0.12573 (XUẤT SẮC)",
        "submission_pytorch.csv (Thành viên C):",
        "  - Mô hình PyTorch HousePriceMLP tối ưu",
        "  - Val RMSE: 0.1252 | Val R²: 0.9123",
        "  - Kaggle Score ước tính: 0.12845",
        "Đóng gói bài làm chuẩn:",
        "  - Báo cáo PDF có bìa, phân công, nội dung",
        "  - Pipeline Drawing PDF & Experiment Log PDF",
        "  - Nén file: lab03_house_price_VuVietHoang_3123411108.zip"
    ]
    for b in bullets4:
        p = tf4.add_paragraph()
        p.text = ("• " if not b.startswith("  ") else "") + b
        p.font.size = Pt(9.5); p.font.color.rgb = c_dark

    # -------------------------------------------------------------
    # SLIDE 2: CHI TIẾT NHÁNH PYTORCH MLP (KIẾN TRÚC & HUẤN LUYỆN)
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)

    # Header Bar
    header2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.4), Inches(12.333), Inches(0.9))
    header2.fill.solid(); header2.fill.fore_color.rgb = c_orange; header2.line.fill.background()
    tf = header2.text_frame
    p = tf.paragraphs[0]
    p.text = "CHI TIẾT NHÁNH DEEP LEARNING: PYTORCH MULTI-LAYER PERCEPTRON (C)"
    p.font.size = Pt(19); p.font.bold = True; p.font.color.rgb = c_white
    p2 = tf.add_paragraph()
    p2.text = "Phụ trách: Thành viên C - Vũ Việt Hoàng (Nhóm trưởng) | Kiến trúc mạng 3 tầng, hàm mất mát MSELoss, Optimizer Adam"
    p2.font.size = Pt(11); p2.font.color.rgb = RGBColor(254, 235, 226)

    # Architecture Box
    tf_arch = add_card(s2, Inches(0.5), Inches(1.5), Inches(5.8), Inches(5.5), "KIẾN TRÚC MẠNG HOUSEPRICEMLP (TORCH.NN.MODULE)", c_light_orange, c_orange)
    p = tf_arch.paragraphs[0]
    p.text = "Mô hình Mạng Nơ-ron Lan truyền tiến (Feedforward MLP):"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = c_orange
    arch_bullets = [
        "Input Dimension: 225 đặc trưng sau khi StandardScaler & One-Hot Encoding",
        "Tầng 1 (Hidden 1): Linear(225, 128)",
        "  - Hàm kích hoạt: ReLU() sinh tính phi tuyến",
        "  - Dropout(p=0.2): Chống hiện tượng quá khớp (Overfitting)",
        "Tầng 2 (Hidden 2): Linear(128, 64)",
        "  - Hàm kích hoạt: ReLU()",
        "  - Dropout(p=0.2): Triệt tiêu ngẫu nhiên 20% nơ-ron",
        "Tầng 3 (Output): Linear(64, 1)",
        "  - Dự đoán giá trị liên tục trên không gian chuẩn hóa",
        "Tổng tham số: 37,121 tham số (100% có thể huấn luyện)",
        "Tối ưu hóa & Lập lịch học:",
        "  - Optimizer: Adam (Initial LR = 0.001, Weight Decay = 0.001)",
        "  - Scheduler: ReduceLROnPlateau (factor=0.5, patience=8, min_lr=1e-5)",
        "  - Batch Size: 32 (Train) / 64 (Val) | 120 Epochs | Thời gian chạy: ~7.3s trên GPU"
    ]
    for b in arch_bullets:
        p = tf_arch.add_paragraph()
        p.text = ("• " if not b.startswith("  ") else "") + b
        p.font.size = Pt(9.5); p.font.color.rgb = c_dark

    # Results & Ablation Box
    tf_res = add_card(s2, Inches(6.6), Inches(1.5), Inches(6.233), Inches(5.5), "KẾT QUẢ HUẤN LUYỆN & PHÂN TÍCH ĐỐI CHỨNG (ABLATION)", c_light_blue, c_blue)
    p = tf_res.paragraphs[0]
    p.text = "1. Quá trình hội tụ & Chỉ số kiểm định Validation:"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = c_blue
    res_bullets = [
        "Train MSE Loss: Giảm ổn định từ 0.4427 (Epoch 1) → 0.0225 (Epoch 120)",
        "Validation RMSE: Đạt đỉnh tối ưu 0.1252 tại Epoch 30 (sau đó học ổn định nhờ ReduceLROnPlateau)",
        "Validation R²: 0.9123 | Validation MAE: 0.0902",
        "",
        "2. THỰC NGHIỆM ĐỐI CHỨNG ĐẶC TRƯNG (TOP 50 VS 225):",
        "(Đính chính số liệu báo cáo theo ghi chú của Thành viên B)",
        "  • MLP trên toàn bộ 225 đặc trưng: Val RMSE = 0.1252 (Rất tốt)",
        "  • MLP trên Top 50 đặc trưng: Val RMSE = 0.5332 (Hiệu suất giảm mạnh)",
        "  • (Số liệu ghi nhận ban đầu khi chưa scale y: 0.2732 → 0.3588)",
        "",
        "3. GIẢI THÍCH BẢN CHẤT HỌC SÂU TRÊN DỮ LIỆU DẠNG BẢNG (TABULAR):",
        "  • Các mô hình cây (GBR, Random Forest) phân nhánh độc lập theo từng đặc trưng riêng rẽ nên chọn Top 50 vẫn giữ được 90% hiệu năng.",
        "  • Mạng nơ-ron sâu (MLP) biểu diễn quan hệ phối hợp giữa các biến. Khi One-Hot biến các biến phân loại thành nhiều cột nhị phân thưa thớt, việc cắt giảm xuống Top 50 làm đứt gãy thông tin biểu diễn của các hạng mục, khiến mạng nơ-ron mất khả năng học quan hệ phức tạp!"
    ]
    for b in res_bullets:
        p = tf_res.add_paragraph()
        p.text = b
        if "THỰC NGHIỆM" in b or "GIẢI THÍCH" in b:
            p.font.bold = True; p.font.size = Pt(10.5); p.font.color.rgb = c_navy
        else:
            p.font.size = Pt(9.5); p.font.color.rgb = c_dark

    # -------------------------------------------------------------
    # SLIDE 3: BẢNG SO SÁNH TỔNG HỢP (EXPERIMENT LOG COMPARISON)
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)

    header3 = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.4), Inches(12.333), Inches(0.9))
    header3.fill.solid(); header3.fill.fore_color.rgb = c_navy; header3.line.fill.background()
    tf = header3.text_frame
    p = tf.paragraphs[0]
    p.text = "NHẬT KÝ THỰC NGHIỆM SO SÁNH: SCIKIT-LEARN VS PYTORCH MLP"
    p.font.size = Pt(19); p.font.bold = True; p.font.color.rgb = c_white
    p2 = tf.add_paragraph()
    p2.text = "Tổng hợp toàn bộ chỉ số thực nghiệm: Validation RMSE, MAE, R², 5-Fold Cross Validation và Kaggle Public Score"
    p2.font.size = Pt(11); p2.font.color.rgb = RGBColor(203, 213, 225)

    # Table of comparison
    rows, cols = 11, 7
    table_shape = s3.shapes.add_table(rows, cols, Inches(0.5), Inches(1.5), Inches(12.333), Inches(5.4))
    tbl = table_shape.table

    # Column widths
    tbl.columns[0].width = Inches(1.8)
    tbl.columns[1].width = Inches(3.0)
    tbl.columns[2].width = Inches(1.4)
    tbl.columns[3].width = Inches(1.3)
    tbl.columns[4].width = Inches(1.3)
    tbl.columns[5].width = Inches(1.6)
    tbl.columns[6].width = Inches(1.933)

    headers = ["Nhóm phương pháp", "Tên mô hình / Phương pháp", "Val RMSE", "Val MAE", "Val R²", "CV 5-Fold RMSE", "Kaggle Score"]
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid(); cell.fill.fore_color.rgb = c_navy
        p = cell.text_frame.paragraphs[0]
        p.text = h_text; p.font.bold = True; p.font.size = Pt(10.5); p.font.color.rgb = c_white
        p.alignment = PP_ALIGN.CENTER

    data_rows = [
        ("Sklearn (Baseline)", "Linear Regression", "0.1220", "0.0866", "0.9202", "–", "–"),
        ("Sklearn (Baseline)", "Ridge Regression (alpha=10)", "0.1218", "0.0864", "0.9205", "–", "–"),
        ("Sklearn (Baseline)", "Lasso (alpha=0.001)", "0.1194", "0.0841", "0.9236", "–", "–"),
        ("Sklearn (Baseline)", "Random Forest (300 cây)", "0.1458", "0.0944", "0.8861", "–", "–"),
        ("Sklearn (Tuned)", "Ridge (alpha=300)", "0.1245", "0.0875", "0.9170", "0.1387 ± 0.043", "–"),
        ("Sklearn (Tuned)", "ElasticNet (a=0.002, l1=0.8)", "0.1193", "0.0840", "0.9238", "0.1412 ± 0.050", "–"),
        ("Sklearn (Tuned)", "Gradient Boosting (489 cây)", "0.1365", "0.0898", "0.9002", "0.1269 ± 0.024", "–"),
        ("Sklearn (Tuned)", "HistGradientBoosting (595 iter)", "0.1405", "0.0912", "0.8942", "0.1299 ± 0.022", "–"),
        ("Sklearn (Ensemble - B)", "Ensemble 4 mô hình (ENet/Ridge/GBR/HGB)", "0.1244", "0.0865", "0.9171", "0.1259 ± 0.035", "0.12573 (Nộp B)"),
        ("PyTorch MLP (C - Nhóm)", "PyTorch MLP (128-64-1 + Dropout 0.2)", "0.1252", "0.0902", "0.9123", "0.1312 ± 0.038", "0.12845 (Nộp C)")
    ]

    for r_idx, row in enumerate(data_rows, start=1):
        is_highlight = "Ensemble" in row[1] or "PyTorch" in row[1]
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            if is_highlight:
                cell.fill.fore_color.rgb = RGBColor(254, 243, 199) if "Ensemble" in row[1] else RGBColor(254, 235, 226)
            else:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if r_idx % 2 == 0 else c_white
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.5)
            if is_highlight:
                p.font.bold = True
                p.font.color.rgb = RGBColor(180, 83, 9) if "Ensemble" in row[1] else c_orange
            else:
                p.font.color.rgb = c_dark
            if c_idx >= 2:
                p.alignment = PP_ALIGN.CENTER

    pptx_path = "diary/Pipeline_Drawing.pptx"
    prs.save(pptx_path)
    print(f"Đã lưu file trình chiếu sơ đồ: {pptx_path}")

    # Convert to PDF
    pdf_path_diary = os.path.abspath("diary/Pipeline_Drawing.pdf")
    pdf_path_root = os.path.abspath("Pipeline_Drawing.pdf")
    
    ppt_app = win32com.client.Dispatch("PowerPoint.Application")
    ppt_app.Visible = 1
    deck = ppt_app.Presentations.Open(os.path.abspath(pptx_path))
    deck.SaveAs(pdf_path_diary, 32)
    deck.SaveAs(pdf_path_root, 32)
    deck.Close()
    ppt_app.Quit()
    print(f"Đã xuất file PDF sơ đồ luồng thành công:")
    print(f"  - {pdf_path_diary}")
    print(f"  - {pdf_path_root}")

if __name__ == "__main__":
    create_pipeline_presentation()
