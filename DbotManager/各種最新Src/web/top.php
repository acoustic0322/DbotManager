

<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>X-DBOTへようこそ</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      font-family: 'Inter', sans-serif;
      background: #0a0f1a;
      color: white;
    }
    .hero {
      background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
      padding: 100px 10%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
    }
    .hero-text {
      max-width: 600px;
    }
    .hero h1 {
      font-size: 48px;
      margin-bottom: 20px;
    }
    .hero p {
      font-size: 18px;
      color: #ccc;
    }
    .hero img {
      width: 300px;
      border-radius: 12px;
    }
    form {
      margin-top: 30px;
      display: flex;
      flex-direction: column;
      gap: 15px;
    }
    label {
      font-weight: bold;
      font-size: 14px;
    }
    input[type="text"],
    input[type="password"] {
      padding: 12px;
      border: 1px solid #374151;
      border-radius: 8px;
      background: #1e293b;
      color: white;
      font-size: 16px;
      transition: border-color 0.3s ease;
    }
    input[type="text"]:focus,
    input[type="password"]:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59,130,246,0.3);
    }
    .btn {
      margin-top: 10px;
      padding: 14px 30px;
      background: linear-gradient(to right, #3b82f6, #2563eb);
      color: white;
      border: none;
      border-radius: 10px;
      font-size: 18px;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.3s ease;
    }
    .btn:hover {
      background: linear-gradient(to right, #2563eb, #1d4ed8);
    }
    .section {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      padding: 80px 10%;
      border-bottom: 1px solid #1e293b;
    }
    .section.reverse {
      flex-direction: row-reverse;
    }
    .section img {
      width: 240px;
    }
    .section-content {
      max-width: 600px;
      flex: 1;
    }
    .section h2 {
      font-size: 32px;
      margin-bottom: 20px;
    }
    .section p {
      font-size: 16px;
      color: #cbd5e1;
      line-height: 1.8;
    }
    .section-image {
      flex: 0 0 240px;
      display: flex;
      justify-content: center;
    }
    .section.note h2 {
      color: #ffffff;
      font-size: 28px;
    }
    .section.note p {
      font-size: 15px;
      color: #94a3b8;
    }
    @media screen and (max-width: 768px) {
      .hero, .section {
        flex-direction: column;
        text-align: center;
      }
      .hero img, .section img {
        margin-top: 30px;
      }
    }
  </style>
</head>
<body>
  <section class="hero">
    <div class="hero-text">
      <h1>X-DBOTへようこそ</h1>
      <p>Xアカウントの自動化と管理を、もっとスマートに。</p>
      <form method="POST" action="login.php">
        <button class="btn" type="submit">ログイン</button>
      </form>
    </div>
    <img src="img/robot-hero.png" alt="X-DBOTロボット">
  </section>

  <section class="section">
    <div class="section-content">
      <h2>スケジュールポスト</h2>
      <p>予め登録したポスト本文を指定した時間帯にポストします。ポスト本文の設定数に上限はありません。</p>
    </div>
    <div class="section-image">
      <img src="img/icon-schedule.png" alt="スケジュールポストアイコン">
    </div>
  </section>

  <section class="section reverse">
    <div class="section-content">
      <h2>スケジュールポスト(AI)</h2>
      <p>スケジュールポストのポスト内容をAIで自動生成します。</p>
    </div>
    <div class="section-image">
      <img src="img/icon-schedule_ai.png" alt="スケジュールポストアイコン">
    </div>    
  </section>

  <section class="section note">
    <div class="section-content">
      <h2>リプライの自動返信<span style="font-size: 14px; color: #94a3b8;">※実装中</span></h2>
      <p>自身のアカウントへリプライが送られた際に、AIが自動で返信します。</p>
    </div>    
    <div class="section-image">
      <img src="img/icon-reply_ai.png" alt="リプライへの自動返信アイコン">
    </div>    
  </section>
</body>
</html>