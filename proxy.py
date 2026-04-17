#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的HTTP代理服务器
将 /api/* 请求转发到 http://localhost:5001/api/*
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import json

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            self._proxy_request('GET')
        else:
            self._serve_static()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self._proxy_request('POST')
        else:
            self._serve_static()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _proxy_request(self, method):
        try:
            # 构建目标URL
            target_url = f'http://localhost:5001{self.path}'
            
            # 处理请求头
            headers = {}
            for key, value in self.headers.items():
                if key != 'Host':
                    headers[key] = value
            
            # 处理POST数据
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
            else:
                post_data = None
            
            # 创建请求
            req = urllib.request.Request(target_url, data=post_data, headers=headers, method=method)
            
            # 发送请求
            with urllib.request.urlopen(req) as response:
                # 获取响应
                status = response.status
                response_headers = dict(response.getheaders())
                response_data = response.read()
            
            # 发送响应
            self.send_response(status)
            for key, value in response_headers.items():
                if key.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                    self.send_header(key, value)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_data)
            
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_data = json.dumps({"error": str(e)}).encode()
            self.wfile.write(error_data)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_data = json.dumps({"error": f"代理错误: {str(e)}"}).encode()
            self.wfile.write(error_data)
    
    def _serve_static(self):
        try:
            # 移除前导斜杠
            file_path = self.path[1:] if self.path.startswith('/') else self.path
            
            # 默认文件
            if file_path == '':
                file_path = 'index.html'
            
            # 构建完整路径
            full_path = f'/workspace/{file_path}'
            
            # 读取文件
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # 确定内容类型
            if file_path.endswith('.html'):
                content_type = 'text/html'
            elif file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            else:
                content_type = 'application/octet-stream'
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            
        except FileNotFoundError:
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>404 Not Found</h1></body></html>')
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(f'<html><body><h1>500 Internal Server Error</h1><p>{str(e)}</p></body></html>'.encode())

def run_proxy(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProxyHandler)
    print(f"代理服务器启动在 http://localhost:{port}")
    print(f"将 /api/* 请求转发到 http://localhost:5001/api/*")
    print("按 Ctrl+C 停止服务")
    httpd.serve_forever()

if __name__ == '__main__':
    run_proxy()
