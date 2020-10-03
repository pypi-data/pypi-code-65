import os
import socket
import webbrowser
from functools import cached_property

from flask import Flask, jsonify, send_file, render_template, redirect
import glob
from .renderer import MarkdownRenderer


class Server(object):
    app = Flask(__name__)

    def __init__(self, path: str):
        self.base_path = path
        self.static_path = os.path.join(os.path.dirname(__file__), 'static')
        self.start_app()
        self.renderer = MarkdownRenderer()

    def start_app(self):
        app = self.app

        @app.route('/')
        def home():
            return redirect('/README.md')

        @app.route('/<path:path>')
        def markdown(path: str):
            path = os.path.join(self.base_path, path)
            path = os.path.join(self.base_path, path)
            if os.path.isdir(path):
                path = os.path.join(path, 'README.md')
            if not os.path.exists(path):
                return self.renderer.render('# 文件不存在')
            if path.endswith('.md'):
                with open(path, mode='r', encoding='utf-8') as f:
                    return render_template(
                        'content.html',
                        title=os.path.split(path)[1],
                        content=self.renderer.render(f.read()),
                        file_tree=self.file_tree,
                    )
            return send_file(path)

        @app.route('/<path:path>')
        def static_file(path):
            return app.send_static_file(path)

    @cached_property
    def port(self):
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    @cached_property
    def file_tree(self):

        def get_file_tree(directory_path):
            files = glob.glob(os.path.join(directory_path, '*'))
            directory_info = []
            for file in files:
                if os.path.isdir(file):
                    directory_info.append(
                        {
                            'is_directory': True,
                            'text': os.path.split(file)[1],
                            'url': '/' + os.path.relpath(file, self.base_path) + '/',
                            'children': get_file_tree(file)
                        })
                elif os.path.isfile(file) and os.path.splitext(file)[1] == '.md':
                    directory_info.append({
                        'text': os.path.splitext(os.path.split(file)[1])[0],
                        'url': '/' + os.path.relpath(file, self.base_path),
                    })
            return directory_info

        return get_file_tree(self.base_path)

    def show(self, path):
        webbrowser.open(os.path.join(self.base_path, path))

    def run(self):
        self.app.run(port=self.port)
