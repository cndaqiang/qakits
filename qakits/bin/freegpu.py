import torch
import time
import os
from datetime import datetime
import argparse
import psutil
import subprocess  # 用于调用 nvidia-smi 获取显存信息

def get_nvidia_smi_memory():
    """调用 nvidia-smi 获取显存信息"""
    command = "nvidia-smi --query-gpu=index,memory.total,memory.used,memory.free --format=csv,noheader,nounits"
    result = subprocess.check_output(command, shell=True).decode('utf-8').strip().splitlines()
    
    # 返回一个字典，键为GPU索引，值为[total_memory, used_memory, free_memory]
    memory_info = {}
    for line in result:
        gpu_id, total, used, free = map(int, line.split(', '))
        memory_info[gpu_id] = {
            'total': total,
            'used': used,
            'free': free
        }
    return memory_info

def get_best_gpu(start_gpu=0, end_gpu=-1):
    """获取最佳的 GPU（基于空闲显存）"""
    free_memory = []
    memory_info = get_nvidia_smi_memory()  # 获取nvidia-smi的显存信息
    end_gpu = end_gpu if end_gpu > 0 else torch.cuda.device_count()

    output = f"{'GPU':<6} {'Total Memory (GB)':<22} {'Used Memory (GB)':<22} {'Free Memory (GB)':<22}\n"
    output += "="*80 + "\n"

    for i in range(start_gpu, end_gpu):
        # 使用 nvidia-smi 获取的显存数据
        total = memory_info.get(i, {}).get('total', 0) / 1024  # 转换为 GB
        used = memory_info.get(i, {}).get('used', 0) / 1024
        free = memory_info.get(i, {}).get('free', 0) / 1024

        output += f"{i:<6} {total:>22.2f} {used:>22.2f} {free:>22.2f}\n"

        free_memory.append((free, i))

    free_memory.sort(reverse=True, key=lambda x: x[0])
    best_gpu = free_memory[0][1]

    return output, best_gpu

def monitor_gpu_memory(start_gpu, end_gpu, flashinterval):
    previous_output = ""  # 用于存储上一次输出的内容

    while True:
        # 获取当前时间和显存信息
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output, best_gpu = get_best_gpu(start_gpu, end_gpu)

        # 获取CPU内存信息
        cpu_memory = psutil.virtual_memory()
        total_cpu_memory = cpu_memory.total / 1024**3  # 转换为GB
        used_cpu_memory = cpu_memory.used / 1024**3  # 转换为GB
        free_cpu_memory = cpu_memory.free / 1024**3  # 转换为GB

        # 拼接最终输出
        final_output = f"Timestamp: {timestamp}\n" + "="*80 + "\n" + output
        final_output += f"\nBest GPU for allocation: GPU {best_gpu} (based on free memory)\n\n"
        final_output += f"CPU Memory - Total: {total_cpu_memory:>6.2f} GB, Used: {used_cpu_memory:>6.2f} GB, Free: {free_cpu_memory:>6.2f} GB\n"

        # 判断是否有变化，避免重复刷新
        if final_output != previous_output:
            os.system('cls' if os.name == 'nt' else 'clear')  # 清除屏幕，适配Windows
            print(final_output)
            previous_output = final_output

        time.sleep(flashinterval)  # 每隔flashinterval秒刷新一次显存信息

def main():
    parser = argparse.ArgumentParser(description="Monitor GPU memory usage")
    parser.add_argument('start', type=int, nargs='?', default=0, help="The starting GPU index (default is 0)")
    parser.add_argument('end', type=int, nargs='?', default=-1, help="The ending GPU index (default is -1)")
    parser.add_argument('flashinterval', type=int, nargs='?', default=1, help="Interval (in seconds) to refresh GPU memory information (default is 1)")

    args = parser.parse_args()

    monitor_gpu_memory(args.start, args.end, args.flashinterval)

if __name__ == "__main__":
    main()
