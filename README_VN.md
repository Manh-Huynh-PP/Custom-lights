# Custom Lights
**Thiết lập Ánh sáng Chuyên nghiệp Dễ dàng trong Blender.**

Custom Lights là một addon thông minh được thiết kế để tinh giản và tăng tốc quy trình làm việc với ánh sáng trong Blender. Bằng cách kết hợp các công cụ tạo ánh sáng nhanh với giao diện quản lý tập trung, nó cho phép bạn thiết lập các cảnh ánh sáng chuyên nghiệp chỉ trong vài giây, giúp bạn tiết kiệm thời gian quý báu để tập trung vào các khía cạnh sáng tạo của tác phẩm 3D.

## Hỗ trợ & Mua hàng

- **Sở hữu Addon:** [Gumroad](https://manhdesigns.gumroad.com/l/customlights)
- **Hỗ trợ phát triển:** [Buy Me a Coffee](https://coffee.manhhuynh.work)

### 🎥 [Xem Video Demo Phiên bản 2.0](https://youtube.com/shorts/s9AEGNVPpMQ) | [Demo v1](https://www.youtube.com/shorts/VkU7IYyqykY)

---

## Có gì mới trong Custom Lights 2.0

### 🎥 [Xem Video Demo Tính năng v2.0](https://youtube.com/shorts/s9AEGNVPpMQ)

### 🚀 Tương thích Blender 5.0
Đã được cập nhật và kiểm tra đầy đủ để đảm bảo hiệu suất mượt mà với phiên bản Blender 5.0 mới nhất.

### 🌍 Điều khiển Độ sáng Thế giới (World Brightness)
Nhanh chóng điều chỉnh độ sáng môi trường/thế giới của cảnh trực tiếp từ bảng Manage Lights.

### 🎚️ Bộ nhân Độ sáng Bộ sưu tập (Collection Brightness Multiplier)
Thanh trượt mới trên mỗi đầu mục bộ sưu tập để nhân độ sáng của tất cả đèn trong bộ sưu tập đó. Nhấn nút ✓ để áp dụng và thiết lập lại.

### 🎨 Chia tách Plane Gradient Light
Gradient Light Plane hiện được chia thành hai toán tử riêng biệt:
- **Linear Gradient** - Tạo các mặt phẳng phát xạ gradient tuyến tính
- **Sphere Gradient** - Tạo các mặt phẳng phát xạ gradient hình cầu

Cả hai đều bao gồm hộp kiểm **"Transparent Black Gradient"** mới giúp các vùng màu đen của gradient trở nên trong suốt.

### ✨ Plane Gobo Lights
Ba toán tử plane gobo mới để tạo hiệu ứng vân sáng nhanh chóng:
- **P.Noise** - Vân gobo dựa trên Noise
- **P.Voronoise** - Kiểu mẫu vân Voronoi
- **P.Wave** - Vân gobo kiểu sóng

### 🌡️ Màu sắc Black Body Chính xác
Cập nhật các giá trị màu Black Body để phù hợp hoàn hảo với các tính toán ánh sáng vật lý của Blender.

### ⚡ Phím tắt Truy cập Nhanh "L"
Nhấn **"L"** khi chọn các đèn để mở menu popup điều chỉnh tham số (hỗ trợ điều chỉnh đồng thời nhiều đèn được chọn), hoặc mở Viewport Pie Menu nếu không chọn đèn nào.

### 🌐 Cập nhật Light Dome
Những cải tiến đáng kể cho tính năng Light Dome để chiếu sáng môi trường tốt hơn.

### 🔦 Cải tiến Gobo Light
- **Gobo Light Noise:** Thêm sự biến đổi tự nhiên và kết cấu cho đèn của bạn.
- **Image Gobo Light:** Chiếu hình ảnh và hoa văn cho các hiệu ứng ánh sáng phức tạp.

### 🎨 Cập nhật UI & Manage Light
- **Bộ lọc loại đèn trực quan:** Lọc đèn nhanh trong N-panel theo các nhóm (Tất cả, Đèn cơ bản, Đèn Mesh, Gobo).
- **Chế độ Solo / Isolate:** Tập trung tinh chỉnh một nguồn sáng duy nhất bằng nút Solo. Các đèn khác sẽ tự động ẩn tạm thời và khôi phục khi tắt Solo.
- **Quản lý Collection bị loại trừ:** Bật/tắt trạng thái loại trừ (exclude) của collection trực tiếp từ panel và tránh lỗi Runtime khi chọn đèn thuộc collection đang bị ẩn.
- **Xóa đèn nhanh:** Xóa nhanh bất kỳ đèn nào khỏi danh sách bằng nút biểu tượng thùng rác.

### ☀️ Tinh chỉnh góc xoay HDRI (HDRI Z-Rotation)
Xoay bản đồ môi trường (HDRI) trực tiếp từ mục điều khiển World bằng thanh trượt góc xoay trục Z.

### 🎛️ Bảng Điều khiển Thuộc tính Gobo Thời gian thực
Tinh chỉnh trực tiếp các thông số của các node Noise, Voronoi, Wave, Image, Mapping, và ColorRamp của đèn Gobo hoặc Mesh Gobo trực tiếp trên thanh Sidebar mà không cần mở Shader Editor.

### 🥧 Pie Menu Thao Tác Nhanh (Phím "L" khi không chọn đèn)
Tạo nhanh các loại đèn cơ bản/tùy chỉnh, bật tắt Solo hoặc gọi menu thông số đèn ngay dưới vị trí con trỏ chuột trong viewport 3D. Nhấn phím **"L"** khi không có đèn nào được chọn để mở menu này.

---

## Các Tính năng Chính

### 1. Thêm Đèn Cơ bản (Add Base Lights)
Nhanh chóng tạo các đèn tiêu chuẩn của Blender tại vị trí con trỏ.
- **Các loại:** Point, Sun, Spot, Area (Rectangle/Ellipse).
- **Tự động Tổ chức:** Tự động nhóm các đèn vào các bộ sưu tập (collections).

### 2. Đèn & Công cụ Tùy chỉnh (Custom Lights & Tools)
Các công cụ chiếu sáng nâng cao cho các tình huống phức tạp.

- **Tracker Light:** Đèn Area tự động hướng theo một đối tượng mục tiêu.
- **Linear/Sphere Gradient Plane:** Các mặt phẳng phát xạ với gradient có thể điều chỉnh và tùy chọn trong suốt vùng đen.
- **Translucent Light Plane:** Mặt phẳng khuếch tán để làm mềm bóng đổ và tạo hiệu ứng studio.
- **Simple God Rays:** Hiệu ứng "Tia sáng của Chúa" (volumetric) cho đèn Spot.
- **Plane Gobos:** Các gobo vân noise, voronoise và wave nhanh chóng.
- **Track to Selected:** Áp dụng ràng buộc "Track To" cho nhiều đối tượng.
- **Make Emission Mesh:** Chuyển đổi bất kỳ lưới (mesh) nào thành nguồn sáng.
- **Input Blackbody Color:** Thiết lập màu đèn bằng giá trị nhiệt độ Kelvin.

### 3. Quản lý Đèn (Manage Lights)
Trung tâm điều khiển cho tất cả ánh sáng trong cảnh.
- **Chế độ xem Tập trung:** Tất cả đèn và lưới phát xạ được sắp xếp theo bộ sưu tập.
- **Độ sáng Bộ sưu tập:** Nhân độ sáng của tất cả đèn trong một bộ sưu tập.
- **Độ sáng Thế giới:** Điều khiển cường độ ánh sáng môi trường.
- **Điều khiển Trực tiếp:** Điều chỉnh Màu sắc, Độ sáng/Công suất và Kích thước/Hình dạng từ danh sách.
- **Lựa chọn:** Nhấp vào tên để chọn đèn hoặc toàn bộ bộ sưu tập.
- **Hiển thị:** Bật/tắt hiển thị trong Viewport, Render và Camera.

---

## Cài đặt & Bắt đầu

1.  **Cài đặt:**
    - Tải xuống tệp `custom_light.zip`.
    - Mở Blender và đi tới **Edit > Preferences > Add-ons**.
    - Nhấp vào **Install...**, chọn tệp zip và bật "Custom Lights".

2.  **Vị trí:**
    - Trong 3D Viewport, nhấn **"N"** để mở Sidebar.
    - Nhấp vào tab **"Custom Lights"**.

3.  **Bắt đầu Chiếu sáng:**
    - Sử dụng các bảng điều khiển để thêm đèn, áp dụng hiệu ứng hoặc quản lý ánh sáng cho cảnh của bạn.

---

## Nhật ký thay đổi (Changelog)

Xem toàn bộ lịch sử thay đổi tại tệp [CHANGELOG.md](file:///e:/BLENDER/ADDON/Custom-light/custom_light/CHANGELOG.md).

### [2.1.4] - 2026-06-17
- **Nâng cấp giao diện chỉnh phím tắt**: Thiết kế lại giao diện chỉnh sửa phím tắt gọn gàng, ẩn tên hàm nội bộ và hiển thị các phím bổ trợ trực tiếp dưới dạng các nút bấm bật/tắt tiện lợi.
- **Bổ sung liên kết Website Addon**: Cấu hình địa chỉ repository GitHub vào thông số manifest và metadata `bl_info`.
- **Sửa lỗi crash giao diện Preferences**: Khắc phục lỗi crash khi cấu hình addon trong Preferences do sử dụng icon không tồn tại `KEYBOARD_KEY` (đã đổi thành `PREFERENCES`).
- **Sửa lỗi reset cài đặt hiển thị (Visibility Reset)**: Dùng cờ hiệu `is_initializing` để sửa lỗi tự động đưa Cycles ray visibility về mặc định khi gọi menu Quick Adjust (phím `L`).

### [2.1.3] - 2026-06-15
- **Kiểm tra khả thi giao diện Gradient**: Các tùy chọn "Flip Gradient" và "Rotate Gradient" trong bảng Quick Adjust (phím `L`) nay chỉ được vẽ khi khả thi dựa trên sự tồn tại của các node tương ứng.
- **Khắc phục lỗi crash Blender**: Thay đổi hai operator Flip/Rotate thành dạng `INTERNAL` để ngăn lỗi crash Blender (`MSVCP140.dll` / `wm_block_redo_cb`) khi thực thi từ bên trong menu popup tạm thời. Đồng thời hỗ trợ thao tác Undo thủ công qua lệnh `undo_push()`.
- **Sửa lỗi logic Solo Light**: Sửa lỗi tự động kích hoạt lại chế độ Solo Mode cho đèn mới được chọn sau khi bạn đã tắt chế độ Solo của đèn trước đó qua bảng popup.

### [2.1.2] - 2026-06-15
- **Điều chỉnh nhiều đèn cùng lúc (Multi-Light Quick Adjust)**: Nhấn `L` khi chọn nhiều đèn để mở menu popup điều chỉnh thông số cho tất cả đèn được chọn.
- **Phân nhóm thông số động**: Menu tự động phát hiện các loại đèn được chọn (Area, Spot, Point) và hiển thị các trường thông số phù hợp.
- **Đồng bộ thời gian thực**: Thay đổi giá trị trên các thanh trượt sẽ lập tức áp dụng cho mọi đèn được chọn cùng loại tương ứng.

### [2.1.1] - 2026-06-15
- **Tùy chỉnh Collection Đích**: Cho phép chọn chế độ tạo mới hoặc chọn collection có sẵn ngay tại N-panel để chèn đèn.
- **Phím tắt Thông minh (`L`)**: Nhấn `L` sẽ tự động mở bảng Quick Adjust (nếu đang chọn đèn) hoặc mở Viewport Pie Menu (nếu chọn đối tượng khác hoặc không chọn gì). Loại bỏ phím tắt `Shift + Alt + L`.
- **Tự động Active Collection**: Khi thêm đèn, collection đích sẽ tự động được kích hoạt và thêm vào View Layer nếu đang bị ẩn/loại trừ để tránh lỗi Runtime.
- **Sửa lỗi AttributeError**: Khắc phục lỗi crash khiến bảng Manage Lights bị biến mất hoàn toàn.
- **Mặc định số lượng đèn Tracker**: Đổi mặc định số lượng đèn khi tạo Tracker Light từ 1 thành 3.

### [2.1.0] - 2026-06-15
- **Viewport Pie Menu** giúp tạo nhanh đèn, toggle Solo và Quick Adjust.
- **Xoay môi trường HDRI (HDRI Z-Rotation)** trực tiếp bằng thanh trượt trục Z.
- **Bảng điều khiển Gobo thời gian thực** ngay trên Sidebar (hỗ trợ ColorRamp trực quan).
- **Chế độ Solo / Cô lập đèn** để tập trung tinh chỉnh nguồn sáng riêng lẻ.
- **Quản lý Collection Exclude/Include** trực tiếp trên N-panel bảo vệ lỗi Runtime.
- **Bộ lọc loại đèn (Tabs)** tại đầu bảng Manage Lights (Tất cả, Đèn cơ bản, Đèn Mesh, Gobo).
- **Xóa đèn nhanh** (nút thùng rác) trực tiếp trong danh sách Manage Lights.
- **Tối ưu hóa gom nhóm Collection** hạn chế rác Outliner.

---

*Chúc bạn làm việc hiệu quả!*
