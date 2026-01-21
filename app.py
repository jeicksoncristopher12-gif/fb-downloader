from flask import Flask, request, jsonify, render_template_string
import yt_dlp
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Downloader Pro - No Watermark</title>
    <style>
        :root { --fb-blue: #1877f2; --fb-green: #42b72a; --dark-bg: #0f172a; }
        body { 
            font-family: 'Segoe UI', sans-serif; margin: 0; height: 100vh;
            display: flex; justify-content: center; align-items: center;
            background: linear-gradient(-45deg, #0f172a, #1e293b, #334155);
            background-size: 400% 400%; animation: gradientBG 15s ease infinite;
            overflow: hidden;
        }
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .card { 
            background: rgba(255, 255, 255, 0.98); padding: 30px; border-radius: 20px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.5); width: 360px; text-align: center;
            z-index: 10;
        }
        h1 { color: #333; font-size: 24px; margin-bottom: 5px; font-weight: 800; }
        input { width: 90%; padding: 14px; border: 2px solid #eee; border-radius: 12px; margin-bottom: 20px; outline: none; font-size: 15px; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 15px; transition: 0.3s; margin-bottom: 10px; text-decoration: none; display: block; box-sizing: border-box; }
        .btn-primary { background: #000; color: white; }
        .btn-video { background: #fe2c55; color: white; animation: pulse 2s infinite; }
        .btn-audio { background: #25f4ee; color: #000; }
        .btn-secondary { background: #e4e6eb; color: #333; font-size: 13px; margin-top: 5px; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(254, 44, 85, 0.5); } 70% { box-shadow: 0 0 0 10px rgba(254, 44, 85, 0); } 100% { box-shadow: 0 0 0 0 rgba(254, 44, 85, 0); } }
        #result { display: none; }
        .thumb { width: 100%; border-radius: 10px; margin-bottom: 10px; border: 2px solid #f0f0f0; }
        .loader { display: none; margin: 15px 0; color: #333; font-weight: bold; }
        .tip { font-size: 10px; color: #888; margin-top: 10px; line-height: 1.2; }
    </style>
</head>
<body>
    <div class="card">
        <div id="search-section">
            <h1>Downloader Pro</h1>
            <p style="color: #666; font-size: 12px; margin-bottom: 20px;">TikTok Sin Marca, Shorts, Reels & FB</p>
            <input type="text" id="videoUrl" placeholder="Pega el link aquí...">
            <button class="btn btn-primary" id="btnProcess" onclick="processVideo()">Analizar Enlace</button>
            <div class="loader" id="loader">⚡ Procesando enlace...</div>
        </div>
        <div id="result">
            <img id="preview" class="thumb" src="">
            <h3 id="title" style="font-size: 14px; margin-bottom: 15px; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"></h3>
            <a id="downloadVideo" class="btn btn-video" href="" target="_blank">🎬 Descargar Video</a>
            <a id="downloadAudio" class="btn btn-audio" href="" target="_blank">🎵 Solo Audio</a>
            <button class="btn btn-secondary" onclick="goBack()">← Volver atrás</button>
            <p class="tip">Si abre el video sin descargar:<br>Mantén presionado y elige "Descargar video"</p>
        </div>
    </div>
    <script>
        async function processVideo() {
            const urlInput = document.getElementById('videoUrl').value;
            if(!urlInput) return alert("Pega un link válido");
            document.getElementById('btnProcess').style.display = 'none';
            document.getElementById('loader').style.display = 'block';
            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: urlInput })
                });
                const data = await response.json();
                document.getElementById('loader').style.display = 'none';
                if(data.error) { 
                    alert("Error: No se pudo obtener el video. Intenta con otro link."); 
                    resetUI(); 
                }
                else {
                    document.getElementById('preview').src = data.thumbnail;
                    document.getElementById('title').innerText = data.title;
                    document.getElementById('downloadVideo').href = data.video_url;
                    document.getElementById('downloadAudio').href = data.audio_url;
                    document.getElementById('search-section').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                }
            } catch (e) { alert("Error de conexión con el servidor"); resetUI(); }
        }
        function goBack() {
            document.getElementById('videoUrl').value = "";
            document.getElementById('result').style.display = 'none';
            document.getElementById('search-section').style.display = 'block';
            resetUI();
        }
        function resetUI() {
            document.getElementById('btnProcess').style.display = 'block';
            document.getElementById('loader').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url', '')
    
    # 1. Limpiar URL de YouTube Shorts y parámetros basura
    if "youtu" in url:
        url = re.sub(r'\?si=.*$', '', url)
        url = url.replace("shorts/", "watch?v=")

    # 2. Configuración Maestra para evitar Error 403
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 3. Lógica específica TikTok Sin Marca
            video_url = info.get('url')
            if 'tiktok.com' in url:
                for f in info.get('formats', []):
                    # El formato 'download_addr-0' suele ser el original sin marca
                    if f.get('format_id') == 'download_addr-0' or f.get('format_note') == 'Direct download':
                        video_url = f.get('url')
                        break

            # 4. Obtener Audio
            audio_url = video_url
            for f in reversed(info.get('formats', [])):
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    audio_url = f.get('url')
                    break

            return jsonify({
                "title": info.get('title', 'Video Download'),
                "thumbnail": info.get('thumbnail'),
                "video_url": video_url,
                "audio_url": audio_url
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()

