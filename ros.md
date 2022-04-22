
## ROS1のnodeをpython3で作成
```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws
# default poython3
catkin_make -DPYTHON_EXECUTABLE=/usr/bin/python3
```
rospkgが足りなかったのでinstall
```bash
python3 -m pip install rospkg
```
