using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace DbotManager
{
    public static class SupportUtil
    {
        // 条件に一致する行を選択状態にするメソッド
        public static void SelectRowsByColumnValue(DataGridView dataGridView, string columnName, object targetValue)
        {
            // DataGridViewの現在の選択をすべて解除
            dataGridView.ClearSelection();

            foreach (DataGridViewRow row in dataGridView.Rows)
            {
                // 行が新規行ではない場合にのみチェック
                if (!row.IsNewRow && row.Cells[columnName]?.Value?.ToString() == targetValue?.ToString())
                {
                    // 条件に一致する行を選択状態にする
//                    row.Selected = true;

                    dataGridView.Rows[row.Index].Selected = true;
                }
            }
        }

        public static T GetRandomItem<T>(List<T> list)
        {
            if (list == null || list.Count == 0)
            {
                return default(T);
//                throw new ArgumentException("リストが空またはnullです。");
            }

            Random random = new Random();
            int index = random.Next(list.Count); // 0からlist.Count-1までのランダムなインデックスを取得
            return list[index];
        }

        public static string ExtractNumber(string input)
        {
            // URLの場合と単なる数値の場合を考慮
            Match match = Regex.Match(input, @"(?:status/(\d+)|^(\d+))");

            if (match.Success)
            {
                // マッチした部分のうち、最初にキャプチャされたグループ（数値部分）を返す
                return match.Groups[1].Success ? match.Groups[1].Value : match.Groups[2].Value;
            }

            return null;
        }

        public static int ParseOrDefault(object value, int defaultValue)
        {
            if (value != null && int.TryParse(value.ToString(), out int result))
            {
                return result;
            }
            return defaultValue;
        }

        #region ファイル処理関連

        // TextBoxにログを表示するメソッド
        public static void AppendLog(string message , TextBox textBox)
        {
            if (message != null)
            {
                textBox.Invoke((MethodInvoker)(() =>
                    textBox.AppendText(message + Environment.NewLine)
                ));

                // 必要に応じてログファイルにも書き込む
                SaveLogToFile(message , textBox);
            }
            /*
            if (message != null)
            {
                textBoxLog.Invoke((MethodInvoker)(() => textBoxLog.AppendText(message + Environment.NewLine)));

                // ログファイルに書き込み
                SaveLogToFile(message);
            }
            */
        }

        // ログメッセージを日付別のファイルに保存するメソッド
        public static void SaveLogToFile(string message , TextBox textBox)
        {
            // ログフォルダのパスを設定
            string logDirectory = "log";

            MakeFolder(logDirectory);

            // 日付別のログファイルパスを設定
            string logFilePath = Path.Combine(logDirectory, $"log_{DateTime.Now:yyyyMMdd}.txt"); // 例: log/log_20241113.txt

            try
            {
                // メッセージを追記で日別ログファイルに書き込み
                using (StreamWriter writer = new StreamWriter(logFilePath, true))
                {
                    writer.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss}: {message}");
                }
            }
            catch (Exception ex)
            {
                // ファイル書き込みに失敗した場合のエラーハンドリング
                textBox.Invoke((MethodInvoker)(() => textBox.AppendText("ログの書き込みに失敗しました: " + ex.Message + Environment.NewLine)));
            }
        }

        public static void MakeFolder(string folderPath)
        {
            // ログフォルダが存在しない場合は作成
            if (!Directory.Exists(folderPath))
            {
                Directory.CreateDirectory(folderPath);
            }
        }

        public static string ToSafeString(object value)
        {
            return value == null || value == DBNull.Value
                ? string.Empty
                : value.ToString();
        }

        public static bool ParseBool(object value)
        {
            return value?.ToString() == "1";
        }

        #endregion
    }
}
