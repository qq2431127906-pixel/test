# make_self_extract.py — 零依赖制作自解压安装包
# 用 csc.exe (Windows 自带) 编译 sfx_stub.cs + 合并 ZIP

import sys, os, struct, shutil

version = sys.argv[1]
src = sys.argv[2]           # "dist\\assistant"
exe_name = f"学术论文辅助写作智能体_Setup_v{version}.exe"
zip_name = f"学术论文辅助写作_v{version}.zip"

# ============================================================
# 1. 创建 ZIP
# ============================================================
print("Creating ZIP...")
shutil.make_archive(zip_name.replace(".zip", ""), 'zip', src)
zip_size = os.path.getsize(zip_name)
print(f"ZIP created: {zip_name} ({zip_size/1024/1024:.1f} MB)")

# ============================================================
# 2. 编译 C# stub
# ============================================================
candidates = [
    r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
    r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe",
]
csc = None
for c in candidates:
    if os.path.exists(c):
        csc = c
        break

if not csc:
    print("csc.exe not found, ZIP only")
    sys.exit(0)

refs = r"/reference:System.IO.Compression.FileSystem.dll"
cmd = f'"{csc}" /target:exe /out:sfx_stub.exe {refs} sfx_stub.cs'
print(f"Compiling: {cmd}")
result = os.system(cmd)
if result != 0:
    print(f"csc failed (exit {result}), ZIP only")
    sys.exit(0)

# ============================================================
# 3. 合并 stub.exe + zip 数据
# ============================================================
print("Merging stub + ZIP...")
stub = open("sfx_stub.exe", "rb").read()
zip_data = open(zip_name, "rb").read()

# 末尾 8 字节 footer: [4-byte zip_length] [4-byte magic]
magic = 0x5A49505A  # "ZIPZ"
footer = struct.pack("<II", len(zip_data), magic)
combined = stub + zip_data + footer

with open(exe_name, "wb") as f:
    f.write(combined)

mb = os.path.getsize(exe_name) / 1024 / 1024
print(f"CREATED: {exe_name} ({mb:.1f} MB)")
