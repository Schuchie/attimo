from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for
import os


class UiProvider:
    def __init__(self,  root_dir: Path = None , config_provider=None, image_provider=None):
        self.config_provider = config_provider
        self.image_provider = image_provider

        self.app = Flask(__name__)
         # Set folders via config
        self.app.config.update({
            "TEMPLATES_AUTO_RELOAD": True,
            "TEMPLATE_FOLDER": root_dir / "resource" / "templates",
            "STATIC_FOLDER": root_dir / "static",
        })

        # Set template/static folders directly
        self.app.template_folder = self.app.config["TEMPLATE_FOLDER"]
        self.app.static_folder = self.app.config["STATIC_FOLDER"]

        self.setup_routes()

    def setup_routes(self):
        
        @self.app.route('/')
        def index():
            images = self.image_provider.get_images()
            images = sorted(images, reverse=True)
            return render_template('index.html', images=images)

        @self.app.route('/upload', methods=['POST'])
        def upload():
            if 'images' not in request.files:
                return redirect(url_for('index'))

            files = request.files.getlist('images')
            for file in files:
                if file and file.filename != '':
                    self.image_provider.save_image(file)

            return redirect(url_for('index'))

        @self.app.route('/delete/<filename>', methods=['POST'])
        def delete(filename):
            if filename:
                self.image_provider.delete_image(filename)
                

            return redirect(url_for('index'))

    def run(self):
        print("[UiProvider] Starting UI provider...")
        self.app.run(host=self.config_provider.get('web.host', '0.0.0.0'), port=self.config_provider.get("web.port", 8080), debug=True)
