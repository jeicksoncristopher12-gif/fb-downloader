from flask import Flask, request, jsonify, render_template_string
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All-in-One Downloader</title>
    <style>
        :root { --fb-blue: #1877f2; --fb-green: #42b72a; --yt-red: #ff0000; }
        body { 
            font-family: 'Segoe UI', sans-serif; margin: 0; height: 100vh;
            display: flex; justify-content: center; align-items: center;
            background: linear-gradient(-45deg, #141e30, #243b55, #000000);
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
        .btn-primary { background: #333; color: white; }
        .btn-video { background: var(--fb-blue); color: white; animation: pulse 2s infinite; }
        .btn-audio { background: #ff9800; color: white; }
        .btn-secondary { background: #e4e6eb; color: #333; font-size: 13px; margin-top: 5px; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(24, 119, 242, 0.5); } 70% { box-shadow: 0 0 0 10px rgba(24, 119, 242, 0); } 100% { box-shadow: 0 0 0 0 rgba(24, 119, 242, 0); } }
        #result { display: none; }
        .thumb { width: 100%; border-radius: 10px; margin-bottom: 10px; }
        .loader { display: none; margin: 15px 0; color: #333; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div id="search-section">
            <h1>Downloader Pro</h1>
            <p style="color: #666; font-size: 12px; margin-bottom: 20px;">YouTube, TikTok, FB & Música</p>
            <input type="text" id="videoUrl" placeholder="Pega el link aquí...">
            <button class="btn btn-primary" id="btnProcess" onclick="processVideo()">Analizar Enlace</button>
            <div class="loader" id="loader">⚡ Procesando...</div>
        </div>
        <div id="result">
            <img id="preview" class="thumb" src="">
            <h3 id="title" style="font-size: 14px; margin-bottom: 15px; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"></h3>
            
            <a id="downloadVideo" class="btn btn-video" href="" target="_blank">🎬 Descargar Video</a>
            <a id="downloadAudio" class="btn btn-audio" href="" target="_blank">🎵 Descargar Solo Audio</a>
            
            <button class="btn btn-secondary" onclick="goBack()">← Volver atrás</button>
        </div>
    </div>
    <script>
        async function processVideo() {
            const url = document.getElementById('videoUrl').value;
            if(!url) return alert("Pega un link");
            document.getElementById('btnProcess').style.display = 'none';
            document.getElementById('loader').style.display = 'block';
            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                const data = await response.json();
                document.getElementById('loader').style.display = 'none';
                if(data.error) { alert("Error al procesar"); resetUI(); }
                else {
                    document.getElementById('preview').src = data.thumbnail;
                    document.getElementById('title').innerText = data.title;
                    document.getElementById('downloadVideo').href = data.video_url;
                    document.getElementById('downloadAudio').href = data.audio_url;
                    document.getElementById('search-section').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                }
            } catch (e) { alert("Error fatal"); resetUI(); }
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
    video_url = data.get('url')
    if not video_url: return jsonify({"error": "No URL"}), 400

    try:
        # Buscamos por separado el mejor video y el mejor audio solo
        with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Formato de Video (con audio incluido)
            video_link = info.get('url') 
            
            # Formato de Audio Solo (buscamos el mejor audio disponible)
            formats = info.get('formats', [])
            audio_link = video_link # Default por si no hay
            for f in formats:
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    audio_link = f.get('url')
                    break

            return jsonify({
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail'),
                "video_url": video_link,
                "audio_url": audio_link
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
