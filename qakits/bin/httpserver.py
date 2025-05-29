import argparse
import os
import socket
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import TCPServer

def get_all_local_ips():
    """获取本机的所有局域网IP地址"""
    local_ips = []
    try:
        # 获取主机名
        hostname = socket.gethostname()
        # 获取所有与主机名关联的IP地址
        addresses = socket.gethostbyname_ex(hostname)[-1]
        for ip in addresses:
            if not ip.startswith("127.") and "." in ip:  # 过滤掉回环地址和非IPv4地址
                local_ips.append(ip)
    except Exception as e:
        print(f"尝试通过主机名获取IP地址时出错: {e}")

    # 如果通过主机名无法获取IP地址，则尝试直接扫描所有网络接口
    if not local_ips:
        try:
            # 创建一个UDP套接字以检测所有可用的网络接口
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # 尝试连接到公共DNS服务器（不实际发送数据）
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                if not ip.startswith("127.") and "." in ip:
                    local_ips.append(ip)
        except Exception as e:
            print(f"尝试通过UDP套接字获取IP地址时出错: {e}")

    return list(set(local_ips))  # 去重

class RangeRequestHandler(SimpleHTTPRequestHandler):
    """支持断点续传的HTTP请求处理器"""

    def do_GET(self):
        # 检查是否包含Range头字段
        range_header = self.headers.get("Range")
        if range_header:
            self.handle_range_request(range_header)
        else:
            # 如果没有Range头字段，调用父类的do_GET方法
            super().do_GET()

    def handle_range_request(self, range_header):
        """处理带有Range头字段的请求"""
        try:
            # 解析文件路径
            path = self.translate_path(self.path)
            if not os.path.isfile(path):
                self.send_error(404, "File not found")
                return

            # 获取文件大小
            file_size = os.path.getsize(path)

            # 解析Range头字段，格式如"bytes=0-1023"
            start, end = self.parse_range_header(range_header, file_size)
            if start is None or end is None:
                self.send_error(400, "Invalid Range header")
                return

            # 打开文件并读取指定范围的内容
            with open(path, "rb") as f:
                f.seek(start)
                data = f.read(end - start + 1)

            # 构造响应头
            self.send_response(206)  # 部分内容响应
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            # 发送数据
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def parse_range_header(self, range_header, file_size):
        """解析Range头字段"""
        try:
            # 提取范围值，例如"bytes=0-1023"
            range_value = range_header.strip().split("=")[1]
            start, end = range_value.split("-")
            start = int(start) if start else 0
            end = int(end) if end else file_size - 1
            # 确保范围有效
            if start < 0 or end >= file_size or start > end:
                return None, None
            return start, end
        except Exception:
            return None, None

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="启动一个支持断点续传的HTTP文件分享服务")
    parser.add_argument("-p", "--port", type=int, default=8000, help="指定HTTP服务的端口号，默认为8000")
    
    # 解析命令行参数
    args = parser.parse_args()
    port = args.port

    # 检查端口号是否有效
    if not (1 <= port <= 65535):
        print("错误：端口号必须在1到65535之间")
        return

    # 获取当前工作目录
    current_directory = os.getcwd()
    os.chdir(current_directory)  # 确保服务器运行在当前目录

    # 获取所有局域网IP地址
    local_ips = get_all_local_ips()

    # 启动HTTP服务器
    with HTTPServer(("", port), RangeRequestHandler) as httpd:
        print(f"正在共享目录: {current_directory}")
        print(f"HTTP服务已启动，访问地址:")
        
        # 打印所有可用的局域网IP地址
        if local_ips:
            print("  局域网地址:")
            for ip in local_ips:
                print(f"    http://{ip}:{port}")
        else:
            print("  无法获取局域网IP地址，请检查网络配置。")

        # 打印本机地址
        print(f"  本机地址: http://localhost:{port}")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已停止")

if __name__ == "__main__":
    main()
