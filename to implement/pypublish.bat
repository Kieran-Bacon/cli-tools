IF "%1"=="" (
    echo "Repository name is required"
) ELSE (
    pip install --user --upgrade setuptools wheel twine || goto :error
    python setup.py sdist bdist_wheel || goto :error
    python -m twine upload --verbose --config-file "~\OneDrive\bin\.pypirc" -r "%1" dist/*
    RMDIR /Q/S build || goto :error
    RMDIR /Q/S dist || goto :error
    goto :EOF
   :error
   echo Failed with error #%errorlevel%.
)
