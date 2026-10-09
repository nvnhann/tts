# TTS truyện tiếng Việt với VieNeu-TTS

Chuyển các chương truyện dạng `.txt` thành audio `.mp3` bằng
[VieNeu-TTS v3 Turbo](https://github.com/pnnbao97/VieNeu-TTS) (48 kHz, 25 giọng có sẵn, chạy GPU).

- Mỗi file `.txt` sẽ thành một file `.mp3` cùng tên (`0001.txt` → `0001.mp3`).
- File `.mp3` nào đã có thì được bỏ qua, nên chạy lại sẽ làm tiếp từ chỗ dừng.
- Có chế độ `--voice all` để tạo thử mọi giọng, mỗi giọng một thư mục.

Đo trên Colab A100: 10 chương (~78.000 ký tự) ra **70,7 phút audio trong 52 giây** (RTF ≈ 0,012).

---

## Yêu cầu

- GPU NVIDIA có CUDA (Colab T4/L4/A100 đều được). Không có GPU thì vẫn chạy được, nhưng chậm hơn khoảng 25 lần.
- Python 3.10 trở lên
- `ffmpeg` (Colab có sẵn)

---

## Hướng dẫn từng bước trên Google Colab

### Bước 1: Bật GPU và mount Google Drive

Vào menu **Runtime → Change runtime type → GPU**, rồi chạy cell sau:

```python
from google.colab import drive
drive.mount('/content/drive')
```

Thư mục truyện nên có dạng:

```
/content/drive/MyDrive/audio/1. Ngã dục phong thiên/
├── 0001.txt
├── 0002.txt
└── ...
```

### Bước 2: Cài thư viện

```bash
!git clone https://github.com/nvnhann/tts.git /content/TTS
%cd /content/TTS

# torch 2.8 + CUDA 12.8 (cài 3 gói cùng lúc để không lệch phiên bản torchvision)
!pip install -q torch==2.8.0 torchaudio==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu128
!pip install -q -r requirements.txt
```

> ⚠️ **Lưu ý trên Colab**
> - Lệnh trên sẽ hạ torch và transformers mặc định của Colab xuống bản 2.8 / 4.57.6 (bản VieNeu khuyên dùng). Khởi động lại runtime là Colab về như cũ.
> - Colab đặt sẵn `UV_SYSTEM_PYTHON=true`, nên `uv venv` + `uv pip install` vẫn cài vào Python hệ thống chứ không vào venv.
> - Nếu gặp lỗi `operator torchvision::nms does not exist` hoặc `Could not import module 'PreTrainedModel'`, nghĩa là torchvision không khớp với torch. Cài lại `torchvision==0.23.0` như ở trên.

### Bước 3: Kiểm tra nhanh

```bash
!python -c "from vieneu import Vieneu; v=Vieneu(); v.save(v.infer('Xin chào, đây là thử nghiệm.', voice='Hải Đăng'), 'test.wav')"
```

Lần chạy đầu sẽ tải model từ Hugging Face (khoảng 1–2 phút). Nghe `test.wav` để kiểm tra.

### Bước 4: Chạy thử 10 chương đầu

```bash
!python run_vieneu.py --n 10 --out output
```

Kết quả nằm ở `output/0001.mp3` … `output/0010.mp3`, kèm log thời gian của từng chương:

```
[Hải Đăng] 0001.txt: 10813 ký tự -> 9.7 phút audio, 9.0s, RTF 0.015
```

### Bước 5 (tuỳ chọn): Nghe thử để chọn giọng

```bash
!python run_vieneu.py --n 1 --voice all --out voices
```

Mỗi giọng có một thư mục `voices/<tên giọng>/`. Với `--n 1` thì mỗi giọng chỉ đọc chương đầu, khoảng 10 giây/giọng.

### Bước 6: Chạy cả bộ và lưu thẳng vào Drive

```bash
!python run_vieneu.py --n 100000 --voice "Hải Đăng" \
  --src "/content/drive/MyDrive/audio/1. Ngã dục phong thiên" \
  --out "/content/drive/MyDrive/audio/1. Ngã dục phong thiên - Hải Đăng"
```

1000 chương mất khoảng 2,5 giờ trên A100 (tính cả bước chuyển mp3) và ra khoảng 6–7 GB. Nếu Colab ngắt giữa chừng, làm lại từ Bước 1, 2 rồi chạy lại đúng lệnh này: các chương đã xong sẽ được bỏ qua.

---

## Tham số `run_vieneu.py`

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `--src` | `/content/drive/MyDrive/audio/1. Ngã dục phong thiên` | Thư mục chứa các file `.txt` (xử lý theo thứ tự tên file) |
| `--out` | `output` | Thư mục lưu `.mp3` |
| `--n` | `10` | Số file `.txt` đầu tiên cần xử lý |
| `--voice` | `Hải Đăng` | Tên giọng, hoặc `all` để chạy mọi giọng |

Audio được xuất ra mp3 128 kbps, 48 kHz.

## Danh sách giọng có sẵn

⭐ = giọng được nhà phát triển VieNeu chọn.

| Giọng | Giới tính · Vùng | Phong cách |
|---|---|---|
| ⭐ Adam bựa | Nam · Bắc | tự nhiên |
| ⭐ Trúc Ly | Nữ · Bắc | tự nhiên |
| ⭐ Thiện Minh | Nam · Bắc | kể chuyện |
| ⭐ Mai Anh | Nữ · Bắc | tin tức |
| ⭐ **Hải Đăng** (mặc định) | Nam · Bắc | tự nhiên |
| ⭐ Thùy Dung | Nữ · Nam | tin tức |
| ⭐ Thiền Tâm Đức | Nam · Bắc | kể chuyện |
| ⭐ Ngọc Huyền | Nữ · Bắc | tự nhiên |
| ⭐ Quang Sơn | Nam · Trung | tự nhiên |
| ⭐ Ngọc Trân | Nữ · Trung | tự nhiên |
| Minh Đức | Nam · Bắc | tin tức |
| Phạm Tuyên | Nam · Bắc | tự nhiên |
| Thái Sơn | Nam · Nam | kể chuyện |
| Xuân Vĩnh | Nam · Bắc | tự nhiên |
| Thanh Bình | Nam · Bắc | kể chuyện |
| Ngọc Linh | Nữ · Bắc | kể chuyện |
| Đoan Trang | Nữ · Bắc | tự nhiên |
| Thục Đoan | Nữ · Nam | kể chuyện |
| Minh Triết | Nam · Nam | tin tức |
| Mỹ Duyên | Nữ · Nam | đọc truyện |
| Quỳnh Anh | Nữ · Bắc | đọc truyện |
| Đức Trí | Nam · Nam | đọc truyện |
| Kim Thanh | Nữ · Nam | đọc truyện |
| Adam | Nam · Nam | tự nhiên |
| Quốc Tuấn | Nam · Bắc | tự nhiên |

## Chạy trên máy cá nhân (Linux, có GPU)

```bash
git clone https://github.com/nvnhann/tts.git && cd tts
python -m venv .venv && source .venv/bin/activate
pip install torch==2.8.0 torchaudio==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
sudo apt install -y ffmpeg
python run_vieneu.py --src /duong/dan/truyen --out output --n 10
```

## Ghi chú

- VieNeu-TTS tự chia văn bản dài thành các đoạn khoảng 256 ký tự và gộp batch trên GPU, nên có thể đưa cả chương vào một lần.
- Theo mặc định, VieNeu chèn watermark vào audio (`apply_watermark=True`).
- Giấy phép model: xem [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) và [model card trên Hugging Face](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo).
