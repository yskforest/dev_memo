import sys
import time
from datetime import datetime
from glob import glob
import argparse

from tqdm import tqdm
import open3d as o3d
import numpy as np
import numpy as np
import open3d as o3d
import cv2


class DepthImage():
    def __init__(self, fov_h):
        self.camera_intrinsic = None
        self.fov_h = fov_h

    def rgbd2pcd(self, color, depth):
        if self.camera_intrinsic is None:
            h, w = color.shape[:2]
            fx = w / 2 / np.tan(np.deg2rad(self.fov_h / 2))
            fy = fx * h / w
            self.camera_intrinsic = o3d.camera.PinholeCameraIntrinsic(
                width=w, height=h, fx=fx, fy=fy, cx=w / 2, cy=h / 2)

        color = o3d.geometry.Image(color)
        depth = o3d.geometry.Image(depth.astype(np.float32))
        rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color, depth, convert_rgb_to_intensity=False)

        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, self.camera_intrinsic)
        pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
        return pcd


def depth_conv(src, thre_max=None):
    in_meters = (src[:, :, 0] + src[:, :, 1] * 256.0 + src[:, :, 2] * 256.0 * 256.0) / 1000

    if thre_max:
        in_meters = np.where(thre_max < in_meters, thre_max, in_meters)

    return in_meters


def rgbd_3d_video(rgb_path, depth_path):
    vis = o3d.visualization.Visualizer()
    vis.create_window(
        window_name='open3d depth image',
        width=960,
        height=540,
        left=480,
        top=270)
    vis.get_render_option().background_color = [0.05, 0.05, 0.05]
    vis.get_render_option().point_size = 1
    vis.get_render_option().show_coordinate_frame = True

    pointcloud = o3d.geometry.PointCloud()
    depth_image = DepthImage(90)
    rgb_files = sorted(glob(rgb_path))
    depth_files = sorted(glob(depth_path))
    total_frame = len(rgb_files)

    count = 0
    pbar = tqdm()
    while True:

        rgb = cv2.imread(rgb_files[count % total_frame])
        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)

        depth_raw = cv2.imread(depth_files[count % total_frame])
        depth_raw = cv2.cvtColor(depth_raw, cv2.COLOR_BGR2RGB)
        depth_m = depth_conv(depth_raw, thre_max=30.0)

        pcd = depth_image.rgbd2pcd(rgb, depth_m)
        pointcloud.points = pcd.points
        pointcloud.colors = pcd.colors

        if count == 0:
            vis.add_geometry(pointcloud)

        vis.update_geometry(pointcloud)

        vis.poll_events()
        vis.update_renderer()

        # # This can fix Open3D jittering issues:
        time.sleep(0.005)

        count += 1
        pbar.update()

    pbar.close()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-i', '--in_rgb',
        default="dataset/rgb/*")
    argparser.add_argument(
        '-d', '--in_depth',
        default="dataset/depth/*")
    args = argparser.parse_args()

    rgbd_3d_video(args.in_rgb, args.in_depth)
    print('Done')
