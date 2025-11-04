# Claude Code Statusline - Thanh trạng thái đẹp cho Claude Code

<div align="center">

**Hiển thị thông tin thời gian thực về phiên làm việc với Claude Code**

*Theo dõi model, Git, session timer, tokens, chi phí và context usage*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)

</div>

---

## ✨ Tính năng

Hiển thị đầy đủ thông tin về phiên làm việc Claude Code:

- **🤖 Model Info** - Tên model đang sử dụng
- **🌿 Git Integration** - Branch hiện tại và trạng thái (clean/dirty)
- **⏱ Session Timer** - Thời gian còn lại trong khối 5 giờ với progress bar
- **💬 Request Counter** - Số lượng requests trong session
- **📊 Token Statistics** - Tổng tokens đã dùng và burn rate (tokens/phút)
- **💵 Cost Tracking** - Chi phí thực tế bằng USD
- **📈 Context Usage** - % context window đã sử dụng (của 200K tokens)
- **📝 Code Stats** - Dòng code đã thêm/xóa
- **🎨 Colorful Display** - Màu sắc đẹp mắt với emoji

---

## 📋 Yêu cầu hệ thống

### Bắt buộc
- **Python 3.6+** - Chạy statusline script
- **Claude Code** - Công cụ bạn đang sử dụng

### Tùy chọn (để có đầy đủ tính năng)
- **Git** - Hiển thị branch (thường đã có sẵn)
- **ccusage** - Lấy thống kê usage chi tiết (tự động cài qua npx)

---

## 🚀 Cài đặt nhanh

### Bước 1: Tải script

**Cách 1: Clone từ GitHub (khuyến nghị)**
```bash
git clone https://github.com/yourusername/claude-code-statusline.git
cd claude-code-statusline
```

**Cách 2: Tải trực tiếp**
- Tải file `statusline.py` về máy

### Bước 2: Chạy script cài đặt

**Trên Windows:**
```cmd
install.bat
```

**Trên Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

Script sẽ tự động:
1. ✅ Copy `statusline.py` vào `~/.claude/statusline.py`
2. ✅ Cấu hình file `~/.claude/settings.json`
3. ✅ Khởi động lại Claude Code (nếu cần)

### Bước 3: Khởi động lại Claude Code

Sau khi cài đặt, khởi động lại Claude Code để thấy statusline mới!

---

## 🛠️ Cài đặt thủ công

Nếu không muốn dùng script tự động:

### 1. Copy file statusline.py

**Windows:**
```cmd
copy statusline.py "%USERPROFILE%\.claude\statusline.py"
```

**Linux/macOS:**
```bash
cp statusline.py ~/.claude/statusline.py
chmod +x ~/.claude/statusline.py
```

### 2. Cấu hình Claude Code

Mở file `~/.claude/settings.json` và thêm:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python ~/.claude/statusline.py"
  }
}
```

**Lưu ý Windows:** Đường dẫn có thể là:
```json
{
  "statusLine": {
    "type": "command",
    "command": "python C:\\Users\\YourUsername\\.claude\\statusline.py"
  }
}
```

### 3. Khởi động lại Claude Code

---

## 📊 Ví dụ hiển thị

```
🤖 Sonnet 4.5 │ 🌿 main │ ⏱ 4h 32m until reset at 18:00 (12%) [=----------] │ 💬 15 requests │ 📊 45,230 tok (450 tpm) │ 💵 $0.23 │ 📈 23.6% │ +120 -45
```

**Giải thích:**
- `🤖 Sonnet 4.5` - Model đang dùng
- `🌿 main` - Git branch (🔴 nếu có thay đổi chưa commit)
- `⏱ 4h 32m...` - Còn 4h32m cho đến khi session reset (12% đã dùng)
- `💬 15 requests` - Đã gửi 15 requests
- `📊 45,230 tok (450 tpm)` - Tổng 45,230 tokens, tốc độ 450 tokens/phút
- `💵 $0.23` - Chi phí $0.23
- `📈 23.6%` - Đã dùng 23.6% context window
- `+120 -45` - Thêm 120 dòng, xóa 45 dòng

---

## 🎨 Màu sắc

Statusline tự động tô màu theo trạng thái:

### Session Timer
- 🟢 **Xanh** - Còn >25% thời gian
- 🟡 **Vàng** - Còn 10-25% thời gian
- 🔴 **Đỏ** - Còn <10% thời gian

### Context Usage
- 🟢 **Xanh** - <50% context
- 🟡 **Vàng** - 50-80% context
- 🔴 **Đỏ** - >80% context (sắp đầy!)

### Git Status
- 🌿 **Xanh** - Clean (không có thay đổi)
- 🔴 **Đỏ** - Dirty (có thay đổi chưa commit)

---

## 🔧 Cách hoạt động

### 1. Nguồn dữ liệu

Script đọc dữ liệu từ 3 nguồn:

#### a) **Input JSON từ Claude Code** (qua stdin)
```json
{
  "model": { "display_name": "Sonnet 4.5" },
  "workspace": { "current_dir": "/path/to/project" },
  "transcript_path": "/path/to/transcript.jsonl",
  "cost": {
    "total_lines_added": 120,
    "total_lines_removed": 45
  }
}
```

#### b) **Transcript File** (`transcript.jsonl`)
File này chứa lịch sử tất cả API calls:
```json
{"timestamp": "2025-10-08T12:20:00Z", "message": {"usage": {"input_tokens": 1234, ...}}}
{"timestamp": "2025-10-08T12:25:00Z", "message": {"usage": {"input_tokens": 2345, ...}}}
```

Script phân tích:
- Timestamps → Tính toán khối 5 giờ
- Usage tokens → Tính context length

#### c) **Lệnh `ccusage`** (nếu có)
```bash
ccusage blocks --json
```

Trả về thông tin chi tiết về session hiện tại:
- Thời gian reset
- Total tokens
- Chi phí USD
- Burn rate (tokens/phút)
- Số requests

### 2. Thuật toán tính Session Blocks

Script chia timeline thành các khối 5 giờ:

```
Timeline:
12:00 ─────────────── 17:00    Block 1 (5h)
                        │
                        ├─── Gap (không hoạt động)
                        │
09:00 ─────────────── 14:00    Block 2 (5h)
```

**Logic:**
1. Đọc tất cả timestamps từ transcript
2. Floor về đầu giờ (12:20 → 12:00)
3. Nếu gap >5h giữa 2 timestamps → Tạo block mới
4. Tính usage cho từng block

### 3. Hiển thị thông tin

Script ghép các phần lại với separator `│` và màu sắc:

```python
parts = [model_info, git_info, session_timer, requests, tokens, cost, context, code_stats]
output = " │ ".join(parts)
print(output)
```

---

## 🔍 Chi tiết kỹ thuật

### Cấu trúc code

```python
# 1. Định nghĩa màu sắc (ANSI RGB codes)
class Colors:
    CYAN = "\033[38;2;0;240;255m"
    # ...

# 2. Các hàm tiện ích
def get_context_length_from_transcript(path):
    # Parse transcript để lấy context length

def get_block_start_time(path):
    # Tính thời điểm bắt đầu block 5h

def get_usage_info_from_ccusage():
    # Lấy thông tin từ ccusage

def get_git_info(cwd):
    # Lấy branch và status

# 3. Logic chính
data = json.load(sys.stdin)  # Đọc input
# ... thu thập dữ liệu ...
parts = [...]  # Xây dựng từng phần
print(" │ ".join(parts))  # In ra
```

### Performance

- **Execution time:** ~50-100ms (rất nhanh!)
- **Memory:** ~2-5MB
- **Dependencies:** Chỉ Python 3.6+ (built-in libraries)

---

## 🐛 Xử lý lỗi

### Statusline không hiển thị?

**1. Kiểm tra Python:**
```bash
python --version
# hoặc
python3 --version
```
Cần Python 3.6+

**2. Kiểm tra file tồn tại:**
```bash
ls ~/.claude/statusline.py
# Windows: dir %USERPROFILE%\.claude\statusline.py
```

**3. Kiểm tra settings.json:**
```bash
cat ~/.claude/settings.json
# Windows: type %USERPROFILE%\.claude\settings.json
```

Phải có cấu hình `statusLine`

**4. Test thủ công:**
```bash
echo '{"model":{"display_name":"Test"},"workspace":{"current_dir":"."},"transcript_path":"","cost":{}}' | python ~/.claude/statusline.py
```

### Thiếu tính năng?

**Không có session timer / tokens:**
- Cài đặt `ccusage`: `npm install -g ccusage`
- Hoặc dùng qua npx (tự động)

**Không có git branch:**
- Cài đặt git: https://git-scm.com/

**Context % không chính xác:**
- Đảm bảo transcript_path hợp lệ
- Kiểm tra file transcript.jsonl có tồn tại

---

## 🎯 Tùy chỉnh

### Thay đổi màu sắc

Chỉnh sửa class `Colors` trong `statusline.py`:

```python
class Colors:
    CYAN = "\033[38;2;0;240;255m"     # Thay đổi RGB (R, G, B)
    BLUE = "\033[38;2;100;150;255m"
    # ...
```

Công cụ chọn màu: https://www.rapidtables.com/web/color/RGB_Color.html

### Bỏ emoji

Tìm và thay các emoji:
```python
# Từ:
parts.append(f"{Colors.CYAN}{Colors.BOLD}🤖 {model}{Colors.RESET}")

# Thành:
parts.append(f"{Colors.CYAN}{Colors.BOLD}Model: {model}{Colors.RESET}")
```

### Tắt một số tính năng

Comment dòng tương ứng:

```python
# Tắt git branch
# if branch:
#     git_icon = "🔴" if is_dirty else "🌿"
#     parts.append(f"{Colors.GREEN}{git_icon} {branch}{Colors.RESET}")
```

---

## 📚 FAQ

### 1. Tại sao cần ccusage?

`ccusage` cung cấp thông tin chi tiết về usage mà transcript không có:
- Thời gian reset chính xác
- Burn rate (tokens/phút)
- Chi phí theo từng model

Không có `ccusage`, statusline vẫn hoạt động nhưng thiếu các thông tin này.

### 2. Session block 5 giờ là gì?

Claude Code tính usage theo khối 5 giờ. Script tự động:
- Phát hiện khi bạn bắt đầu session mới
- Tính thời gian còn lại đến khi reset
- Hiển thị progress bar

### 3. Có tốn phí không?

Script này **HOÀN TOÀN MIỄN PHÍ** và không gây ra API calls bổ sung. Nó chỉ đọc dữ liệu đã có sẵn.

### 4. Tương thích với OS nào?

- ✅ **Windows 10/11**
- ✅ **macOS** (Intel & Apple Silicon)
- ✅ **Linux** (Ubuntu, Debian, Fedora, Arch...)

### 5. Có thể dùng cho nhiều projects?

Có! Cài đặt ở `~/.claude/` (global) sẽ áp dụng cho tất cả projects.

Hoặc tạo `.claude/statusline.py` riêng cho từng project.

---

## 🤝 Đóng góp

Contributions rất được hoan nghênh!

### Cách đóng góp:

1. Fork repo này
2. Tạo branch mới: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push lên branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

### Ý tưởng đóng góp:

- 🐛 Sửa bugs
- ✨ Thêm tính năng mới
- 📚 Cải thiện documentation
- 🎨 Thêm color themes
- 🌍 Dịch sang ngôn ngữ khác

---

## 📝 Changelog

### v1.0.0 (2025-01-04)
- 🎉 Initial release
- ✨ Hiển thị model, git, session timer, tokens, cost, context
- 🎨 Màu sắc đẹp mắt với emoji
- 🔧 Tích hợp ccusage
- 📦 Scripts cài đặt tự động

---

## 📄 License

MIT License - Xem file [LICENSE](LICENSE) để biết chi tiết.

Bạn được tự do:
- ✅ Sử dụng cho mục đích cá nhân và thương mại
- ✅ Sửa đổi và phân phối
- ✅ Tích hợp vào projects của bạn

---

## 🙏 Credits

**Công nghệ sử dụng:**
- [ccusage](https://github.com/ryoppippi/ccusage) - Claude Code usage analytics
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - Official docs

**Cảm hứng từ:**
- [cc-statusline](https://github.com/chongdashu/cc-statusline) - TypeScript version

---

<div align="center">

**Made with ❤️ for Claude Code users**

⭐ Nếu thấy hữu ích, hãy star repo này! ⭐

[Report Bug](https://github.com/yourusername/claude-code-statusline/issues) · [Request Feature](https://github.com/yourusername/claude-code-statusline/issues)

</div>
