import os
import datetime
import pyrealsense2 as rs
import numpy as np
import cv2
from tqdm import tqdm


class RealSense:
    def __init__(self, width=1280, height=720, fps=30):
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = self.config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))
        print(f"device_product_line: {device_product_line}")

        found_rgb = False
        for sensor in device.sensors:
            if sensor.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            print("The demo requires Depth camera with Color sensor")
            exit(0)

        self.config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        align_to = rs.stream.color
        self.align = rs.align(align_to)

    def __del__(self):
        self.pipeline.stop()

    def start_streaming(self):
        profile = self.pipeline.start(self.config)
        depth_sensor = profile.get_device().first_depth_sensor()
        self.color_intrinsics = rs.video_stream_profile(profile.get_stream(rs.stream.color)).get_intrinsics()
        print(f"color_intrinsics: {self.color_intrinsics}")
        self.depth_scale = depth_sensor.get_depth_scale()
        print("Depth Scale is: ", self.depth_scale)

        self.clipping_distance_in_meters = 1
        self.clipping_distance = self.clipping_distance_in_meters / self.depth_scale

    def get_color_and_depth(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not aligned_depth_frame or not color_frame:
            return None, None

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        return color_image, depth_image


def realsense_viewer():
    realsense = RealSense(1280, 720)
    realsense.start_streaming()

    now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    output_dir = "out"
    folder = f"{output_dir}/img_{now_str}"
    frame_no = 0
    recording = False
    is_first_time = True

    tqdm_bar = tqdm()

    try:
        while True:
            color_image, depth_image = realsense.get_color_and_depth()

            if color_image is not None and depth_image is not None:
                cv2.imshow('color', color_image)
                key = cv2.waitKey(1)
                if key == 27:  # ESC key
                    break
                elif key == 32:  # Space key
                    print("toggle recording")
                    recording = not recording

                if recording:
                    if is_first_time:
                        os.makedirs(folder, exist_ok=True)
                        is_first_time = False
                    cv2.imwrite(f"{folder}/rgb_{frame_no:06}_color.png", color_image)
                    np.save(f"{folder}/depth_{frame_no:06}_depth.npy", depth_image)

                frame_no += 1
                tqdm_bar.update()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cv2.destroyAllWindows()
        del realsense


if __name__ == "__main__":
    realsense_viewer()
