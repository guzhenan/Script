import os
import argparse
from datetime import datetime, timedelta


def main():
    parser = argparse.ArgumentParser(description='文件清理工具')
    parser.add_argument('path', help='要清理的目标路径')
    parser.add_argument('-e', '--ext', nargs='+', help='按扩展名筛选（例如 .txt .log）')
    parser.add_argument('-d', '--days', type=int, help='按修改时间筛选（N天前的文件）')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('-p', '--preview', action='store_true', help='预览模式（不实际删除）')
    args = parser.parse_args()

    # 处理路径中的反斜杠
    normalized_path = os.path.normpath(args.path)
    if not os.path.exists(normalized_path):
        print(f"路径不存在: {normalized_path}")
        return

    if not os.path.isdir(args.path):
        print(f"需要目录路径: {args.path}")
        return

    # 收集符合条件的文件
    files_to_delete = []
    cutoff_time = datetime.now() - timedelta(days=args.days) if args.days else None

    if args.recursive:
        for root, _, files in os.walk(args.path):
            for file in files:
                file_path = os.path.join(root, file)
                if match_conditions(file_path, args.ext, cutoff_time):
                    files_to_delete.append(file_path)
    else:
        for item in os.listdir(args.path):
            file_path = os.path.join(args.path, item)
            if os.path.isfile(file_path) and match_conditions(file_path, args.ext, cutoff_time):
                files_to_delete.append(file_path)

    # 显示预览
    print(f"找到 {len(files_to_delete)} 个待清理文件:")
    for f in files_to_delete:
        print(f"  {f}")

    if args.preview:
        print("\n预览模式已启用，不会执行实际删除")
        return

    # 确认删除
    confirm = input("\n确认删除这些文件吗？(y/n): ").strip().lower()
    if confirm == 'y':
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"删除失败 {file_path}: {str(e)}")
        print(f"成功删除 {deleted_count} 个文件")
    else:
        print("取消删除操作")


def match_conditions(file_path, extensions, cutoff_time):
    if extensions:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in [e.lower() for e in extensions]:
            return False

    if cutoff_time:
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        if mtime > cutoff_time:
            return False

    return True


if __name__ == '__main__':
    main()
    
#bash
#执行定时任务
# python cleanup_script.py  “路径” -r

#查询定时任务 
# powershell -Command schtasks /Query /TN 'AutoCleanTask'

#创建定时任务 
# schtasks /Create /TN AutoCleanTask /TR ""C:\Users\w\AppData\Local\Microsoft\WindowsApps\python.exe" "f:\Code\cleanup_script.py" "目标路径" -d 7 -r" /SC DAILY /ST 12:00 /F

#删除定时任务
#powershell -Command schtasks /Delete /TN ’TaskName‘ /F