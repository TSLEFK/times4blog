pythonのパッケージ管理用にディレクトリを作成する。

> python -m venv venv

requirements.txtを作成し、必要なモジュールのインストールを行う。

> pip install -r requirements.txt -t venv

はてぶ,slackの情報を設定する。

> cp .env.sample .env

---


> set PYTHONPATH=%PYTHONPATH%;path\to\project\of\venv
