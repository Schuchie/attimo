from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime


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
            sort_by = request.args.get("sort", "added")  # "created" or "added"

            image_meta_dict = self.image_provider.get_images()  # {uuid: meta}
            image_items = list(image_meta_dict.items())  # [(filename, metadata), ...]

            def get_sort_value(item):
                attr = item[1].get("attribute", {})
                dt_str = attr.get("created_datetime") if sort_by == "created" else attr.get("added_datetime")
                try:
                    return datetime.fromisoformat(dt_str)
                except:
                    return datetime.min

            # Sort images by selected field
            image_items.sort(key=get_sort_value, reverse=True)

            # Keep only filenames for rendering
            sorted_filenames = [filename for filename, _ in image_items]

            return render_template('index.html', images=sorted_filenames, sort_by=sort_by)

        @self.app.route('/upload', methods=['POST'])
        def upload():
            sort_by = request.args.get("sort", "added")
            if 'images' not in request.files:
                return redirect(url_for('index'))

            files = request.files.getlist('images')
            for file in files:
                if file and file.filename != '':
                    self.image_provider.save_image(file)

            return redirect(url_for('index', sort=sort_by))

        @self.app.route('/delete/<filename>', methods=['POST'])
        def delete(filename):
            sort_by = request.args.get("sort", "added")
            if filename:
                self.image_provider.delete_image(filename)
                

            return redirect(url_for('index', sort=sort_by))

    def run(self):
        print("[UiProvider] Starting UI provider...")
        self.app.run(host=self.config_provider.get('web.host', '0.0.0.0'), port=self.config_provider.get("web.port", 8080), debug=True)
