from flask import Flask, request, jsonify, render_template_string
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Video Downloader</title>
    <style>
        body { 
            font-family: 'Segoe UI', sans-serif; background: #f0f2f5; 
            display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; 
        }
        .card { 
            background: white; padding: 30px; border-radius: 12px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; 
        }
        h1 { color: #1877f2; font-size: 24px; margin-bottom: 20px; }
        input { 
            width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; 
            margin-bottom: 20px; box-sizing: border-box; outline: none;
        }
        button { 
            background: #1877f2; color: white; border: none; padding: 12px 20px; 
            border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%;
        }
        button:hover { background: #166fe5; }
        #result { margin-top: 20px; display: none; }
        .thumb { width: 100%; border-radius: 8px; margin-bottom: 10px; }
        .download-btn { 
            display: inline-block; background: #42b72a; color: white; 
            text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>FB Downloader</h1>
        <input type="text" id="videoUrl" placeholder="Pega el link de Facebook aquí...">
        <button onclick="downloadVideo()">Analizar Video</button>
        <div id="result">
            <img id="preview" class="thumb" src="">
            <p id="title" style="font-weight: bold;"></p>
            <a id="downloadBtn" class="download-btn" href="" target="_blank">Descargar Ahora</a>
        </div>
    </div>

    <script>
        async function downloadVideo() {
            const url = document.getElementById('videoUrl').value;
            if (!url) return alert("Pega un link");
            
            const response = await fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                document.getElementById('preview').src = data.thumbnail;
                document.getElementById('title').innerText = data.title;
                document.getElementById('downloadBtn').href = data.url;
                document.getElementById('result').style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')
    
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
