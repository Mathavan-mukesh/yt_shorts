import streamlit as st
import requests
import json
import os
import pathlib

# ✅ Streamlit page config
st.set_page_config(page_title="Tamil Shorts Generator", layout="centered")
st.title("🎬 Tamil YouTube Shorts Extractor")

# ✅ Select source
option = st.radio("Choose Video Source:", ["📺 YouTube URL", "📁 Upload Local Video"])

# ✅ Backend API host
api_host = "http://127.0.0.1:8000"

# ✅ Process YouTube video
if option == "📺 YouTube URL":
    youtube_url = st.text_input("Enter YouTube Video URL")

    if st.button("🚀 Process YouTube Video"):
        if not youtube_url.strip():
            st.warning("Please enter a valid YouTube URL")
        else:
            with st.spinner("Processing..."):
                try:
                    res = requests.post(f"{api_host}/process/", json={"youtube_url": youtube_url})
                    data = res.json()
                    if res.status_code == 200:
                        st.success(data["status"])
                        st.json(data)
                    else:
                        st.error(data["detail"])
                except Exception as e:
                    st.error(f"❌ {e}")

# ✅ Process local video
elif option == "📁 Upload Local Video":
    uploaded_file = st.file_uploader("Upload MP4 video", type=["mp4"])

    if uploaded_file and st.button("🚀 Process Local Video"):
        with st.spinner("Processing..."):
            try:
                res = requests.post(
                    f"{api_host}/process_local/",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "video/mp4")}
                )
                data = res.json()
                if res.status_code == 200:
                    st.success(data["status"])
                    st.json(data)
                else:
                    st.error(data["detail"])
            except Exception as e:
                st.error(f"❌ {e}")

# ✅ Display Extracted Shorts
if os.path.exists("youtube_shorts.json"):
    st.header("🎞️ Extracted Shorts")
    with open("youtube_shorts.json", "r", encoding="utf-8") as f:
        shorts = json.load(f)

    for short in shorts:
        st.subheader(f"🎬 Short #{short['short_number']}")
        st.write(f"💬 {short['description']}")

        # ✅ Construct absolute path
        filename = short.get("filename", f"short_{short['short_number']}.mp4")
        video_path = pathlib.Path("shorts_output") / filename
        abs_path = video_path.resolve()

        if abs_path.exists():
            # ✅ Debug info


            # ✅ Read and display video
            with open(abs_path, "rb") as vid:
                video_bytes = vid.read()
                st.video(video_bytes)

                # ✅ Download button
                st.download_button(
                    label="⬇️ Download This Short",
                    data=video_bytes,
                    file_name=filename,
                    mime="video/mp4"
                )
        else:
            st.warning(f"⚠️ Video not found: {abs_path}")
