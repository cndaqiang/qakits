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

    memory_info = {}
    for line in result:
        gpu_id, total, used, free = map(int, line.split(', '))
        memory_info[gpu_id] = {
            'total': total,
            'used': used,
            'free': free
        }
    return memory_info


def find_best_by_divide(slots, depth=0):
    if len(slots) == 1:
        return slots[0]

    mid = len(slots) // 2
    group1 = slots[:mid]
    group2 = slots[mid:]

    avg1 = sum(s["used"] for s in group1) / len(group1)
    avg2 = sum(s["used"] for s in group2) / len(group2)

    indent = '  ' * depth
    print(f"{indent}分组 {[(s['gpu']) for s in group1]} 平均占用: {avg1:.2f} GB "
          f"| {[(s['gpu']) for s in group2]} 平均占用: {avg2:.2f} GB")

    return find_best_by_divide(group1, depth+1) if avg1 < avg2 else find_best_by_divide(group2, depth+1)


def get_best_gpu(start_gpu=0, end_gpu=-1, num_pergpu=0):
    """
    获取最佳 GPU
    - 当 num_pergpu < 1：使用递归对半分组平均显存占用的策略。
    - 当 num_pergpu >= 1：每num_pergpu个GPU分一组，基于总显存占用进行分配。

    参数:
    - start_gpu: int，起始GPU编号。
    - end_gpu: int，结束GPU编号（默认为-1，表示torch.cuda.device_count()）。
    - num_pergpu: int，每个物理GPU上划分的核心数量。

    返回:
    - best_gpu: int，分配的最佳GPU编号。
    """
    memory_info = get_nvidia_smi_memory()
    num_detected_gpus = torch.cuda.device_count()
    num_memory_entries = len(memory_info)
    is_mig = num_memory_entries > num_detected_gpus

    if end_gpu < 0:
        end_gpu = num_memory_entries if is_mig else num_detected_gpus

    output = f"{'ID':<6} {'Total Memory (GB)':<22} {'Used Memory (GB)':<22} {'Free Memory (GB)':<22}\n"
    output += "="*80 + "\n"

    slot_infos = []
    for idx in range(start_gpu, end_gpu):
        info = memory_info.get(idx, {})
        total = info.get('total', 0) / 1024
        used = info.get('used', 0) / 1024
        free = info.get('free', 0) / 1024

        output += f"{idx:<6} {total:>22.2f} {used:>22.2f} {free:>22.2f}\n"

        slot_infos.append({
            "gpu": idx,
            "total": total,
            "used": used,
            "free": free
        })

    slot_infos.sort(key=lambda x: x['gpu'])
    if num_pergpu < 1:
        best_slot = find_best_by_divide(slot_infos)
        best_gpu = best_slot['gpu']
    else:
        total_gpus = end_gpu - start_gpu
        total_slots = total_gpus * num_pergpu

        if num_pergpu == 1 or total_slots == total_gpus:
            slot_infos.sort(reverse=True, key=lambda x: x['free'])
            best_gpu = slot_infos[0]['gpu']
        else:
            group_usage = {}
            for slot in slot_infos:
                group_id = (slot['gpu'] - start_gpu) // num_pergpu
                if group_id not in group_usage:
                    group_usage[group_id] = {"total_used": 0.0, "slots": []}
                group_usage[group_id]["total_used"] += slot['used']
                group_usage[group_id]["slots"].append(slot)

            min_usage = min(info["total_used"] for info in group_usage.values())
            candidate_groups = [gid for gid, info in group_usage.items() if info["total_used"] == min_usage]

            candidate_slots = []
            for gid in candidate_groups:
                candidate_slots.extend(group_usage[gid]["slots"])

            candidate_slots.sort(reverse=True, key=lambda x: x['free'])
            best_gpu = candidate_slots[0]['gpu']

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
