import streamlit as st
import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# OpenAIクライアント
client = OpenAI()

# ディレクトリ設定
AUDIO_DIR = "audio"
HISTORY_FILE = "history.json"

os.makedirs(AUDIO_DIR, exist_ok=True)

# 履歴ファイル初期化
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# 履歴読み込み
def load_history():
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 履歴保存
def save_history(item):
    history = load_history()
    history.insert(0, item)  # 新しい順
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


st.title("Speech05 - 読み上げアプリ（完成版）")

# 入力
input_text = st.text_area("読み上げるテキスト（改行で複数OK）")

# 音声選択
voice = st.selectbox(
    "音声を選択",
    ["alloy", "nova", "shimmer", "echo", "onyx"]
)

# 実行
if st.button("読み上げ実行"):
    if input_text.strip() == "":
        st.warning("テキストを入力してください")
    else:
        lines = input_text.split("\n")

        for line in lines:
            text = line.strip()
            if text == "":
                continue

            try:
                # ファイル名
                filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".wav"
                filepath = os.path.join(AUDIO_DIR, filename)

                # 音声生成
                with client.audio.speech.with_streaming_response.create(
                    model="gpt-4o-mini-tts",
                    voice=voice,
                    input=text
                ) as response:
                    response.stream_to_file(filepath)

                # 履歴保存
                save_history({
                    "text": text,
                    "voice": voice,
                    "file": filepath,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                st.success(f"生成完了: {text}")

                # 再生
                st.audio(filepath)

                # ダウンロード
                with open(filepath, "rb") as f:
                    st.download_button(
                        label=f"ダウンロード ({text[:10]}...)",
                        data=f,
                        file_name=filename,
                        mime="audio/wav",
                        key=filename
                    )

            except Exception as e:
                st.error(f"エラー: {e}")

# -----------------------------
# 履歴表示
# -----------------------------
st.markdown("---")
st.subheader("履歴")

history = load_history()

if len(history) == 0:
    st.info("履歴はまだありません")
else:
    for i, item in enumerate(history):
        st.markdown(f"**{item['created_at']}**")
        st.write(f"音声: {item['voice']}")
        st.write(item["text"])

        if os.path.exists(item["file"]):
            st.audio(item["file"])

            with open(item["file"], "rb") as f:
                st.download_button(
                    label="ダウンロード",
                    data=f,
                    file_name=os.path.basename(item["file"]),
                    mime="audio/wav",
                    key=f"history_{i}"
                )

        st.markdown("---")