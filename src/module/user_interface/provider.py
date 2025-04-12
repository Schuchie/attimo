from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for
import os


class UiProvider:
    def __init__(self,  root_dir: Path = None , config_provider=None):
        self.config_provider = config_provider
        self.app = Flask(__name__)
        self.app.config['TEMPLATES_AUTO_RELOAD'] = True
        self.app.config['TEMPLATE_FOLDER'] = root_dir  / "resource" / "templates"  #os.path.join(os.path.dirname(__file__), 'templates')
        self.app.config['STATIC_FOLDER'] = root_dir / "static"
        self.app.config['UPLOAD_FOLDER'] = root_dir / "static" / "uploads"
        self.app.template_folder = self.app.config['TEMPLATE_FOLDER']
        self.app.static_folder = self.app.config['STATIC_FOLDER']
        self.upload_folder = self.app.config['UPLOAD_FOLDER']

        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            images = os.listdir(self.upload_folder)
            images = sorted(images, reverse=True)
            return render_template('index.html', images=images)

        @self.app.route('/upload', methods=['POST'])
        def upload():
            file = request.files.get('image')
            if file and file.filename != '':
                filepath = os.path.join(self.upload_folder, file.filename)
                file.save(filepath)
            return redirect(url_for('index'))

        @self.app.route('/delete/<filename>', methods=['POST'])
        def delete(filename):
            filepath = os.path.join(self.upload_folder, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for('index'))

    def run(self):
        print("[UiProvider] Starting UI provider...")
        self.app.run(host=self.config_provider.get('web.host', '0.0.0.0'), port=self.config_provider.get("web.port", 8080), debug=True)
