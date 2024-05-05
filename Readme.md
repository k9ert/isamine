
```
virtualenv --python=python3 .env
. ./.env/bin/activate
pip3 install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0
```

