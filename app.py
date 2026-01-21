from flask import Flask, request, jsonify, render_template_string
import yt_dlp

app = Flask(__name__)

# El HTML se guarda en una variable de Python
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FB Video Downloader - Premium</title>
    <style>
        :root { --fb-blue: #1877f2; --fb-green: #42b72a; --bg-dark: #141e30; }
        body { 
            font-family: 'Segoe UI', sans-serif; margin: 0; height: 100vh;
            display: flex; justify-content: center; align-items: center;
            background: linear-gradient(-45deg, #1877f2, #2b32b2, #141e30, #243b55);
            background-size: 400% 400%; animation: gradientBG 15s ease infinite;
            overflow: hidden;
        }
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .card { 
            background: rgba(255, 255, 255, 0.95); padding: 35px; border-radius: 20px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.3); width: 380px; text-align: center;
            backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.3); z-index: 10;
        }
        h1 { color: var(--fb-blue); font-size: 26px; margin-bottom: 25px; font-weight: 800; letter-spacing: -1px; }
        input { width: 90%; padding: 14px; border: 2px solid #eee; border-radius: 12px; margin-bottom: 20px; outline: none; transition: 0.3s; font-size: 15px; }
        input:focus { border-color: var(--fb-blue); }
        .btn { width: 100%; padding: 14px; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; font-size: 16px; transition: all 0.3s ease; position: relative; overflow: hidden; }
        .btn-primary { background: var(--fb-blue); color: white; box-shadow: 0 4px 15px rgba(24, 119, 242, 0.4); }
        .btn-success { background: var(--fb-green); color: white; text-decoration: none; display: block; margin-top: 15px; animation: pulse 2s infinite; }
        .btn-secondary { background: #e4e6eb; color: #050505; margin-top: 10px; font-size: 14px; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(66, 183, 42, 0.7); } 70% { box-shadow: 0 0 0 15px rgba(66, 183, 42, 0); } 100% { box-shadow: 0 0 0 0 rgba(66, 183, 42, 0); } }
        #result { display: none; animation: fadeIn 0.6s cubic-bezier(0.23, 1, 0.32, 1); }
        .thumb { width: 100%; border-radius: 12px; margin: 15px 0; border: 3px solid #eee; }
        .loader { display: none; margin: 15px 0; color: var(--fb-blue); font-weight: bold; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
    </style>
</head>
<body>
    <div class="card">
        <div id="search-section">
            <h1>FB Downloader</h1>
            <input type="text" id="videoUrl" placeholder="Pega el link aquí...">
            <button class="btn btn-primary" id="btnProcess" onclick="processVideo()">Obtener Video</button>
            <div class="loader" id="loader">🚀 Buscando video...</div>
        </div>
        <div id="result">
            <img id="preview" class="thumb" src="">
            <h3 id="title" style="font-size: 15px; margin: 10px 0; color: #333;"></h3>
            <a id="downloadBtn" class="btn btn-success" href="" target="_blank">⬇️ Descargar Ahora</a>
            <button class="btn btn-secondary" onclick="goBack()">← Descargar otro más</button>
        </div>
    </div>
    <script>
        async function processVideo() {
            const url = document.getElementById('videoUrl').value;
            if(!url) return alert("Por favor, pega un link válido");
            document.getElementById('btnProcess').style.display = 'none';
            document.getElementById('loader').style.display = 'block';
            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                const data = await response.json();
                if(data.error) { alert("Error: " + data.error); resetUI(); }
                else {
                    document.getElementById('preview').src = data.thumbnail;
                    document.getElementById('title').innerText = data.title;
                    document.getElementById('downloadBtn').href = data.url;
                    document.getElementById('search-section').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                }
            } catch (e) { alert("Error de conexión."); resetUI(); }
        }
        function goBack() {
            document.getElementById('videoUrl').value = "";
            resetUI();
            document.getElementById('result').style.display = 'none';
            document.getElementById('search-section').style.display = 'block';
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
    if not video_url:
        return jsonify({"error": "URL no proporcionada"}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                "title": info.get('title', 'Video de Facebook'),
                "url": info.get('url'),
                "thumbnail": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
