# override
$CARLA_ROOT = "C:\folder\carlaDev\CARLA_0.9.13\WindowsNoEditor"
[System.Environment]::SetEnvironmentVariable("CARLA_ROOT", $CARLA_ROOT, "User")

$env:SCENARIO_RUNNER_ROOT =  (Convert-Path .)
[System.Environment]::SetEnvironmentVariable("SCENARIO_RUNNER_ROOT", $SCENARIO_RUNNER_ROOT, "User")

$PYTHONPATH = $CARLA_ROOT + "\PythonAPI"
$PYTHONPATH += ";" +  $CARLA_ROOT + "\PythonAPI\carla"
$PYTHONPATH += ";" +  $CARLA_ROOT + "\PythonAPI\carla\dist\carla-0.9.13-py3.7-win-amd64.egg"
[System.Environment]::SetEnvironmentVariable("PYTHONPATH", $PYTHONPATH, "User")
