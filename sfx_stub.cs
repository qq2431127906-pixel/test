// sfx_stub.cs — 自解压安装器 stub，由 csc.exe 编译
using System;
using System.IO;
using System.IO.Compression;
using System.Diagnostics;

class Sfx {
    static void Main() {
        try {
            string self = System.Reflection.Assembly.GetEntryAssembly().Location;
            byte[] all = File.ReadAllBytes(self);

            // 读取末尾 8 字节 footer
            int footerLen = 8;
            int zipLen = BitConverter.ToInt32(all, all.Length - footerLen);
            int zipStart = all.Length - footerLen - zipLen;

            byte[] zipData = new byte[zipLen];
            Array.Copy(all, zipStart, zipData, 0, zipLen);

            // 解压到 %LOCALAPPDATA%
            string dest = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "AcademicWritingAssistant");

            if (Directory.Exists(dest)) {
                try { Directory.Delete(dest, true); } catch {}
            }
            Directory.CreateDirectory(dest);

            // 写入临时 zip 文件然后解压（兼容 .NET 4.x）
            string tmpZip = Path.GetTempFileName() + ".zip";
            File.WriteAllBytes(tmpZip, zipData);
            ZipFile.ExtractToDirectory(tmpZip, dest);
            File.Delete(tmpZip);

            // 创建 .env（如果没有）
            string env = Path.Combine(dest, ".env");
            string envEx = Path.Combine(dest, ".env.example");
            if (!File.Exists(env) && File.Exists(envEx)) {
                File.Copy(envEx, env);
                Process.Start("notepad", env);
            }

            // 创建桌面快捷方式
            string desktop = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
            string shortcut = Path.Combine(desktop, "学术论文辅助写作.lnk");
            Type shellType = Type.GetTypeFromProgID("WScript.Shell");
            object shell = Activator.CreateInstance(shellType);
            object sc = shellType.InvokeMember("CreateShortcut",
                System.Reflection.BindingFlags.InvokeMethod, null, shell, new object[] { shortcut });
            Type scType = sc.GetType();
            scType.InvokeMember("TargetPath",
                System.Reflection.BindingFlags.SetProperty, null, sc,
                new object[] { Path.Combine(dest, "run.exe") });
            scType.InvokeMember("WorkingDirectory",
                System.Reflection.BindingFlags.SetProperty, null, sc,
                new object[] { dest });
            scType.InvokeMember("Save",
                System.Reflection.BindingFlags.InvokeMethod, null, sc, null);

            // 启动
            Process.Start(Path.Combine(dest, "run.exe"));
        } catch (Exception e) {
            File.WriteAllText(
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
                "install_error.txt"), e.ToString());
        }
    }
}
