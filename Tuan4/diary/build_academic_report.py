import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import win32com.client

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def build_report():
    doc = docx.Document()

    # Set page margins (1 inch all sides)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # -------------------------------------------------------------
    # TRANG BÌA (COVER PAGE)
    # -------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("TRƯỜNG ĐẠI HỌC SÀI GÒN\nKHOA CÔNG NGHỆ THÔNG TIN\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)

    r_line = p.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n\n")
    r_line.font.name = "Times New Roman"
    r_line.font.size = Pt(12)
    r_line.font.color.rgb = RGBColor(43, 108, 176)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run("BÁO CÁO BÀI TẬP THỰC HÀNH NHÓM (LAB 03)\n")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(14)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(221, 107, 32)

    r_main = p_title.add_run("DỰ ĐOÁN GIÁ BÁN NHÀ Ở AMES HOUSING\n(KAGGLE ADVANCED REGRESSION TECHNIQUES)\n\n")
    r_main.font.name = "Times New Roman"
    r_main.font.size = Pt(20)
    r_main.font.bold = True
    r_main.font.color.rgb = RGBColor(26, 54, 93)

    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c = p_course.add_run("Học phần: HỌC SÂU (DEEP LEARNING)\nLớp: DCT123C4\n\n\n\n")
    r_c.font.name = "Times New Roman"
    r_c.font.size = Pt(13)
    r_c.font.italic = True
    r_c.font.color.rgb = RGBColor(74, 85, 104)

    # Info table on cover
    info_table = doc.add_table(rows=5, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ("Giảng viên hướng dẫn:", "Thầy Đỗ Như Tài"),
        ("Nhóm sinh viên thực hiện:", "Nhóm thực hành Lab 03"),
        ("1. Vũ Việt Hoàng (Nhóm trưởng):", "MSSV: 3123411108 (Phụ trách PyTorch MLP & Báo cáo)"),
        ("2. Nguyễn Hữu Anh Khoa:", "Thành viên A (Khám phá EDA & Tiền xử lý)"),
        ("3. Nguyễn Đức Tài:", "Thành viên B (Mô hình Scikit-Learn & Ensemble)")
    ]
    for i, (label, val) in enumerate(info_data):
        row = info_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.8)
        c1.width = Inches(3.7)
        set_cell_margins(c0, 60, 60, 80, 80)
        set_cell_margins(c1, 60, 60, 80, 80)
        
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r0 = p0.add_run(label)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(11)
        r0.font.bold = True
        
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r1 = p1.add_run(val)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        if "3123411108" in val:
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(194, 65, 12)

    doc.add_paragraph("\n\n\n")
    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_d = p_date.add_run("THÀNH PHỐ HỒ CHÍ MINH, THÁNG 10 / 2026")
    r_d.font.name = "Times New Roman"
    r_d.font.size = Pt(11)
    r_d.font.bold = True
    r_d.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

    # Helper function for headings
    def add_heading_1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        r = h.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(26, 54, 93)
        return h

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        r = h.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(43, 108, 176)
        return h

    def add_body(text, bold_prefix="", italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(4)
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(11)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.italic = italic
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(3)
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(11)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        return p

    def add_callout(text, title="⚠️ LƯU Ý & ĐÍNH CHÍNH QUAN TRỌNG:"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "FEF3C7") # Warm Yellow
        set_cell_margins(cell, 120, 120, 150, 150)
        
        # Border
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="D97706"/>
                <w:top w:val="none"/>
                <w:right w:val="none"/>
                <w:bottom w:val="none"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        rt = p.add_run(title + "\n")
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(11)
        rt.font.bold = True
        rt.font.color.rgb = RGBColor(180, 83, 9)
        
        rc = p.add_run(text)
        rc.font.name = "Times New Roman"
        rc.font.size = Pt(10.5)
        rc.font.color.rgb = RGBColor(30, 41, 59)
        doc.add_paragraph()

    # -------------------------------------------------------------
    # BẢNG PHÂN CÔNG CÔNG VIỆC
    # -------------------------------------------------------------
    add_heading_1("BẢNG PHÂN CÔNG NHIỆM VỤ & ĐÓNG GÓP THÀNH VIÊN")
    
    t_assign = doc.add_table(rows=4, cols=5)
    t_assign.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_assign, "CBD5E1")

    headers_as = ["Thành viên", "MSSV", "Vai trò", "Nhiệm vụ đảm nhiệm chính", "Đóng góp"]
    widths_as = [Inches(1.5), Inches(1.1), Inches(1.0), Inches(2.3), Inches(0.6)]
    for c_i, (h, w) in enumerate(zip(headers_as, widths_as)):
        cell = t_assign.cell(0, c_i)
        cell.width = w
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Times New Roman"; r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)

    assign_rows = [
        ("Nguyễn Hữu Anh Khoa", "–", "Thành viên A", "EDA, Tiền xử lý thiếu, One-Hot Encoding, StandardScaler, Kỹ thuật đặc trưng (TotalSF, TotalBath...), Bàn giao 225 biến.", "100%"),
        ("Nguyễn Đức Tài", "–", "Thành viên B", "7 mô hình Scikit-Learn baseline, Thử nghiệm chọn biến Top-N, Tinh chỉnh siêu tham số, Ensemble 4 mô hình, Nộp Kaggle (0.12573).", "100%"),
        ("Vũ Việt Hoàng", "3123411108", "Nhóm trưởng (C)", "Xây dựng mạng Deep Learning PyTorch MLP, DataLoader/Dataset, Huấn luyện 120 Epochs, Thực nghiệm đối chứng Top 50, Vẽ Sơ đồ luồng, Nhật ký thực nghiệm, Báo cáo & Nộp bài.", "100%")
    ]
    for r_i, r_data in enumerate(assign_rows, 1):
        for c_i, val in enumerate(r_data):
            cell = t_assign.cell(r_i, c_i)
            cell.width = widths_as[c_i]
            set_cell_margins(cell, 60, 60, 80, 80)
            if r_i % 2 == 1: set_cell_background(cell, "F8FAFC")
            p = cell.paragraphs[0]
            if c_i in [1, 2, 4]: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.name = "Times New Roman"; r.font.size = Pt(9.5)
            if "3123411108" in val: r.font.bold = True

    # -------------------------------------------------------------
    # CHƯƠNG 1: GIỚI THIỆU & MỤC TIÊU
    # -------------------------------------------------------------
    add_heading_1("1. TỔNG QUAN ĐỀ TÀI & MỤC TIÊU DỰ ÁN")
    add_body("Bài toán dự đoán giá nhà Ames Housing là bài toán hồi quy kinh điển thuộc cuộc thi 'House Prices: Advanced Regression Techniques' trên nền tảng Kaggle. Dữ liệu bao gồm 79 biến mô tả chi tiết các thuộc tính căn nhà tại Ames, Iowa.")
    add_body("Mục tiêu trọng tâm của đồ án:", "Mục tiêu: ")
    add_bullet("Thiết kế đường ống tiền xử lý dữ liệu (Data Preprocessing Pipeline) chuẩn hóa, giải quyết triệt để giá trị khuyết thiếu và biến đổi phân phối mục tiêu.")
    add_bullet("Xây dựng, so sánh và tinh chỉnh các mô hình học máy truyền thống (Scikit-Learn) kết hợp chiến lược Ensemble để đạt điểm cao trên Kaggle.")
    add_bullet("Thiết kế mạng nơ-ron học sâu (Deep Learning Multi-Layer Perceptron) bằng PyTorch, khảo sát sự hội tụ và so sánh khả năng biểu diễn của học sâu với các mô hình cây trên dữ liệu bảng (Tabular Data).")
    add_bullet("Thước đo đánh giá: Root Mean Squared Logarithmic Error (RMSLE), tương đương RMSE trên thang đo log1p(SalePrice).")

    # -------------------------------------------------------------
    # CHƯƠNG 2: TIỀN XỬ LÝ & KỸ THUẬT ĐẶC TRƯNG (A)
    # -------------------------------------------------------------
    add_heading_1("2. TIỀN XỬ LÝ & KỸ THUẬT ĐẶC TRƯNG (NHÁNH A)")
    add_body("Thực hiện bởi Thành viên A - Nguyễn Hữu Anh Khoa.", "Phụ trách: ", italic=True)
    add_body("Biến mục tiêu SalePrice có phân phối lệch dương (Right-skewed) với đuôi dài. Áp dụng biến đổi y = log1p(SalePrice) đưa biến mục tiêu về dạng chuẩn Gauss (Mean ≈ 12.0241, Std ≈ 0.3994), triệt tiêu sự chi phối của các căn nhà có giá trị cá biệt.", "• Biến đổi logarit: ")
    add_body("Các cột mà 'NA' mang nghĩa không có tiện ích (PoolQC, GarageType, BsmtQual...) được điền 'None'. Các cột số tương ứng (GarageArea, BsmtFinSF...) được điền 0. LotFrontage được điền theo Median của từng khu phố (Neighborhood). Các biến phân loại thông thường được điền bằng Mode.", "• Xử lý khuyết thiếu (Missing values): ")
    add_body("Ordinal Encoding cho 17 đặc trưng có thứ bậc chất lượng (Ex: 5, Gd: 4, TA: 3, Fa: 2, Po: 1, None: 0). Áp dụng One-Hot Encoding (pd.get_dummies) cho các biến phân loại danh định còn lại.", "• Mã hóa biến (Encoding): ")
    add_body("Sinh 5 biến nghiệp vụ mới: TotalSF = 1stFlrSF + 2ndFlrSF + TotalBsmtSF; TotalBath = FullBath + 0.5*HalfBath + BsmtFullBath + 0.5*BsmtHalfBath; HouseAge = YrSold - YearBuilt; RemodAge = YrSold - YearRemodAdd; HasPool = (PoolArea > 0). Sau đó loại bỏ 9 cột gốc để triệt tiêu đa cộng tuyến.", "• Sinh đặc trưng mới (Feature Engineering): ")
    add_body("Áp dụng StandardScaler đưa toàn bộ 225 đặc trưng về phân phối chuẩn (Zero-mean, Unit-variance). Bàn giao các file: x_train.xlsx (1460×225), y_train.xlsx (1460×1), x_test.xlsx (1459×225).", "• Chuẩn hóa dữ liệu: ")

    # -------------------------------------------------------------
    # CHƯƠNG 3: MÔ HÌNH SCIKIT-LEARN & ENSEMBLE (B)
    # -------------------------------------------------------------
    add_heading_1("3. MÔ HÌNH HỌC MÁY SCIKIT-LEARN & ENSEMBLE (NHÁNH B)")
    add_body("Thực hiện bởi Thành viên B - Nguyễn Đức Tài.", "Phụ trách: ", italic=True)
    add_body("Chia tập dữ liệu 80% Train (1168 mẫu) và 20% Validation (292 mẫu) với random_state=42. Huấn luyện 7 mô hình baseline và thu được kết quả:", "• Baseline 7 mô hình: ")

    # Sklearn table
    t_sk = doc.add_table(rows=8, cols=5)
    t_sk.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_sk, "CBD5E1")
    sk_hd = ["Mô hình", "Val RMSE", "Val MAE", "Val R²", "Thời gian (s)"]
    sk_w = [Inches(2.5), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0)]
    for c_i, (h, w) in enumerate(zip(sk_hd, sk_w)):
        cell = t_sk.cell(0, c_i); cell.width = w; set_cell_background(cell, "2563EB")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = "Times New Roman"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
    
    sk_data = [
        ("Lasso (alpha=0.001)", "0.1194", "0.0841", "0.9236", "0.05"),
        ("ElasticNet (a=0.001, l1=0.5)", "0.1206", "0.0853", "0.9220", "0.07"),
        ("Ridge Regression (alpha=10)", "0.1218", "0.0864", "0.9205", "0.01"),
        ("Linear Regression", "0.1220", "0.0866", "0.9202", "0.03"),
        ("Gradient Boosting (500 cây)", "0.1395", "0.0913", "0.8957", "3.99"),
        ("HistGradientBoosting", "0.1408", "0.0921", "0.8938", "1.35"),
        ("Random Forest (300 cây)", "0.1458", "0.0944", "0.8861", "2.37")
    ]
    for r_i, r_data in enumerate(sk_data, 1):
        for c_i, val in enumerate(r_data):
            cell = t_sk.cell(r_i, c_i); cell.width = sk_w[c_i]
            set_cell_margins(cell, 50, 50, 70, 70)
            if r_i % 2 == 1: set_cell_background(cell, "F8FAFC")
            p = cell.paragraphs[0]
            if c_i >= 1: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val); r.font.name = "Times New Roman"; r.font.size = Pt(9.5)
            if r_i == 1: r.font.bold = True

    add_body("Sử dụng GridSearchCV cho mô hình tuyến tính (Ridge alpha=300, ElasticNet alpha=0.002, l1=0.8) và RandomizedSearchCV cho Boosting (GBR 489 cây, HistGB 595 iter).", "• Tinh chỉnh siêu tham số: ")
    add_body("Mặc dù mô hình tuyến tính đạt Val RMSE tốt trên tập Val 292 mẫu, nhưng độ lệch chuẩn trên 5-Fold CV rất cao (std 0.043–0.050). Do đó, Thành viên B chọn mô hình Ensemble trung bình đều của 4 mô hình đã tune (ElasticNet, Ridge, GBR, HistGB). Mô hình này đạt 5-Fold CV RMSE = 0.1259 (tốt nhất và ổn định nhất). Nộp file submission_sklearn.csv lên Kaggle và đạt điểm Public Score: 0.12573.", "• Ensemble & Kết quả Kaggle: ")

    # -------------------------------------------------------------
    # CHƯƠNG 4: MẠNG NƠ-RON DEEP LEARNING PYTORCH MLP (C)
    # -------------------------------------------------------------
    add_heading_1("4. XÂY DỰNG MẠNG DEEP LEARNING PYTORCH MLP (NHÁNH C)")
    add_body("Thực hiện bởi Thành viên C - Vũ Việt Hoàng (MSSV: 3123411108 - Nhóm trưởng).", "Phụ trách: ", italic=True)
    add_body("Notebook thực hiện: pytorch_sample_project/house_prices/pytorch_mlp.ipynb.", "Mã nguồn: ", italic=True)

    add_heading_2("4.1. Kiến trúc mạng nơ-ron đa tầng (HousePriceMLP)")
    add_body("Mạng nơ-ron được thiết kế theo cấu trúc truyền thẳng 3 tầng ẩn chuẩn học sâu:")
    add_bullet("Tầng Input: 225 đặc trưng đầu vào sau chuẩn hóa.")
    add_bullet("Tầng ẩn 1: Linear(225 → 128) + ReLU() + Dropout(p = 0.2). Chứa 28,928 tham số.")
    add_bullet("Tầng ẩn 2: Linear(128 → 64) + ReLU() + Dropout(p = 0.2). Chứa 8,256 tham số.")
    add_bullet("Tầng Output: Linear(64 → 1). Chứa 65 tham số. Dự đoán giá trị liên tục.")
    add_bullet("Tổng số tham số có thể huấn luyện: 37,121 tham số.")

    add_heading_2("4.2. Kỹ thuật tiền xử lý Tensor & Quản lý dữ liệu")
    add_bullet("Target Normalization: Chuẩn hóa biến mục tiêu log1p(SalePrice) về Zero-mean và Unit-variance (y_mean = 12.0307, y_std = 0.3904). Kỹ thuật này triệt tiêu hiện tượng gradient bùng nổ, giúp mạng hội tụ ổn định ngay từ Epoch đầu tiên.")
    add_bullet("CustomDataset & DataLoader: Xây dựng HousePriceDataset kế thừa torch.utils.data.Dataset; DataLoader huấn luyện với Batch Size = 32 (shuffle=True) và kiểm định với Batch Size = 64.")

    add_heading_2("4.3. Huấn luyện & Đánh giá mô hình")
    add_bullet("Hàm mất mát: nn.MSELoss().")
    add_bullet("Optimizer: Adam (Initial LR = 0.001, Weight Decay = 0.001 đóng vai trò điều chuẩn L2).")
    add_bullet("Bộ lập lịch học: ReduceLROnPlateau (factor=0.5, patience=8, min_lr=1e-5).")
    add_bullet("Thời gian thực thi: 120 Epochs trên GPU CUDA hoàn tất trong 7.29 giây.")
    add_bullet("Kết quả tối ưu: Mô hình chạm mốc Validation RMSE = 0.1252 (R² = 0.9123, MAE = 0.0902) tại Epoch 30. Trọng số tốt nhất được lưu và nạp lại để dự đoán.")

    # Embed plot 1 if exists
    if os.path.exists("diary/plot_1.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture("diary/plot_1.png", width=Inches(6.2))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c = p_cap.add_run("Hình 1: Đồ thị quá trình huấn luyện PyTorch MLP (Train MSE Loss và Validation RMSE qua 120 Epochs)")
        r_c.font.name = "Times New Roman"; r_c.font.size = Pt(9.5); r_c.font.italic = True; r_c.font.color.rgb = RGBColor(100, 116, 139)

    # Embed plot 2 if exists
    if os.path.exists("diary/plot_2.png"):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(6)
        p_img2.paragraph_format.space_after = Pt(2)
        doc.add_picture("diary/plot_2.png", width=Inches(6.2))
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c2 = p_cap2.add_run("Hình 2: Phân tích kết quả dự đoán trên tập Validation (Actual vs Predicted và Phân phối sai số Residuals)")
        r_c2.font.name = "Times New Roman"; r_c2.font.size = Pt(9.5); r_c2.font.italic = True; r_c2.font.color.rgb = RGBColor(100, 116, 139)

    # -------------------------------------------------------------
    # CHƯƠNG 5: THỰC NGHIỆM ĐỐI CHỨNG & ĐÍNH CHÍNH SỐ LIỆU
    # -------------------------------------------------------------
    add_heading_1("5. THỰC NGHIỆM ĐỐI CHỨNG (ABLATION) & ĐÍNH CHÍNH SỐ LIỆU")

    # Important Callout Box
    add_callout(
        "Theo rà soát phản hồi từ Thành viên B: Trong bản ghi chép dự thảo ban đầu, phần nhận xét về tác động của việc chọn đặc trưng trên mô hình MLP bị ghi nhầm là 'giảm từ 0.2902 → 0.2161 (cải thiện)'.\n\n"
        "ĐÍNH CHÍNH CHÍNH XÁC THEO KẾT QUẢ THỰC NGHIỆM THỰC TẾ:\n"
        "Khi rút gọn xuống Top 50 đặc trưng (theo ranking của Gradient Boosting), hiệu suất của PyTorch MLP BỊ GIẢM MẠNH (RMSE tăng vọt):\n"
        "  • Mô hình Raw (chưa chuẩn hóa y): RMSE thực tế tăng từ 0.2732 lên 0.3588 (xấu đi).\n"
        "  • Mô hình Tối ưu (đã chuẩn hóa y): RMSE thực tế tăng từ 0.1252 lên 0.5332 (xấu đi rõ rệt).\n\n"
        "GIẢI THÍCH NGUYÊN NHÂN HỌC MÁY:\n"
        "Mô hình cây (GBR, Random Forest) phân nhánh độc lập theo từng đặc trưng riêng rẽ nên việc giữ Top 50 vẫn bảo toàn thông tin chính. Ngược lại, mạng nơ-ron MLP dựa trên biểu diễn phân phối của toàn bộ không gian biến sau One-Hot Encoding. Việc cắt giảm biến làm đứt gãy quan hệ đa chiều giữa các biến hạng mục, khiến mạng mất khả năng xấp xỉ hàm giá trị phức tạp."
    )

    # Ablation comparison table
    t_ab = doc.add_table(rows=4, cols=5)
    t_ab.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_ab, "CBD5E1")
    ab_hd = ["Mô hình", "225 đặc trưng", "Top 50 đặc trưng", "Độ lệch RMSE", "Nhận xét xu hướng"]
    ab_w = [Inches(2.3), Inches(1.1), Inches(1.1), Inches(1.0), Inches(1.0)]
    for c_i, (h, w) in enumerate(zip(ab_hd, ab_w)):
        cell = t_ab.cell(0, c_i); cell.width = w; set_cell_background(cell, "B45309")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = "Times New Roman"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)

    ab_rows = [
        ("Gradient Boosting (GBR)", "0.1395", "0.1400", "+0.0005", "Gần như không đổi (ổn định)"),
        ("PyTorch MLP (Raw)", "0.2732", "0.3588", "+0.0856", "HIỆU SUẤT GIẢM (Xấu đi)"),
        ("PyTorch MLP (Tuned - C)", "0.1252", "0.5332", "+0.4080", "HIỆU SUẤT GIẢM MẠNH")
    ]
    for r_i, r_data in enumerate(ab_rows, 1):
        for c_i, val in enumerate(r_data):
            cell = t_ab.cell(r_i, c_i); cell.width = ab_w[c_i]
            set_cell_margins(cell, 50, 50, 70, 70)
            if "MLP" in r_data[0]: set_cell_background(cell, "FEF3C7")
            elif r_i % 2 == 1: set_cell_background(cell, "F8FAFC")
            p = cell.paragraphs[0]
            if c_i in [1, 2, 3]: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val); r.font.name = "Times New Roman"; r.font.size = Pt(9.5)
            if "MLP" in r_data[0]: r.font.bold = True

    # -------------------------------------------------------------
    # CHƯƠNG 6: TỔNG HỢP SO SÁNH & KẾT QUẢ KAGGLE
    # -------------------------------------------------------------
    add_heading_1("6. TỔNG HỢP SO SÁNH SKLEARN VS PYTORCH & KẾT QUẢ KAGGLE")

    t_all = doc.add_table(rows=11, cols=6)
    t_all.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_all, "CBD5E1")
    all_hd = ["Nhóm", "Mô hình / Cấu hình", "Val RMSE", "Val R²", "CV5 RMSE", "Kaggle Score"]
    all_w = [Inches(1.2), Inches(2.2), Inches(0.8), Inches(0.8), Inches(1.1), Inches(1.1)]
    for c_i, (h, w) in enumerate(zip(all_hd, all_w)):
        cell = t_all.cell(0, c_i); cell.width = w; set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = "Times New Roman"; r.font.size = Pt(9); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)

    all_data = [
        ("Sklearn", "Linear Regression", "0.1220", "0.9202", "–", "–"),
        ("Sklearn", "Ridge Regression (alpha=10)", "0.1218", "0.9205", "–", "–"),
        ("Sklearn", "Lasso (alpha=0.001)", "0.1194", "0.9236", "–", "–"),
        ("Sklearn", "Random Forest (300)", "0.1458", "0.8861", "–", "–"),
        ("Sklearn", "Ridge (tuned, alpha=300)", "0.1245", "0.9170", "0.1387 ± 0.043", "–"),
        ("Sklearn", "ElasticNet (tuned)", "0.1193", "0.9238", "0.1412 ± 0.050", "–"),
        ("Sklearn", "Gradient Boosting (tuned)", "0.1365", "0.9002", "0.1269 ± 0.024", "–"),
        ("Sklearn", "HistGB (tuned)", "0.1405", "0.8942", "0.1299 ± 0.022", "–"),
        ("Sklearn (B)", "Ensemble 4 mô hình (Nộp B)", "0.1244", "0.9171", "0.1259 ± 0.035", "0.12573"),
        ("PyTorch (C)", "PyTorch HousePriceMLP (Nộp C)", "0.1252", "0.9123", "0.1312 ± 0.038", "0.12845")
    ]
    for r_i, r_data in enumerate(all_data, 1):
        for c_i, val in enumerate(r_data):
            cell = t_all.cell(r_i, c_i); cell.width = all_w[c_i]
            set_cell_margins(cell, 45, 45, 60, 60)
            is_sub = ("Ensemble" in r_data[1] or "PyTorch HousePriceMLP" in r_data[1])
            if is_sub:
                set_cell_background(cell, "FEF3C7" if "Ensemble" in r_data[1] else "FCE7F3")
            elif r_i % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            p = cell.paragraphs[0]
            if c_i in [0, 2, 3, 4, 5]: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val); r.font.name = "Times New Roman"; r.font.size = Pt(8.5)
            if is_sub: r.font.bold = True

    add_heading_1("7. KẾT LUẬN & ĐÓNG GÓI BÀI NỘP")
    add_bullet("Cả hai nhánh mô hình (Sklearn Ensemble và PyTorch MLP) đều đạt kết quả xuất sắc (Val RMSE ~0.124–0.125, điểm Kaggle 0.12573).")
    add_bullet("Mô hình Ensemble cây + tuyến tính thể hiện độ ổn định vượt trội trên dữ liệu dạng bảng.")
    add_bullet("Mạng nơ-ron PyTorch MLP chứng minh tiềm năng biểu diễn phi tuyến mạnh mẽ nếu được chuẩn hóa target và áp dụng Dropout điều chuẩn đúng cách.")
    add_bullet("Toàn bộ sản phẩm bài làm đã được tổ chức khoa học, chạy nghiệm thu thực tế và đóng gói thành tệp nén theo đúng quy định.")

    docx_path = "Bao_Cao_Lab03_HousePrice.docx"
    doc.save(docx_path)
    print(f"Đã lưu file Word báo cáo: {docx_path}")

    # Convert to PDF via Word COM
    pdf_path_1 = os.path.abspath("Bao_Cao_Lab03_HousePrice.pdf")
    pdf_path_2 = os.path.abspath("Bao_cao_ML_Project.pdf")

    word_app = win32com.client.Dispatch("Word.Application")
    word_app.Visible = False
    doc_com = word_app.Documents.Open(os.path.abspath(docx_path))
    # 17 is wdExportFormatPDF
    doc_com.SaveAs(pdf_path_1, 17)
    doc_com.SaveAs(pdf_path_2, 17)
    doc_com.Close(False)
    word_app.Quit()

    print(f"Đã xuất file PDF báo cáo thành công:")
    print(f"  - {pdf_path_1}")
    print(f"  - {pdf_path_2}")

if __name__ == "__main__":
    build_report()
