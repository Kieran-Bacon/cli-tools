@ECHO OFF
python -c "import datetime; print(datetime.datetime.fromtimestamp(%1*1e-3, tz=datetime.timezone.utc))"