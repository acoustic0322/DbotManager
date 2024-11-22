using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
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




        #endregion
    }
}
