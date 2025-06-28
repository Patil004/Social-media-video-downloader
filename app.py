from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp
import os
import threading
import time
from urllib.parse import urlparse

app = Flask(__name__)
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_platform_name(url):
    domain = urlparse(url).netloc.lower()
    if "youtube" in domain or "youtu.be" in domain:
        return "YouTube"
    elif "instagram" in domain:
        return "Instagram"
    elif "twitter" in domain or "x.com" in domain:
        return "Twitter"
    elif "facebook" in domain:
        return "Facebook"
    elif "tiktok" in domain:
        return "TikTok"
    else:
        return "Other"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processing', methods=['POST'])
def processing():
    url = request.form['url']
    quality = request.form['quality']
    ext = 'mp3' if quality == 'audio' else 'mp4'

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'format': 'bestaudio/best',
        'merge_output_format': ext,
        'quiet': True,
        'noplaylist': False,
    }

    if quality != 'audio':
        ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            entry = info['entries'][0] if 'entries' in info else info
            filename = ydl.prepare_filename(entry).replace('.webm', f'.{ext}').replace('.mkv', f'.{ext}')
            safe_name = os.path.basename(filename)
            return render_template('download.html', filename=safe_name)

    except Exception as e:
        return f"<h3>Error: {e}</h3><a href='/'>Back</a>"

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)

    def delete_file_delayed(path):
        time.sleep(10)  # wait 10 seconds to ensure download completes
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted {path}")

    if os.path.exists(file_path):
        threading.Thread(target=delete_file_delayed, args=(file_path,)).start()
        return send_file(file_path, as_attachment=True)
    else:
        return "<h3>File not found.</h3><a href='/'>Back</a>"

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} at {d['_speed_str']} ETA {d['_eta_str']}")
    elif d['status'] == 'finished':
        print("Download finished.")

if __name__ == '__main__':
    app.run(debug=True)
