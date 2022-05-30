def set_cam_3(self, x=0, y=0, z=0, roll=0, pitch=0, yaw=0, width=1920, height=1080,
                attach_to=None, margin_pix=0, sensor='sensor.camera.rgb'):
    '''fov60のカメラを6台設置してcubemap画像を作成する'''
    '''left, front, right, zoom'''
    '''marginを有効にするとマージンだけ大きい画像が取得されるので注意'''

    fov_h = 60.0

    # 少し大きくとることで結合部を自然にする
    if margin_pix != 0:
        img_width = width
        focal = width / (2.0 * math.tan(math.radians(fov_h / 2)))
        fov_h = math.degrees(2 * math.atan((img_width + margin_pix * 2) / 2 / focal))
        width = width + margin_pix * 2

    # 複数カメラの設定をそろえる
    attribute_dic = {}
    attribute_dic['exposure_mode'] = 'manual'
    attribute_dic['fstop'] = '1.4'
    attribute_dic['iso'] = '1.0'
    attribute_dic['gamma'] = '2.2'
    attribute_dic['shutter_speed'] = '2.0'
    attribute_dic['bloom_intensity'] = '0.0'
    attribute_dic['lens_flare_intensity'] = '0.0'
    attribute_dic['motion_blur_intensity'] = '0.0'

    # width = 1920 // 2 // 3
    # height = 1080 // 2

    front = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw, width=width,
                            height=height, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
    right = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw + 60, width=width,
                            height=height, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
    left = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw - 60, width=width,
                        height=height, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
    zoom = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw + 180, width=width,
                        height=height, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)

    return left, front, right, zoom


def main():
    util = CarlaUtil()
    world = util.client.get_world()
    m = world.get_map()
    start_pose = random.choice(m.get_spawn_points())
    # start_pose = carla.Transform(carla.Location(x=-466, y=315, z=0.4), carla.Rotation(roll=0.0, pitch=0.0, yaw=0.0))
    waypoint = m.get_waypoint(start_pose.location)
    blueprint_library = world.get_blueprint_library()
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_folder = "dataset" + "/" + now_str
    os.makedirs(out_folder, exist_ok=True)

    try:
        # set car
        vehicle = world.spawn_actor(random.choice(blueprint_library.filter('vehicle.*')), start_pose)
        util.actor_list.append(vehicle)
        vehicle.set_simulate_physics(False)

        FPS = 30
        CAR_SPEED = 80    # km/h
        m_per_frame = CAR_SPEED / 3600 * 1000 / FPS  # m/frame
        cube_size = 1080 // 2   # 2048
        width = 1920 
        height = 1920
        margin_pix_per = 0.5    # 画面端を解像度多めにとって後で削除、つなぎ目が自然になるが処理重くなる
        margin_pix = int(cube_size * margin_pix_per)
        # set sensor ~4 cameras
        cam_num = 1
        front, right, left, zoom = util.set_cam_3(
            x=2.2, z=1.4, width=width, height=height, attach_to=vehicle, margin_pix=margin_pix)
        # front2, rear2, right2, left2, up2, down2 = util.set_cam_cubemap(
        #     x=2.2, z=1.4, img_size=cube_size, attach_to=vehicle, margin_pix=margin_pix)
        # front3, rear3, right3, left3, up3, down3 = util.set_cam_cubemap(
        #     x=2.2, z=1.4, img_size=cube_size, attach_to=vehicle, margin_pix=margin_pix)
        # front4, rear4, right4, left4, up4, down4 = util.set_cam_cubemap(
        #     x=2.2, z=1.4, img_size=cube_size, attach_to=vehicle, margin_pix=margin_pix)

        # generate map
        # map_x, map_y = cube2eq_map(cube_size, cube_size * 6, "line_v")
        # map_x = np.loadtxt("fisheye_map_x.txt", dtype=np.float32)
        # map_y = np.loadtxt("fisheye_map_y.txt", dtype=np.float32)

        tick_count = 0
        # Create a synchronous mode context.
        with CarlaSyncMode(world, front, right, left, zoom, fps=FPS) as sync_mode:
            while True:
                # Advance the simulation and wait for the data.
                datas = sync_mode.tick(timeout=180.0)

                del datas[0]  # 0 is world snapshot
                img_list = []
                for data in datas:
                    img = util.render_image(data)
                    if margin_pix != 0:
                        h, w, _ = img.shape
                        img = img[:, margin_pix:(w - margin_pix)]
                        # img = img[margin_pix:(h - margin_pix), margin_pix:(w - margin_pix)]
                    img_list.append(img)

                for i in range(cam_num):
                    dst = cv2.hconcat([img_list[0], img_list[1], img_list[2]])
                    cv2.imshow(f"cube{i}", dst)
                    cv2.imwrite(f"screenshot/cam3{i}_{tick_count:06}.png", dst)

                if cv2.waitKey(1) == 27:
                    break

                # Choose the next waypoint and update the car location.
                waypoint = random.choice(waypoint.next(m_per_frame))
                vehicle.set_transform(waypoint.transform)
                tick_count += 1

    finally:
        print('destroying actors.')
        util.destroy()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
import random
import datetime
import itertools
from tqdm import tqdm
import argparse
import os
import carla

from carla_util import CarlaUtil
from carla_util import CarlaSyncMode

# 2車両を生成してwaypointに沿わせて走行
# carla.logファイルを保存する


def main(args):
    if args.out_file is None:
        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = "carlalog"
        os.makedirs(out_folder, exist_ok=True)
        args.out_file = os.path.join(os.getcwd(), out_folder) + "/carla_" + now_str + ".log"

    m_per_frame = args.kmph / 3600 * 1000 / args.fps
    car_distance = args.car_distance  # 正確な車間距離ではなく、車両の中心点間の距離
    random.seed(args.seed)

    try:
        util = CarlaUtil(timeout=20)
        world = util.client.get_world()
        carla_map = world.get_map()
        blueprint_library = world.get_blueprint_library()

        # set car
        # vehicle_list = []
        waypoint_list = []
        # start_pose = random.choice(carla_map.get_spawn_points())
        start_pose = carla.Transform(carla.Location(x=args.x, y=args.y, z=args.z))
        vehicle = world.spawn_actor(random.choice(blueprint_library.filter(args.filter)), start_pose)
        waypoint = carla_map.get_waypoint(start_pose.location)
        vehicle.set_simulate_physics(False)
        vehicle.set_transform(waypoint.transform)
        waypoint_list.append(waypoint)
        # vehicle_list.append(vehicle)
        util.vehicle_list.append(vehicle)
        # util.actor_list.append(vehicle)

        # second car
        start_pose = waypoint.next(car_distance)[0].transform
        start_pose.location.z += 0.5    # colision対策
        vehicle = world.spawn_actor(random.choice(blueprint_library.filter(args.filter)), start_pose)
        waypoint = carla_map.get_waypoint(start_pose.location)
        vehicle.set_simulate_physics(False)
        vehicle.set_transform(waypoint.transform)
        waypoint_list.append(waypoint)
        util.vehicle_list.append(vehicle)
        # util.actor_list.append(vehicle)

        # set sensor empty
        sensors = []
        sensors.append(util.set_cam(x=2.2, z=1.4, attach_to=util.vehicle_list[0]))
        is_fisrt_time = True

        # Create a synchronous mode context.
        with CarlaSyncMode(world, *sensors, fps=args.fps) as sync_mode:
            for i in tqdm(itertools.count()):
                if is_fisrt_time:
                    util.client.start_recorder(args.out_file, True)
                    is_fisrt_time = False

                # Advance the simulation and wait for the data.
                datas = sync_mode.tick(timeout=180.0)

                # Choose the next waypoint and update the car location.
                for i, vehicle in enumerate(util.vehicle_list):
                    # waypoint_list[i] = random.choice(waypoint_list[i].next(m_per_frame))
                    waypoint_list[i] = waypoint_list[i].next(m_per_frame)[0]    # list内の順序は不明だが、0だとだいたい直進する
                    vehicle.set_transform(waypoint_list[i].transform)

    finally:
        util.client.stop_recorder()
        print('destroying actors.')
        util.destroy()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-o', '--out_file',
        help='output carla log name (abs path) c:/hoge.log')
    argparser.add_argument(
        '--fps',
        default="30.0", type=float,
        help='record fps')
    argparser.add_argument(
        '--kmph',
        default="80.0", type=float,
        help='ego car speed[km/h] default="80.0"')
    argparser.add_argument(
        '--filter',
        default='vehicle.audi.TT',
        help='actor filter (default: "vehicle.*")')
    argparser.add_argument(
        '-s', '--seed',
        default="0", type=int,
        help='random seed value')
    argparser.add_argument(
        '-x', '--x',
        default="193.7", type=float,
        help='start loc x')
    argparser.add_argument(
        '-y', '--y',
        default="293.5", type=float,
        help='start loc y')
    argparser.add_argument(
        '-z', '--z',
        default="1.0", type=float,
        help='start loc z')
    argparser.add_argument(
        '-d', '--car_distance',
        default="30.0", type=float,
        help='car distance default="30.0"')
    args = argparser.parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


import math
import random
import os
import time
import numpy as np
import cv2
try:
    import queue
except ImportError:
    import Queue as queue
import carla
# from carla import ColorConverter as cc


class CarlaSyncMode(object):
    """
    Context manager to synchronize output from different sensors. Synchronous
    mode is enabled as long as we are inside this context

        with CarlaSyncMode(world, sensors) as sync_mode:
            while True:
                data = sync_mode.tick(timeout=1.0)

    """
    # synchronous_mode.py より

    def __init__(self, world, *sensors, **kwargs):
        self.world = world
        self.sensors = sensors
        self.frame = None
        self.delta_seconds = 1.0 / kwargs.get('fps', 20)
        self._queues = []
        self._settings = None

    def __enter__(self):
        self._settings = self.world.get_settings()
        self.frame = self.world.apply_settings(carla.WorldSettings(
            no_rendering_mode=False,
            synchronous_mode=True,
            fixed_delta_seconds=self.delta_seconds))

        def make_queue(register_event):
            q = queue.Queue()
            register_event(q.put)
            self._queues.append(q)

        make_queue(self.world.on_tick)
        for sensor in self.sensors:
            make_queue(sensor.listen)
        return self

    def tick(self, timeout):
        self.frame = self.world.tick()
        data = [self._retrieve_data(q, timeout) for q in self._queues]
        assert all(x.frame == self.frame for x in data)
        return data

    def __exit__(self, *args, **kwargs):
        self.world.apply_settings(self._settings)

    def _retrieve_data(self, sensor_queue, timeout):
        while True:
            data = sensor_queue.get(timeout=timeout)
            if data.frame == self.frame:
                return data


class CarlaUtil():
    '''CARLA PythonAPIの汎用処理クラス'''

    def __init__(self, host='localhost', port=2000, timeout=5.0):
        self.client = carla.Client(host, port)
        self.client.set_timeout(timeout)
        self.sensor_list = []
        self.vehicle_list = []
        self.actor_list = []

    def set_spectator_ego(self):
        world = self.client.get_world()
        spectator = world.get_spectator()
        vehicle_bp = random.choice(world.get_blueprint_library().filter('vehicle.bmw.*'))
        transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.try_spawn_actor(vehicle_bp, transform)
        # Wait for world to get the vehicle actor
        world.tick()
        world_snapshot = world.wait_for_tick()
        actor_snapshot = world_snapshot.find(vehicle.id)
        # Set spectator at given transform (vehicle transform)
        spectator.set_transform(actor_snapshot.get_transform())

    def set_spectator(self, x, y, z, roll=0.0, pitch=0.0, yaw=0.0):
        world = self.client.get_world()
        spectator = world.get_spectator()
        spawn_point = carla.Transform(carla.Location(x, y, z), carla.Rotation(roll=roll, pitch=pitch, yaw=yaw))
        spectator.set_transform(spawn_point)

    def spawn_car_pos(self, x, y, z, roll=0, pitch=0, yaw=0, filter_str="vehicle.*", color="recommended", role_name="role_name", physics=True, is_static=False):
        world = self.client.get_world()
        blueprints = world.get_blueprint_library().filter(filter_str)
        blueprint = random.choice(blueprints)
        if blueprint.has_attribute('color'):
            if color == "recommended":
                color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        blueprint.set_attribute('role_name', role_name)
        spawn_point = carla.Transform(carla.Location(x, y, z), carla.Rotation(roll=roll, pitch=pitch, yaw=yaw))
        vhehicle = world.spawn_actor(blueprint, spawn_point)
        vhehicle.set_simulate_physics(physics)
        # temp set light
        # light_mask = carla.VehicleLightState.NONE
        # light_mask |= carla.VehicleLightState.Interior
        # light_mask |= carla.VehicleLightState.Position
        # if test_flag:
        #     light_mask |= carla.VehicleLightState.HighBeam
        # else:
        #     light_mask |= carla.VehicleLightState.LowBeam
        # light_mask |= carla.VehicleLightState.Brake
        # vehicle.set_light_state(carla.VehicleLightState(light_mask))   # temp
        if not is_static:
            self.vehicle_list.append(vhehicle)

    # def _add_vehicle_light(self, vehicle_actor, vehicle_light_state):
    #     # temp set light
    #     light_mask = carla.VehicleLightState.NONE
    #     light_mask |= vehicle_light_state
    #     vehicle.set_light_state(carla.VehicleLightState(light_mask))   # temp

    def set_map(self, map_name, wait=10, force=True):
        '''mapをロードする　force=Falseの場合、設定MAPが現在のMAPと同じならリロードしない'''

        world = self.client.get_world()
        if force or map_name != world.get_map().name:
            print('load map %r.' % map_name)
            self.client.load_world(map_name)
            time.sleep(wait)

    def set_weather(self, weather_name, wait=10):
        print('load weather %r.' % weather_name)
        world = self.client.get_world()
        world.set_weather(getattr(carla.WeatherParameters, weather_name))
        time.sleep(wait)

    def set_weather_val(
            self,
            cloudiness=None,
            precipitation=None,
            precipitation_deposits=None,
            wind_intensity=None,
            sun_azimuth_angle=None,
            sun_altitude_angle=None,
            fog_density=None,
            fog_distance=None,
            wetness=None,
            fog_falloff=None):
        world = self.client.get_world()
        weather = world.get_weather()
        if cloudiness is not None:
            weather.cloudiness = cloudiness
        if precipitation is not None:
            weather.precipitation = precipitation
        if precipitation_deposits is not None:
            weather.precipitation_deposits = precipitation_deposits
        if wind_intensity is not None:
            weather.wind_intensity = wind_intensity
        if sun_azimuth_angle is not None:
            weather.sun_azimuth_angle = sun_azimuth_angle
        if sun_altitude_angle is not None:
            weather.sun_altitude_angle = sun_altitude_angle
        if fog_density is not None:
            weather.fog_density = fog_density
        if fog_distance is not None:
            weather.fog_distance = fog_distance
        if wetness is not None:
            weather.wetness = wetness
        if fog_falloff is not None:
            weather.fog_falloff = fog_falloff
        world.set_weather(weather)

    def print_carla_env(self):
        world = self.client.get_world()
        weather = world.get_weather()
        print(f"server_version, {self.client.get_server_version()}")
        print(f"cloudiness, {weather.cloudiness}")
        print(f"precipitation, {weather.precipitation}")
        print(f"precipitation_deposits, {weather.precipitation_deposits}")
        print(f"wind_intensity, {weather.wind_intensity}")
        print(f"sun_azimuth_angle, {weather.sun_azimuth_angle}")
        print(f"sun_altitude_angle, {weather.sun_altitude_angle}")
        print(f"fog_density, {weather.fog_density}")
        print(f"fog_distance, {weather.fog_distance}")
        print(f"wetness, {weather.wetness}")
        print(f"fog_falloff, {weather.fog_falloff}")

    def sync_rgb_cap(self, x, y, z, roll=0, pitch=0, yaw=0, width=1280, height=720, fov_h=90, outfolder="out", frame_count=0):
        '''指定位置にrgbカメラを設置して同期モードで取得、指定フォルダに保存'''
        world = self.client.get_world()
        blueprint_library = world.get_blueprint_library()
        spawn_point = carla.Transform(carla.Location(x, y, z), carla.Rotation(roll=roll, pitch=pitch, yaw=yaw))

        # カメラの解像度、FOV、カメラの名前を設定する
        rgb_cam_bp = blueprint_library.find('sensor.camera.rgb')
        rgb_cam_bp.set_attribute('image_size_x', f'{width}')
        rgb_cam_bp.set_attribute('image_size_y', f'{height}')
        rgb_cam_bp.set_attribute('fov', str(fov_h))
        rgb_cam_bp.set_attribute('role_name', 'rgb_cam')
        rgb_cam = world.spawn_actor(rgb_cam_bp, spawn_point)

        work_dir = outfolder
        os.makedirs(outfolder, exist_ok=True)

        with CarlaSyncMode(world, rgb_cam, fps=30) as sync_mode:
            # clock.tick()
            # Advance the simulation and wait for the data.
            snapshot, image_rgb = sync_mode.tick(timeout=10.0)

            mat_rgb = self.render_image(image_rgb)

            cv2.imwrite(work_dir + '/rgb_' + str(frame_count).zfill(6) + '.png', mat_rgb)

        rgb_cam.destroy()

    def sync_capture_hawk(self, x, y, z, roll=0, pitch=0, yaw=0, width=1280, height=720, fov_h=90.0, outfolder="out", frame_count=0):
        '''同じ指定位置にrgb,depth,semsegカメラを設置して同期モードで取得、指定フォルダに保存'''
        world = self.client.get_world()
        blueprint_library = world.get_blueprint_library()
        spawn_point = carla.Transform(carla.Location(x, y, z), carla.Rotation(roll=roll, pitch=pitch, yaw=yaw))

        # カメラの解像度、FOV、カメラの名前を設定する
        rgb_cam_bp = blueprint_library.find('sensor.camera.rgb')
        rgb_cam_bp.set_attribute('image_size_x', f'{width}')
        rgb_cam_bp.set_attribute('image_size_y', f'{height}')
        rgb_cam_bp.set_attribute('fov', str(fov_h))
        rgb_cam_bp.set_attribute('role_name', 'rgb_cam')
        rgb_cam = world.spawn_actor(rgb_cam_bp, spawn_point)

        depth_cam_bp = blueprint_library.find('sensor.camera.depth')
        depth_cam_bp.set_attribute('image_size_x', f'{width}')
        depth_cam_bp.set_attribute('image_size_y', f'{height}')
        depth_cam_bp.set_attribute('fov', str(fov_h))
        depth_cam_bp.set_attribute('role_name', 'depth_cam')
        depth_cam = world.spawn_actor(depth_cam_bp, spawn_point)

        semseg_cam_bp = blueprint_library.find('sensor.camera.semantic_segmentation')
        semseg_cam_bp.set_attribute('image_size_x', f'{width}')
        semseg_cam_bp.set_attribute('image_size_y', f'{height}')
        semseg_cam_bp.set_attribute('fov', str(fov_h))
        semseg_cam_bp.set_attribute('role_name', 'semseg_cam')
        semseg_cam = world.spawn_actor(semseg_cam_bp, spawn_point)

        work_dir = outfolder
        os.makedirs(outfolder, exist_ok=True)

        with CarlaSyncMode(world, rgb_cam, depth_cam, semseg_cam, fps=30) as sync_mode:
            # clock.tick()
            # Advance the simulation and wait for the data.
            snapshot, image_rgb, image_depth, image_semseg = sync_mode.tick(timeout=10.0)

            mat_rgb = self.render_image(image_rgb)
            mat_depth = self.render_image(image_depth)
            mat_semseg = self.render_image(image_semseg)

            cv2.imwrite(work_dir + '/rgb_' + str(frame_count).zfill(6) + '.png', mat_rgb)
            cv2.imwrite(work_dir + '/depth_' + str(frame_count).zfill(6) + '.png', mat_depth)
            cv2.imwrite(work_dir + '/sem_' + str(frame_count).zfill(6) + '.png', mat_semseg)
        # carla.sensor(front_camera_rgb_fix)
        # print(front_camera_rgb_fix.Actor.Sensor.SensorData.Image.FOV)

        rgb_cam.destroy()
        depth_cam.destroy()
        semseg_cam.destroy()

    def sync_capture_hdr(self, x=0, y=0, z=0, roll=0, pitch=0, yaw=0, width=1280, height=720, fov_h=90.0, outfolder="out", frame_count=0, attach_to=None):
        '''指定位置にHDH multicamを設置して同期モードで取得、指定フォルダに保存'''
        world = self.client.get_world()

        attribute_dic = {}
        attribute_dic['bloom_intensity'] = '0.0'
        attribute_dic['fstop'] = '1.2'
        attribute_dic['iso'] = '1600.0'
        attribute_dic['gamma'] = '1.0'
        attribute_dic['lens_flare_intensity'] = '0.0'
        attribute_dic['exposure_mode'] = 'manual'
        attribute_dic['exposure_compensation'] = '0.0'
        attribute_dic['motion_blur_intensity'] = '0.0'

        # 10 camera
        shutter_speed_ary = [20, 125, 500, 2000, 10000, 50000, 100000, 200000, 500000, 1000000]

        cl = []
        for shutter_speed in shutter_speed_ary:
            attribute_dic['shutter_speed'] = str(shutter_speed)
            cam_actor = self.set_cam(x=x, y=y, z=z, roll=0, pitch=0, yaw=0, fov_h=fov_h, width=width,
                                     height=height, attribute_dic=attribute_dic)
            cl.append(cam_actor)

        os.makedirs(outfolder, exist_ok=True)

        with CarlaSyncMode(world, cl[0], cl[1], cl[2], cl[3], cl[4], cl[5], cl[6], cl[7], cl[8], cl[9], fps=30) as sync_mode:
            # Advance the simulation and wait for the data.
            datas = sync_mode.tick(timeout=180.0)

            del datas[0]  # 0 is world snapshot
            img_list = []
            for data in datas:
                img_list.append(self.render_image(data))

            # save origin image
            for i, img in enumerate(img_list):
                cv2.imwrite(f"{outfolder}/rgb_ss{shutter_speed_ary[i]:07}_{frame_count:06}.png", img)

        # for cam_actor in cl:
        #     cam_actor.destroy()

    def render_image(self, image):
        '''carla sensor image → opencv mat'''
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        return array

    def pil2cv(self, image):
        ''' PIL型 -> OpenCV型 '''
        new_image = np.array(image, dtype=np.uint8)
        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
        elif new_image.shape[2] == 4:  # 透過
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
        return new_image

    def set_sensor(self, x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0, attach_to=None,
                   sensor='sensor.camera.rgb', attribute_dic={}):
        world = self.client.get_world()
        blueprint_library = world.get_blueprint_library()

        bp_sensor = blueprint_library.find(sensor)

        for attr_name, attr_value in attribute_dic.items():
            bp_sensor.set_attribute(attr_name, attr_value)

        tf = carla.Transform(carla.Location(x, y, z), carla.Rotation(roll=roll, pitch=pitch, yaw=yaw))
        if attach_to is None:
            sensor_actor = world.spawn_actor(bp_sensor, tf)
        else:
            sensor_actor = world.spawn_actor(bp_sensor, tf, attach_to=attach_to)

        self.sensor_list.append(sensor_actor)
        return sensor_actor

    def set_cam(self, x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0, width=1280, height=720,
                fov_h=90.0, attach_to=None, sensor='sensor.camera.rgb', attribute_dic={}):
        world = self.client.get_world()
        blueprint_library = world.get_blueprint_library()

        bp_cam = blueprint_library.find(sensor)
        bp_cam.set_attribute('image_size_x', str(width))
        bp_cam.set_attribute('image_size_y', str(height))
        bp_cam.set_attribute('fov', str(fov_h))

        for attr_name, attr_value in attribute_dic.items():
            bp_cam.set_attribute(attr_name, attr_value)

        tf = carla.Transform(carla.Location(x, y, z), carla.Rotation(roll=roll, pitch=pitch, yaw=yaw))
        if attach_to is None:
            camera_rgb = world.spawn_actor(bp_cam, tf)
        else:
            camera_rgb = world.spawn_actor(bp_cam, tf, attach_to=attach_to)

        self.sensor_list.append(camera_rgb)
        return camera_rgb

    def set_cam_cubemap(self, x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0, img_size=1080, attach_to=None, margin_pix=0, sensor='sensor.camera.rgb', shutter_speed=200.0):
        '''fov90のカメラを6台設置してcubemap画像を作成する'''
        '''front, rear, right, left, up, downの順で返す'''
        '''marginを有効にするとマージンだけ大きい画像が取得されるので注意'''

        fov_h = 90.0

        # 少し大きくとることで結合部を自然にする
        if margin_pix != 0:
            img_width = img_size
            focal = img_size / (2.0 * math.tan(math.radians(fov_h / 2)))
            fov_h = math.degrees(2 * math.atan((img_width + margin_pix * 2) / 2 / focal))
            img_size = img_size + margin_pix * 2

        attribute_dic = {}

        if sensor == 'sensor.camera.rgb':
            # 複数カメラの設定をそろえる
            attribute_dic['bloom_intensity'] = '0.0'
            attribute_dic['fstop'] = '1.4'
            attribute_dic['iso'] = '100.0'  # カメラ間の境界低減に若干効果があったように見える
            attribute_dic['gamma'] = '2.2'
            attribute_dic['lens_flare_intensity'] = '0.0'
            attribute_dic['shutter_speed'] = str(shutter_speed)  # カメラ間の境界低減に若干効果があったように見える
            attribute_dic['exposure_mode'] = 'manual'
            attribute_dic['motion_blur_intensity'] = '0.0'
            attribute_dic['motion_blur_max_distortion'] = '0.0'
            attribute_dic['motion_blur_min_object_screen_size'] = '0.0'
            # attribute_dic['blade_count'] = '0'
            attribute_dic['white_clip'] = '0.0'  # カメラ間の境界低減に若干効果があったように見える
            # attribute_dic['enable_postprocess_effects'] = 'False'
            # attribute_dic['lens_circle_falloff'] = '10.0'
            # attribute_dic['lens_x_size'] = '1.0'
            # attribute_dic['lens_y_size'] = '1.0'

        front = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw, width=img_size,
                             height=img_size, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
        right = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw + 90, width=img_size,
                             height=img_size, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
        rear = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw + 180, width=img_size,
                            height=img_size, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
        left = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw - 90, width=img_size,
                            height=img_size, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
        up = self.set_cam(x, y, z, roll=roll, pitch=pitch + 90, yaw=yaw, width=img_size,
                          height=img_size, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
        down = self.set_cam(x, y, z, roll=roll, pitch=pitch - 90, yaw=yaw, width=img_size,
                            height=img_size, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)

        return front, rear, right, left, up, down

    def set_cam_cubemap_hdr(self, x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0, img_size=1080, attach_to=None, margin_pix=0, disable_rear_cam=False, harf_size=False):
        '''fov90のカメラを6台設置してcubemap画像を作成する'''
        '''さらに各カメラシャッタースピード10枚分取得してHDR画像を生成する'''
        '''front, rear, right, left, up, downの順でHDR向けに10個CAMERAを設置してリストを返す'''
        '''enable_rear_cam=Falseにする場合、front, right, left, up, downで返す'''
        '''marginを有効にするとマージンだけ大きい画像が取得されるので注意'''

        fov_h = 90.0

        # 少し大きくとることで結合部を自然にする
        if margin_pix != 0:
            img_width = img_size
            focal = img_size / (2.0 * math.tan(math.radians(fov_h / 2)))
            fov_h = math.degrees(2 * math.atan((img_width + margin_pix * 2) / 2 / focal))
            img_size = img_size + margin_pix * 2

        # 複数カメラの設定をそろえる
        # iso  ：実機センサの感度に合わせて取得したいダイナミックレンジに合わせる
        # fstop：実機カメラで用いる最小絞り値に合わせる
        # gamma：どんな値でも良い。デフォルトの2.2でOK
        attribute_dic = {}
        attribute_dic['bloom_intensity'] = '0.0'
        attribute_dic['fstop'] = '1.4'
        attribute_dic['iso'] = '1600.0'  # カメラ間の境界低減に若干効果があったように見える
        attribute_dic['gamma'] = '2.2'
        attribute_dic['lens_flare_intensity'] = '0.0'
        # attribute_dic['shutter_speed'] = str(shutter_speed)  # カメラ間の境界低減に若干効果があったように見える
        attribute_dic['exposure_mode'] = 'manual'
        attribute_dic['motion_blur_intensity'] = '0.0'
        attribute_dic['white_clip'] = '0.0'  # カメラ間の境界低減に若干効果があったように見える
        # attribute_dic['enable_postprocess_effects'] = 'False'
        attribute_dic['lens_circle_falloff'] = '10.0'
        # attribute_dic['lens_x_size'] = '1.0'
        # attribute_dic['lens_y_size'] = '1.0'

        sensor = 'sensor.camera.rgb'
        # 10 camera
        shutter_speed_ary = [20, 125, 500, 2000, 10000, 50000, 100000, 200000, 500000, 1000000]

        # front, rear, right, left, up, down
        yaw_cm = [0, 180, 90, -90, 0, 0]
        pitch_cm = [0, 0, 0, 0, 90, -90]
        cube_cam_num = 6
        if disable_rear_cam:
            # front, right, left, up, down
            yaw_cm = [0, 90, -90, 0, 0]
            pitch_cm = [0, 0, 0, 90, -90]
            cube_cam_num = 5

        print("set cam...")
        cam_list = []
        for i in range(cube_cam_num):
            for shutter_speed in shutter_speed_ary:
                attribute_dic['shutter_speed'] = str(shutter_speed)
                cw = img_size
                if harf_size and 0 < i:
                    cw = cw // 2
                cam = self.set_cam(x, y, z, roll=roll, pitch=pitch + pitch_cm[i], yaw=yaw + yaw_cm[i], width=cw,
                                   height=cw, fov_h=fov_h, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
                cam_list.append(cam)
        print("end")

        return cam_list

    def cubemap_concat(self, front, rear, right, left, up, down, margin_pix=0, cubemode="line_v", is_hdr=False):
        '''モードに応じたcubemap形式を作成、cross_hの例
            [[blank, up, blank, blank],
            [left, front, right, rear],
            [blank, down, blank, blank]]'''
        h, w, _ = front.shape
        if is_hdr:
            image_bit = np.float32
        else:
            image_bit = np.uint8
        blank = np.zeros((h, w, 3), image_bit)
        im_ary = []
        for frame in front, rear, right, left, up, down, blank:
            im_ary.append(frame)

        if margin_pix != 0:
            for i in range(len(im_ary)):
                im_ary[i] = im_ary[i][margin_pix:(h - margin_pix), margin_pix:(w - margin_pix)]

        if cubemode == "cross_h":
            # cubemap tile
            im_list_2d = [[im_ary[6], im_ary[4], im_ary[6], im_ary[6]],
                          [im_ary[3], im_ary[0], im_ary[2], im_ary[1]],
                          [im_ary[6], im_ary[5], im_ary[6], im_ary[6]]]
            cubemap = cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])
        elif cubemode == "line_h":
            cubemap = cv2.hconcat([im_ary[2], im_ary[3], im_ary[4], im_ary[5], im_ary[0], im_ary[1]])
        elif cubemode == "line_v":
            # right, left, up, down, front, rear
            cubemap = cv2.vconcat([im_ary[2], im_ary[3], im_ary[4], im_ary[5], im_ary[0], im_ary[1]])
        else:
            raise Exception("param error")

        return cubemap

    def set_cam_3side(self, x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0, fov_h=60.0, shutter_speed=200.0,
                      width=1920, height=1080, attach_to=None, margin_pix=0, sensor='sensor.camera.rgb'):
        '''カメラを3台設置してcubemap画像を作成する'''
        '''left, front, right'''
        '''marginを有効にするとマージンだけ大きい画像が取得されるので注意'''

        fov_h_margin = fov_h

        # 少し大きくとることで結合部を自然にする
        if margin_pix != 0:
            img_width = width
            focal = width / (2.0 * math.tan(math.radians(fov_h / 2)))
            fov_h_margin = math.degrees(2 * math.atan((img_width + margin_pix * 2) / 2 / focal))
            width = width + margin_pix * 2

        # 複数カメラの設定をそろえる
        attribute_dic = {}
        attribute_dic['exposure_mode'] = 'manual'
        attribute_dic['fstop'] = '1.4'
        attribute_dic['iso'] = '100.0'
        attribute_dic['gamma'] = '2.2'
        attribute_dic['shutter_speed'] = str(shutter_speed)
        attribute_dic['bloom_intensity'] = '0.0'
        attribute_dic['lens_flare_intensity'] = '0.0'
        attribute_dic['motion_blur_intensity'] = '0.0'

        front = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw, width=width,
                             height=height, fov_h=fov_h_margin, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
        right = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw + fov_h, width=width,
                             height=height, fov_h=fov_h_margin, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
        left = self.set_cam(x, y, z, roll=roll, pitch=pitch, yaw=yaw - fov_h, width=width,
                            height=height, fov_h=fov_h_margin, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)

        return left, front, right

    # def set_cam_cubemap_hdr(self, x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0, img_size=1080, attach_to=None, margin_pix=0, disable_rear_cam=False, harf_size=False):
    def set_cam_3side_hdr(self, x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0, fov_h=60.0,
                          width=1920, height=1080, attach_to=None, margin_pix=0):
        '''fov90のカメラを6台設置してcubemap画像を作成する'''
        '''さらに各カメラシャッタースピード10枚分取得してHDR画像を生成する'''
        '''front, rear, right, left, up, downの順でHDR向けに10個CAMERAを設置してリストを返す'''
        '''enable_rear_cam=Falseにする場合、front, right, left, up, downで返す'''
        '''marginを有効にするとマージンだけ大きい画像が取得されるので注意'''

        fov_h_margin = fov_h

        # 少し大きくとることで結合部を自然にする
        if margin_pix != 0:
            img_width = width
            focal = width / (2.0 * math.tan(math.radians(fov_h / 2)))
            fov_h_margin = math.degrees(2 * math.atan((img_width + margin_pix * 2) / 2 / focal))
            width = width + margin_pix * 2

        # 複数カメラの設定をそろえる
        attribute_dic = {}
        attribute_dic['exposure_mode'] = 'manual'
        attribute_dic['fstop'] = '1.4'
        attribute_dic['iso'] = '1600.0'
        attribute_dic['gamma'] = '2.2'
        # attribute_dic['shutter_speed'] = str(shutter_speed)
        attribute_dic['bloom_intensity'] = '0.0'
        attribute_dic['lens_flare_intensity'] = '0.0'
        attribute_dic['motion_blur_intensity'] = '0.0'

        # # 複数カメラの設定をそろえる
        # # iso  ：実機センサの感度に合わせて取得したいダイナミックレンジに合わせる
        # # fstop：実機カメラで用いる最小絞り値に合わせる
        # # gamma：どんな値でも良い。デフォルトの2.2でOK
        # attribute_dic = {}
        # attribute_dic['bloom_intensity'] = '0.0'
        # attribute_dic['fstop'] = '1.4'
        # attribute_dic['iso'] = '1600.0'  # カメラ間の境界低減に若干効果があったように見える
        # attribute_dic['gamma'] = '2.2'
        # attribute_dic['lens_flare_intensity'] = '0.0'
        # # attribute_dic['shutter_speed'] = str(shutter_speed)  # カメラ間の境界低減に若干効果があったように見える
        # attribute_dic['exposure_mode'] = 'manual'
        # attribute_dic['motion_blur_intensity'] = '0.0'
        # attribute_dic['white_clip'] = '0.0'  # カメラ間の境界低減に若干効果があったように見える
        # # attribute_dic['enable_postprocess_effects'] = 'False'
        # attribute_dic['lens_circle_falloff'] = '10.0'
        # # attribute_dic['lens_x_size'] = '1.0'
        # # attribute_dic['lens_y_size'] = '1.0'

        sensor = 'sensor.camera.rgb'
        # 10 camera
        shutter_speed_ary = [20, 125, 500, 2000, 10000, 50000, 100000, 200000, 500000, 1000000]

        # left, front, right
        yaw_cm = [-fov_h, 0, fov_h]
        # pitch_cm = [0, 0, 0, 0, 90, -90]
        cam_num = 3

        print("set cam...")
        cam_list = []
        for i in range(cam_num):
            for shutter_speed in shutter_speed_ary:
                attribute_dic['shutter_speed'] = str(shutter_speed)
                cam = self.set_cam(x, y, z, roll, pitch, yaw=yaw + yaw_cm[i], width=width, height=height,
                                   fov_h=fov_h_margin, attach_to=attach_to, sensor=sensor, attribute_dic=attribute_dic)
                cam_list.append(cam)
        print("end")

        return cam_list

    def destroy(self):
        '''このクラスで生成したアクターのみ削除'''
        for actor in self.actor_list:
            actor.destroy()
        self.actor_list = []
        for actor in self.vehicle_list:
            actor.destroy()
        self.actor_list = []
        for actor in self.sensor_list:
            actor.destroy()
        self.actor_list = []
        self.vehicle_list = []
        self.sensor_list = []

    def __del__(self):
        self.destroy()


def test():
    cutil = CarlaUtil()
    # cutil.set_spectator(0, 0, 0, 0, 0, 0)
    cutil.spawn_car_pos(0, 0, 100)

    time.sleep(5)
    cutil.destroy()


if __name__ == "__main__":
    test()


import random
import datetime
import os
import cv2
import json
import argparse
from tqdm import tqdm
import carla

from carla_util import CarlaUtil
from carla_util import CarlaSyncMode


def main(args):
    try:
        util = CarlaUtil()
        world = util.client.get_world()
        blueprint_library = world.get_blueprint_library()

        with open(args.file_json, 'r') as file:
            json_data = json.load(file)
            print(f"Open {args.file_json}")
        util.set_map(json_data['map'], force=False)
        total_frame = len(json_data['frames'])

        util.set_weather_val(10, 0, 0, 0, 250, 90, 10, 60, 0, 0)

        # vehicles first spawn
        frame = json_data['frames'][args.start_frame]
        ego_idx = 0
        for i, obj in enumerate(frame['objects']):
            if int(obj['objectId']) == args.cam_car_id:
                # 指定のIDの車両にカメラを設定、一致しない場合先頭車両に設置
                ego_idx = i
            obj_type = str(obj['object_type'])
            bp = random.choice(blueprint_library.filter(obj_type))
            x = float(obj['x'])
            y = float(obj['y'])
            z = float(obj['z'])
            r = int(obj['color_r'])
            g = int(obj['color_g'])
            b = int(obj['color_b'])
            yaw = float(obj['yaw'])
            pitch = float(obj['pitch'])
            roll = float(obj['roll'])
            if 0 <= r and 0 <= g and 0 <= b:
                bp.set_attribute('color', f"{r},{g},{b}")
            tf = carla.Transform(carla.Location(x=x, y=y, z=z + 2))  # コリジョンしない位置にスポーン
            vehicle = world.spawn_actor(bp, tf)
            vehicle.set_simulate_physics(False)
            tf = carla.Transform(carla.Location(x=x, y=y, z=z), carla.Rotation(roll=roll, pitch=pitch, yaw=yaw))
            vehicle.set_transform(tf)
            util.vehicle_list.append(vehicle)
            # util.actor_list.append(vehicle)

        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = args.out_folder + "/" + now_str
        os.makedirs(out_folder, exist_ok=True)

        # set_sensor
        sensors = []
        sensors.append(util.set_cam(args.cam_x, args.cam_x, args.cam_x, attach_to=util.vehicle_list[ego_idx]))

        with CarlaSyncMode(world, *sensors, fps=args.fps) as sync_mode:
            for frame_num in tqdm(range(total_frame)):
                if frame_num < args.start_frame:
                    continue
                if args.end_frame is not None and args.end_frame < frame_num:
                    break

                datas = sync_mode.tick(timeout=180.0)
                del datas[0]  # 0 is world snapshot

                img_list = []
                for data in datas:
                    img_list.append(util.render_image(data))

                dst = img_list[0]
                # cv2.imwrite(f"{out_folder}/rgb_{frame_num:06}.png", dst)
                cv2.imshow("img", dst)

                if cv2.waitKey(1) == 27:
                    break

                # Choose the next waypoint and update the car location.
                frame = json_data['frames'][frame_num]
                for j, obj in enumerate(frame['objects']):
                    x = float(obj['x'])
                    y = float(obj['y'])
                    z = float(obj['z'])
                    yaw = float(obj['yaw'])
                    pitch = float(obj['pitch'])
                    roll = float(obj['roll'])
                    tf = carla.Transform(carla.Location(x=x, y=y, z=z), carla.Rotation(roll=roll, pitch=pitch, yaw=yaw))
                    util.vehicle_list[j].set_transform(tf)

    finally:
        print('destroying actors.')
        util.destroy()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-f', '--file_json',
        default="out.json",
        help='scenario json filename (hoge.json)')
    argparser.add_argument(
        '-o', '--out_folder',
        default=r"E:\\dataset\\cube",
        help='output file folder')
    argparser.add_argument(
        '-c', '--cam_car_id',
        default="-1", type=int,
        help='camera set vehicle id')
    argparser.add_argument(
        '--fps',
        default="30.0", type=float,
        help='capture fps default="30.0"')
    argparser.add_argument(
        '-s', '--start_frame',
        default="0", type=int,
        help='start frame default="0"')
    argparser.add_argument(
        '-e', '--end_frame',
        type=int,
        help='end frame')
    argparser.add_argument(
        '-x', '--cam_x',
        default="2.2", type=float,
        help='camera pos x')
    argparser.add_argument(
        '-y', '--cam_y',
        default="0.0", type=float,
        help='camera pos y')
    argparser.add_argument(
        '-z', '--cam_z',
        default="1.4", type=float,
        help='camera pos z')
    args = argparser.parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
