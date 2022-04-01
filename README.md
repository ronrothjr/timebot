Run in the timebot repo folder to setup Timebot
```
python -m virtualenv kivy_venv
python setup.py develop

Run in the timebot repo folder to start Timebot
```
python app/main.py
```

Run watcher while modifying files in app folder:
```
python watch.py --tests app
```

Add this to your launch.json in Visual Studio Code:
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Timebot",
            "type": "python",
            "request": "launch",
            "python": "${command:python.interpreterPath}",
            "program": "${workspaceFolder}/app/main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceRoot}",
        }
    ]
}
```
