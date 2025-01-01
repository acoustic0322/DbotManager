using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager
{
    public class DiscordTask
    {
        private string pythonScriptPath = string.Empty;
        private string pythonExePath = string.Empty;

        public void StartTask()
        {
            ReadIniファイル();
        }

        public void SendMessage(string message)
        {
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo
                {
                    FileName = pythonExePath, // Python実行ファイル
                    Arguments = $"\"{pythonScriptPath}\" {message.Replace(" ","-")}", // スクリプトのフルパスを指定
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                // プロセスを開始
                using (Process process = Process.Start(psi))
                {
                    // 標準出力を取得
                    string output = process.StandardOutput.ReadToEnd();
                    string error = process.StandardError.ReadToEnd();

                    // プロセス終了を待機
                    process.WaitForExit();

                    // 結果を表示
                    Console.WriteLine("Standard Output:");
                    Console.WriteLine(output);

                    if (!string.IsNullOrEmpty(error))
                    {
                        Console.WriteLine("Standard Error:");
                        Console.WriteLine(error);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました:");
                Console.WriteLine(ex.Message);
            }
        }

        private void ReadIniファイル()
        {
            string filePath = "config_discord.ini";

            // ファイルを読み込み
            if (File.Exists(filePath))
            {
                var lines = File.ReadAllLines(filePath);
                var settings = new Dictionary<string, Dictionary<string, string>>();
                string currentSection = "";

                foreach (var line in lines)
                {
                    if (line.StartsWith("[") && line.EndsWith("]"))
                    {
                        currentSection = line.Trim('[', ']');
                        if (!settings.ContainsKey(currentSection))
                        {
                            settings[currentSection] = new Dictionary<string, string>();
                        }
                    }
                    else if (!string.IsNullOrWhiteSpace(line) && line.Contains('='))
                    {
                        var keyValue = line.Split(new[] { '=' }, 2);
                        if (!string.IsNullOrEmpty(currentSection) && keyValue.Length == 2)
                        {
                            settings[currentSection][keyValue[0].Trim()] = keyValue[1].Trim();
                        }
                    }
                }

                // 設定を確認
                if (settings.ContainsKey("Discord") && settings["Discord"].ContainsKey("path"))
                {
                    pythonScriptPath = settings["Discord"]["path"];
                }
                if (settings.ContainsKey("Discord") && settings["Discord"].ContainsKey("exe"))
                {
                    pythonExePath = settings["Discord"]["exe"];
                }

            }
        }


    }
}
