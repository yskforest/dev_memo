import sys
from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args
from tf2_ros import TransformException, LookupException, ConnectivityException, ExtrapolationException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener


class Tf2Pose(Node):

    def __init__(self, args):
        super().__init__('tf2pose')
        self.target_frame = 'map'
        self.source_frame = 'base_link'

        if len(args) >= 3:
            self.target_frame = args[1]
            self.source_frame = args[2]
        if len(args) >= 2:
            self.target_frame = args[1]

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.publisher = self.create_publisher(PoseStamped, '/tf2pose', 10)
        timer_period = 1 / 30.0
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        try:
            when = rclpy.time.Time()
            trans = self.tf_buffer.lookup_transform(self.target_frame, self.source_frame, when)
        except TransformException as ex:
            self.get_logger().info(str(ex))
            return

        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.target_frame
        msg.pose.position.x = trans.transform.translation.x
        msg.pose.position.y = trans.transform.translation.y
        msg.pose.position.z = trans.transform.translation.z
        msg.pose.orientation.x = trans.transform.rotation.x
        msg.pose.orientation.y = trans.transform.rotation.y
        msg.pose.orientation.z = trans.transform.rotation.z
        msg.pose.orientation.w = trans.transform.rotation.w
        self.publisher.publish(msg)


if __name__ == '__main__':
    rclpy.init()
    node = Tf2Pose(remove_ros_args(args=sys.argv))
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()
