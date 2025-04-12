from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import os


class UiProvider:
    def __init__(self,  root_dir: Path = None , config_provider=None):
        self.config_provider = config_provider
        self.app = Flask(__name__)
         # Set folders via config
        self.app.config.update({
            "TEMPLATES_AUTO_RELOAD": True,
            "TEMPLATE_FOLDER": root_dir / "resource" / "templates",
            "STATIC_FOLDER": root_dir / "static",
            "UPLOAD_FOLDER": root_dir / "static" / "uploads",
        })

        # Set template/static folders directly
        self.app.template_folder = self.app.config["TEMPLATE_FOLDER"]
        self.app.static_folder = self.app.config["STATIC_FOLDER"]

        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            images = os.listdir(os.path.join(self.app.config["UPLOAD_FOLDER"], 'preview'))
            images = sorted(images, reverse=True)
            return render_template('index.html', images=images)

        @self.app.route('/upload', methods=['POST'])
        def upload():
            if 'images' not in request.files:
                return redirect(url_for('index'))

            files = request.files.getlist('images')
            for file in files:
                if file and file.filename != '':
                    filename = file.filename
                    filepath = os.path.join(self.app.config['UPLOAD_FOLDER'],'raw', filename)
                    file.save(filepath)

                    # Create a low-res preview
                    preview_folder = os.path.join(self.app.config['UPLOAD_FOLDER'], 'preview')
                    os.makedirs(preview_folder, exist_ok=True)
                    preview_path = os.path.join(preview_folder, filename)

                    try:
                        with Image.open(filepath) as img:
                            img.thumbnail((600, 800))  # Adjust max preview size
                            img.save(preview_path, optimize=True, quality=70)
                    except Exception as e:
                        print(f"⚠️ Failed to create preview for {filename}: {e}")

            return redirect(url_for('index'))

        @self.app.route('/delete/<filename>', methods=['POST'])
        def delete(filename):
            filepath = os.path.join(self.app.config["UPLOAD_FOLDER"],'raw', filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            filepath = os.path.join(self.app.config["UPLOAD_FOLDER"],'preview', filename)
            if os.path.exists(filepath):
                os.remove(filepath)

            return redirect(url_for('index'))

    def run(self):
        print("[UiProvider] Starting UI provider...")
        self.app.run(host=self.config_provider.get('web.host', '0.0.0.0'), port=self.config_provider.get("web.port", 8080), debug=True)
