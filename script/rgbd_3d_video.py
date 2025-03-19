import sys
import time
from datetime import datetime
from glob import glob
import argparse

from tqdm import tqdm
import open3d as o3d
import numpy as np
import cv2


def deg2rad(degrees):
    """Convert degrees to radians."""
    return np.deg2rad(degrees)


def get_rotation_matrix(roll, pitch, yaw):
    """
    Calculate the rotation matrix from roll, pitch, and yaw angles.

    Args:
        roll (float): Roll angle in degrees.
        pitch (float): Pitch angle in degrees.
        yaw (float): Yaw angle in degrees.

    Returns:
        np.ndarray: 3x3 rotation matrix.
    """
    # Convert angles to radians
    roll = deg2rad(roll)
    pitch = deg2rad(pitch)
    yaw = deg2rad(yaw)

    # Rotation matrices around x, y, and z axes
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])

    R_y = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    R_z = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])

    # Combined rotation matrix (Rz * Ry * Rx)
    R = R_z @ R_y @ R_x
    return R


def get_extrinsic_matrix(position, rotation):
    """
    Calculate the extrinsic matrix from position and rotation.

    Args:
        position (tuple): (x, y, z) position in centimeters.
        rotation (tuple): (roll, pitch, yaw) rotation in degrees.

    Returns:
        np.ndarray: 4x4 extrinsic transformation matrix.
    """
    # Extract position and convert to meters
    x, y, z = np.array(position) / 100.0  # Convert cm to m

    # Get the rotation matrix
    R = get_rotation_matrix(*rotation)

    # Combine rotation and translation into a 4x4 matrix
    extrinsic = np.eye(4)
    extrinsic[:3, :3] = R
    extrinsic[:3, 3] = [x, y, z]

    return extrinsic


class Viewer3D:
    """Open3Dを利用した3Dビューアークラス"""

    def __init__(self) -> None:
        self.vis = o3d.visualization.Visualizer()

        self.vis.create_window("3d viewer", width=640, height=480)

        # if "background_color" in viewer_3d_setting:
        #     render_option = self.vis.get_render_option()
        #     render_option.background_color = viewer_3d_setting["background_color"]

        self.pcd = o3d.geometry.PointCloud()
        self.lineset = o3d.geometry.LineSet()
        self.geom_added = False
        self.vis.add_geometry(self.gen_grid(1000, 3))
        self.vis.add_geometry(self.gen_circle(1000))
        self.vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=500))

    def add_mesh(self, filepath):
        pati_mesh = o3d.io.read_triangle_mesh(filepath)
        self.vis.add_geometry(pati_mesh)

    def update_pcd(self, vertices: list[tuple[float, float, float]]):
        self.pcd.points = o3d.utility.Vector3dVector(vertices)

    def update_lineset_from_2points(self, pt_min: tuple[float, float, float],
                                    pt_max: tuple[float, float, float],
                                    line_color: tuple[float, float, float] = (1, 0, 0)):
        vertices = [
            # top surface
            (pt_max[0], pt_max[1], pt_max[2]),  # pt_max
            (pt_min[0], pt_max[1], pt_max[2]),
            (pt_min[0], pt_min[1], pt_max[2]),
            (pt_max[0], pt_min[1], pt_max[2]),
            # bottom surface
            (pt_max[0], pt_max[1], pt_min[2]),
            (pt_min[0], pt_max[1], pt_min[2]),
            (pt_min[0], pt_min[1], pt_min[2]),  # pt_min
            (pt_max[0], pt_min[1], pt_min[2]),
        ]

        lines = np.array([[0, 1],
                          [1, 2],
                          [2, 3],
                          [3, 0],
                          [4, 5],
                          [5, 6],
                          [6, 7],
                          [7, 4],
                          [0, 4],
                          [1, 5],
                          [2, 6],
                          [3, 7],])

        self.lineset.points = o3d.utility.Vector3dVector(vertices)
        self.lineset.lines = o3d.utility.Vector2iVector(lines)
        self.lineset.paint_uniform_color(line_color)

    def render(self):
        if not self.geom_added:
            self.vis.add_geometry(self.pcd)
            self.vis.add_geometry(self.lineset)
            self.geom_added = True
        self.vis.update_geometry(self.pcd)
        self.vis.update_geometry(self.lineset)
        self.vis.poll_events()
        self.vis.update_renderer()

    @staticmethod
    def gen_grid(pitch: float, length: int) -> o3d.geometry.LineSet:
        line_set = o3d.geometry.LineSet()
        max_value = length * pitch
        x = np.arange(-max_value, max_value + pitch, pitch)
        x = np.repeat(x, 2)
        y = np.full_like(x, -max_value)
        y[::2] = max_value
        z = np.zeros_like(x)
        points_Y = np.vstack((x, y, z)).T

        y = np.arange(-max_value, max_value + pitch, pitch)
        y = np.repeat(y, 2)
        x = np.full_like(y, -max_value)
        x[::2] = max_value
        z = np.zeros_like(y)
        points_X = np.vstack((x, y, z)).T

        points = np.vstack((points_X, points_Y))
        line_set.points = o3d.utility.Vector3dVector(points)
        lines = np.arange(points.shape[0]).reshape(-1, 2)
        line_set.lines = o3d.utility.Vector2iVector(lines)

        line_set.paint_uniform_color((0.5, 0.5, 0.5))

        return line_set

    @staticmethod
    def gen_circle(r: float, points: int = 100) -> o3d.geometry.LineSet:
        theta = np.linspace(0, 2 * np.pi, points)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.zeros_like(x)

        points = np.vstack((x, y, z)).T
        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(points)
        lines = np.zeros((points.shape[0] - 1, 2), dtype=int)
        lines[:, 0] = np.arange(points.shape[0] - 1)
        lines[:, 1] = np.arange(points.shape[0] - 1) + 1
        line_set.lines = o3d.utility.Vector2iVector(lines)

        line_set.paint_uniform_color((0.5, 0.5, 0.5))

        return line_set


class DepthImage:
    """Class to handle depth image to point cloud conversion with external parameters."""

    def __init__(self, fov_h, extrinsic=None):
        """
        Initialize DepthImage with horizontal FOV and optional extrinsic parameters.

        Args:
            fov_h (float): Horizontal field of view in degrees.
            extrinsic (np.ndarray): 4x4 transformation matrix for external parameters (default: identity matrix).
        """
        self.camera_intrinsic = None
        self.fov_h = fov_h
        # Set extrinsic parameters (external transformation matrix), default to identity matrix if not provided
        self.extrinsic = extrinsic if extrinsic is not None else np.eye(4)

    def set_extrinsic(self, extrinsic):
        """
        Set the external transformation matrix.

        Args:
            extrinsic (np.ndarray): 4x4 transformation matrix.
        """
        if extrinsic.shape == (4, 4):
            self.extrinsic = extrinsic
        else:
            raise ValueError("Extrinsic matrix must be a 4x4 transformation matrix.")

    def rgbd2pcd(self, color, depth):
        """
        Convert RGB and Depth images to a Point Cloud.

        Args:
            color (np.ndarray): RGB image as a NumPy array.
            depth (np.ndarray): Depth image as a NumPy array.

        Returns:
            o3d.geometry.PointCloud: Generated point cloud from the RGBD image.
        """
        if self.camera_intrinsic is None:
            h, w = color.shape[:2]
            fx = w / 2 / np.tan(np.deg2rad(self.fov_h / 2))
            fov_v = 2 * np.rad2deg(np.arctan((h / w) * np.tan(np.deg2rad(self.fov_h / 2))))
            fy = h / 2 / np.tan(np.deg2rad(fov_v / 2))
            self.camera_intrinsic = o3d.camera.PinholeCameraIntrinsic(
                width=w, height=h, fx=fx, fy=fy, cx=w / 2, cy=h / 2)

        color_o3d = o3d.geometry.Image(color)
        depth_o3d = o3d.geometry.Image(depth.astype(np.float32))
        rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color_o3d, depth_o3d, convert_rgb_to_intensity=False)

        # Create point cloud using intrinsic and extrinsic parameters
        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, self.camera_intrinsic)
        # Apply the external transformation matrix (extrinsic)
        pcd.transform(self.extrinsic)
        # pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
        # pcd.transform([[-0.49999988, - 0.8660254, 0., 0.018],
        #                [0.83407996, - 0.48171522, - 0.26813374, 0.009],
        #                [0.22414387, - 0.12940952, 0.96592583, 0.016],
        #                [0., 0., 0., 1.]])

        return pcd


def depth_conv(src, thre_max=None):
    """Convert 8-bit 3-channel depth image to 1-channel meter depth."""
    in_meters = (src[:, :, 0] + src[:, :, 1] * 256.0 + src[:, :, 2] * 256.0 * 256.0) / 1000

    if thre_max is not None:
        in_meters = np.where(in_meters > thre_max, np.nan, in_meters)

    return in_meters


def unreal_to_open3d_rotation(roll, pitch, yaw):
    """
    Convert Unreal Engine roll, pitch, yaw to Open3D compatible rotation.

    Args:
        roll (float): Roll angle in degrees (rotation around X-axis).
        pitch (float): Pitch angle in degrees (rotation around Y-axis).
        yaw (float): Yaw angle in degrees (rotation around Z-axis).

    Returns:
        tuple: Converted roll, pitch, yaw suitable for Open3D.
    """
    # Convert to radians
    roll = deg2rad(roll)
    pitch = deg2rad(pitch)
    yaw = deg2rad(yaw)

    # Unreal to Open3D coordinate transformation
    # Convert rotation order from Unreal (Yaw-Pitch-Roll) to Open3D (Roll-Pitch-Yaw)
    R_unreal = get_rotation_matrix(0, -15, 120)

    # Apply axes swap and sign adjustments
    # (Y, Z, X in Unreal -> X, Y, Z in Open3D)
    # Apply additional rotation matrix for coordinate alignment
    R_align = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    R_open3d = R_align @ R_unreal

    return np.degrees(np.array((R_open3d)))


def rgbd_3d_video(rgb_path, depth_path):
    """Visualize 3D point cloud from RGB and Depth video."""
    vis = o3d.visualization.Visualizer()
    vis.create_window(
        window_name='Depth Image Visualization',
        width=800,
        height=600,
        left=480,
        top=270)
    vis.get_render_option().background_color = [0.05, 0.05, 0.05]
    vis.get_render_option().point_size = 1
    vis.get_render_option().show_coordinate_frame = True

    # viewer = Viewer3D()

    # Define camera position and rotation
    # position = (0.190, 0.350, 0.240)  # [cm]
    # rotation = (0, -15, 120)    # [degrees]
    rotation = unreal_to_open3d_rotation(0, -30, -120)    # [degrees]
    print("rotation")
    print(rotation)
    position = (0, 0, 0)  # [cm]
    # rotation = (0, 0, 0)    # [degrees]

    # Calculate extrinsic matrix
    extrinsic_matrix = get_extrinsic_matrix(position, rotation)
    print("Extrinsic Matrix:\n", extrinsic_matrix)

    pointcloud = o3d.geometry.PointCloud()
    depth_image = DepthImage(86, extrinsic=extrinsic_matrix)
    rgb_files = sorted(glob(rgb_path))
    depth_files = sorted(glob(depth_path))
    total_frame = len(rgb_files)

    if total_frame == 0:
        print("No frames found. Check the paths provided.")
        return

    count = 0
    pbar = tqdm(total=total_frame)
    while True:
        try:
            rgb = cv2.imread(rgb_files[count % total_frame])
            if rgb is None:
                print(f"Failed to load RGB image: {rgb_files[count % total_frame]}")
                break
            rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)

            depth_raw = cv2.imread(depth_files[count % total_frame])
            if depth_raw is None:
                print(f"Failed to load depth image: {depth_files[count % total_frame]}")
                break
            depth_raw = cv2.cvtColor(depth_raw, cv2.COLOR_BGR2RGB)
            depth_m = depth_conv(depth_raw, thre_max=100.0)

            pcd = depth_image.rgbd2pcd(rgb, depth_m)
            pointcloud.points = pcd.points
            pointcloud.colors = pcd.colors

            if count == 0:
                vis.add_geometry(Viewer3D.gen_grid(0.001, 3))
                vis.add_geometry(pointcloud)

            vis.update_geometry(pointcloud)
            vis.poll_events()
            vis.update_renderer()

            # viewer.update_pcd()

            cv2.imshow("RGB Image", rgb)
            key = cv2.waitKey(1)
            if key == 27:  # ESC key
                break
            elif key == ord("s"):
                cv2.waitKey(0)

            time.sleep(0.005)
            count += 1
            pbar.update(1)

        except Exception as e:
            print(f"Error occurred: {e}")
            break

    pbar.close()
    vis.destroy_window()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="3D Point Cloud Visualization from RGB and Depth Images")
    argparser.add_argument(
        '-i', '--in_rgb',
        default="dataset/rgb/*",
        help="Path to the RGB images.")
    argparser.add_argument(
        '-d', '--in_depth',
        default="dataset/depth/*",
        help="Path to the Depth images.")
    args = argparser.parse_args()

    rgbd_3d_video(args.in_rgb, args.in_depth)
    print('Done')
