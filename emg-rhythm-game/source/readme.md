# MMC RHYTHM GAME
筋電図（EMG）を利用したリズムゲーム

Python・Pygame・Arduino・筋電センサを用いて開発したリズムゲームです。

プレイヤーは使用する筋肉を2か所選択し、筋肉を動かすことでゲームを操作します。

# フォルダ構成
```
practice_on_design_project_11/
├── source/
│   ├── scripts/
│   │   ├── MMC.py
│   │   └── Arduino.ino
│   ├── rsc/
│   │   ├── body.png
│   │   ├── left_arm.png
│   │   ├── right_arm.png
│   │   ├── left_chest.png
│   │   ├── right_chest.png
│   │   ├── takuma.png
│   │   ├── nakayama.png
│   │   ├── bgm.mp3
│   │   ├── Power.mp3
│   │   └── miss.mp3
│   └── readme.md
└── rsc/
```
# 開発概要
開発期間

8週間

開発人数

4人

開発目的

筋電図（EMG）をゲーム操作へ利用し、身体を使った新しいゲーム体験を実現することを目的として開発しました。

実際の筋活動を入力デバイスとして利用することで、リハビリやトレーニングへの応用可能性も意識しました。

# 担当箇所
担当

私は主にソフトウェア開発を担当しました。

具体的には

Python(Pygame)によるゲームプログラム作成
判定処理
スコア管理
ゲーム画面制御
キーボード版ゲームとEMG版ゲームの統合作業

一方で、

ノーツ画像制作
レイアウトデザイン
Arduinoとのシリアル通信
EMG回路の構築

については他メンバーが担当しました。

最後に全員で各機能を統合し、動作確認と調整を行いました。

# 工夫した点
① EMG入力をゲームへリアルタイム反映

Arduinoからシリアル通信で筋電値を取得し、一定以上の値を検知するとゲーム入力として扱う仕組みを実装しました。

② 誤入力防止

筋肉は一度力を入れると連続して高い値が取得されます。

そのため入力後にクールタイムを設け、同じ筋活動で複数回判定されないようにしました。

コード例

INPUT_COOLDOWN = 0.2
③ 判定アルゴリズム

ノーツ位置と判定ラインとの差を計算し、

PERFECT
GOOD
MISS

の3段階で判定しました。

diff = abs(self.y - self.hit_y)
④ ランダム生成

ノーツ出現間隔をランダムにし、

毎回違う譜面になるよう設計しました。

next_spawn = random.randint(
    SPAWN_MIN,
    SPAWN_MAX
)
⑤ モジュール化

ゲーム内を

Noteクラス
描画処理
筋肉選択画面
メインゲーム

に分けて保守しやすい構成にしました。

## 開発環境

- Windows 11
- Python 3.14.5
- pygame-ce 2.5.7
- pyserial
- Arduino Uno

## 使用機材

- Arduino Uno ×2
- 筋電センサ ×4
- PC


## 使用方法

1. プログラムを起動する。

2. 筋肉選択画面が表示されるので、使用する筋肉を2か所選択する。

3. Enterキーを押してゲームを開始する。

4. 画面上部から選択した筋肉に対応するノーツが落下してくる。

5. ノーツが判定位置に重なるタイミングで対応する筋肉を動かして入力する。

6. タイミングに応じてPERFECT、GOOD、MISSの判定が表示される。

7. PERFECTは300点、GOODは150点加算される。MISSの場合は150点減点される。

8. ノーツを取り逃した場合もMISSとなる。

9. ウィンドウを閉じるとゲームを終了できる

## ライブラリのインストール

以下のコマンドを実行する。

```bash
pip install pygame-ce
pip install pyserial
```

## 実行方法

Arduinoを接続した状態で以下を実行する。

```bash
python source\scripts\MMC.py
```

## 注意事項

Arduinoが接続されていない場合は実行できない。

また、以下のエラーが表示された場合はpyserialをインストールする。

```text
ModuleNotFoundError: No module named 'serial'
```

```bash
pip install pyserial
```
## Arduinoと筋電図の接続方法
Arduino.inoを書き込み、シリアルモニタを使用して筋電値が取得できていることを確認する。

COM5は腕、COM4は胸で筋電図を確認するため書き込みを行う。

胸用Arduinoには左胸と右胸の筋電センサを接続し、腕用Arduinoには左腕と右腕の筋電センサを接続する。

筋電センサから取得した値はシリアル通信によってPCへ送信される。

プログラム実行前にArduinoをPCへ接続し、デバイスマネージャーでCOM番号を確認する。

COM番号が異なる場合は、MMC.py内の設定を変更する必要がある。

コード内では以下の設定を使用している。

```python
ser_arm = serial.Serial("COM5", 115200)
ser_chest = serial.Serial("COM4", 115200)
```

使用する環境によってCOM番号は変更する。

使用した筋電センサ：MyoWare 2.0 Muscle Sensor

COM4側のArduinoで、

左胸EMG → A0

右胸EMG → A1

両センサの電源 → 3.3V

両センサのGND → GND


COM5側のArduinoで、

左腕EMG → A0

右腕EMG → A1

両センサの電源 → 3.3V

両センサのGND → GND



## 発表資料
以下のリンク
https://1drv.ms/p/c/37ee4362c21be96d/IQBNPGVv1CzQSrIzAfVlNoj_AdXEs8oxlRYjFByTYAf9_E4?e=qZz7I0
