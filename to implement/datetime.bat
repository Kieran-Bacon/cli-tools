@ECHO OFF
python -c "import datetime; print(datetime.datetime.fromtimestamp(%1, tz=datetime.timezone.utc))"