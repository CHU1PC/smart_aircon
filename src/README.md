# Smart Aircon — 顔認証によるスマートエアコン制御 (演習7)

Raspberry Pi 5 上で、ボタン押下をトリガに顔認証を行い、登録者なら室温に応じて
SwitchBot 経由でエアコンを制御するシステム。開発は Mac、実行は Raspberry Pi 5。

## 動作フロー

1. ボタンが押される
2. 顔認証を行うためにカメラで撮影する(5秒間)
3. 顔認証を行う
4. 顔認証が成功した場合, 室温を取得する
5. 室温が設定温度より高い場合, SwitchBotのAPIを呼び出す
6. 冷房をONにする

## 構成

- 顔検出: OpenCV YuNet (`cv2.FaceDetectorYN`)
- 顔認証: ArcFace / MobileFaceNet 埋め込み + cosine 類似度しきい値 (onnxruntime)
- GPIO: gpiozero + lgpio (Pi5)
- 温湿度: DHT11
- エアコン: SwitchBot Cloud API v1.1
- パッケージ管理: uv

## セットアップ

### 1. 取得

```bash
git clone https://github.com/CHU1PC/Adjusting_AirCondition.git
cd Adjusting_AirCondition/src
```

### 2. 依存インストール

```bash
uv sync --extra pi   # Raspberry Pi (本番)
uv sync              # Mac (開発のみ)
```

`.venv` は各マシンで生成されるため、他マシンから持ち込まない。

### 3. モデル取得 (git 管理外・初回に各マシンで DL)

```bash
mkdir -p models
# 顔検出 YuNet (MIT)
curl -sL -o models/face_detection_yunet_2023mar.onnx \
  https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
# 顔認証 ArcFace/MobileFaceNet (InsightFace buffalo_s / 非商用研究のみ)
curl -sL -o models/w600k_mbf.onnx \
  https://huggingface.co/deepghs/insightface/resolve/main/buffalo_s/w600k_mbf.onnx
```

### 4. SwitchBot 認証情報

```bash
cp .env.example .env   # Token / Secret / DeviceId を記入 (git 管理外)
```

### 5. 配線

- プッシュボタン: GPIO25 (内部プルダウン, 押下で 3.3V)
- LED / DHT11 / SwitchBot は実装に合わせて追記

## 実行

```bash
uv run main.py                # ボタン待受 (押下で1サイクル)
uv run recognition/detect.py  # 検出+整列の単体確認 (aligned.jpg を出力)
```

## メモ

- git 管理外: モデル (`models/*.onnx`) / `.env` / `captures/` / `dataset/` / 登録 gallery
- ArcFace モデル (`w600k_mbf.onnx`) は非商用研究ライセンス
