from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from collections import defaultdict


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
            sort_by = request.args.get("sort", "created")
            image_meta = self.image_provider.get_images()

            grouped_by_year = defaultdict(list)

            for filename, meta in image_meta.items():
                attr = meta.get("attribute", {})
                dt_str = attr.get("created_datetime") if sort_by == "created" else attr.get("added_datetime")

                try:
                    dt = datetime.fromisoformat(dt_str)
                    year = dt.year
                except:
                    year = "Unknown"

                grouped_by_year[year].append((dt_str, filename))

            # Sort years descending, and each image list by datetime
            grouped_sorted = dict()
            for year in sorted(grouped_by_year.keys(), reverse=True):
                grouped_sorted[year] = sorted(grouped_by_year[year], key=lambda x: x[0], reverse=True)

            return render_template("index.html", groups=grouped_sorted, sort_by=sort_by)

        @self.app.route('/upload', methods=['POST'])
        def upload():
            sort_by = request.args.get("sort", "created")
            if 'images' not in request.files:
                return redirect(url_for('index'))

            files = request.files.getlist('images')
            for file in files:
                if file and file.filename != '':
                    self.image_provider.save_image(file)

            return redirect(url_for('index', sort=sort_by))

        @self.app.route('/delete/<filename>', methods=['POST'])
        def delete(filename):
            sort_by = request.args.get("sort", "created")
            if filename:
                self.image_provider.delete_image(filename)
                

            return redirect(url_for('index', sort=sort_by))

    def run(self):
        print("[UiProvider] Starting UI provider...")
        self.app.run(host=self.config_provider.get('web.host', '0.0.0.0'), port=self.config_provider.get("web.port", 8080), debug=True)
