$env:CARLA_ROOT = "C:\folder\carlaDev\CARLA_0.9.12\WindowsNoEditor"
$env:SCENARIO_RUNNER_ROOT = "C:\folder\code\scenario_runner_v0912"
$env:PYTHONPATH = $env:CARLA_ROOT + "\PythonAPI\carla\dist\carla-0.9.12-py3.7-win-amd64.egg"
$env:PYTHONPATH += ";" + $env:CARLA_ROOT + "\PythonAPI\carla\agents"
$env:PYTHONPATH += ";" + $env:CARLA_ROOT + "\PythonAPI\carla"
$env:PYTHONPATH += ";" + $env:CARLA_ROOT + "\PythonAPI"
get-childitem env:CARLA_ROOT
get-childitem env:SCENARIO_RUNNER_ROOT
get-childitem env:PYTHONPATH