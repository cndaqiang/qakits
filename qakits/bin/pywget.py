import argparse
import os
import sys
import time
import urllib.request

def format_size(size):
    """将字节大小格式化为KB、MB或GB"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 ** 3:
        return f"{size / 1024 ** 2:.2f} MB"
    else:
        return f"{size / 1024 ** 3:.2f} GB"

def download_file(url, output=None, resume=False):
    """
    下载文件并保存到本地。
    
    :param url: 文件的URL地址
    :param output: 输出文件名（可选）
    :param resume: 是否启用断点续传（可选）
    """
    try:
        # 解析文件名
        if not output:
            output = url.split("/")[-1]  # 默认使用URL中的文件名
            if not output:
                output = "downloaded_file"

        # 检查是否需要断点续传
        start_byte = 0
        if resume and os.path.exists(output):
            start_byte = os.path.getsize(output)
            print(f"检测到已存在的文件，将从字节 {start_byte} 开始续传...")

        # 设置请求头
        headers = {}
        if start_byte > 0:
            headers["Range"] = f"bytes={start_byte}-"

        # 创建请求对象
        req = urllib.request.Request(url, headers=headers)

        # 打开URL连接
        with urllib.request.urlopen(req) as response:
            # 检查服务器是否支持断点续传
            if start_byte > 0 and response.status != 206:  # HTTP状态码206表示部分内容
                print("服务器不支持断点续传，将重新下载整个文件...")
                start_byte = 0

            file_size = int(response.headers.get("Content-Length", 0))
            if start_byte > 0:
                file_size += start_byte  # 总大小为已下载部分 + 剩余部分

            print(f"正在下载: {url}")
            print(f"文件大小: {format_size(file_size)}")
            print(f"保存路径: {output}")

            # 打开文件以追加模式写入
            mode = "ab" if resume and start_byte > 0 else "wb"
            with open(output, mode) as f:
                start_time = time.time()
                downloaded = start_byte
                last_update_time = start_time  # 上次更新时间

                while True:
                    chunk = response.read(1024 * 8)  # 每次读取8KB
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    # 计算当前时间
                    current_time = time.time()

                    # 每隔0.5秒刷新一次进度条
                    if current_time - last_update_time >= 0.5:
                        # 计算进度、速度和预计完成时间
                        elapsed_time = current_time - start_time
                        speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                        remaining_bytes = file_size - downloaded
                        estimated_time = remaining_bytes / speed if speed > 0 else 0

                        # 格式化显示信息
                        progress = (downloaded / file_size) * 100 if file_size > 0 else 100
                        speed_mb = speed / 1024 ** 2  # 转换为MB/s
                        estimated_time_str = (
                            f"{int(estimated_time // 60)}分{int(estimated_time % 60):02d}秒"
                            if estimated_time > 60
                            else f"{int(estimated_time):02d}秒"
                        )

                        # 使用固定宽度格式化字符串，确保每行输出长度一致
                        progress_bar = (
                            f"\r进度: {progress:6.2f}% | 下载速度: {speed_mb:6.2f} MB/s | 预计剩余时间: {estimated_time_str}"
                        )
                        sys.stdout.write(progress_bar)
                        sys.stdout.flush()

                        # 更新上次刷新时间
                        last_update_time = current_time

        print("\n下载完成！")
    except Exception as e:
        print(f"\n下载失败: {e}")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="一个简单的wget实现")
    parser.add_argument("url", type=str, help="要下载的文件的URL地址")
    parser.add_argument("-o", "--output", type=str, help="输出文件名（可选）")
    parser.add_argument("-r", "--resume", action="store_true", help="启用断点续传")

    # 解析命令行参数
    args = parser.parse_args()

    # 调用下载函数
    download_file(args.url, args.output, args.resume)

if __name__ == "__main__":
    main()