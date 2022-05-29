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
