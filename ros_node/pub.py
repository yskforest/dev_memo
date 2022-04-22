#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovarianceStamped
import numpy as np

def init_pose_pub():
    rospy.init_node("init_pose_pub")

    pose_pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size = 10)

    pose_test = PoseWithCovarianceStamped()
    pose_test.header.frame_id = 'world'
    pose_test.pose.pose.position.x = -1.1
    pose_test.pose.pose.position.y = -12.7
    pose_test.pose.pose.orientation.z = np.pi

    while not rospy.is_shutdown():

        pose_pub.publish(pose_test)

        rospy.sleep(0.2)

    # rospy.init_node("init_pose_pub")

    # pub = rospy.Publisher("chatter", String, queue_size=10)

    # rate = rospy.Rate(1)
    # while not rospy.is_shutdown():
    #     msg = "hello world {}".format(rospy.get_time())
    #     pub.publish(msg)
    #     # rospy.loginfo("Message '{}' published".format(msg))
    #     rate.sleep()


def main():
    rospy.init_node("publisher")

    pub = rospy.Publisher("chatter", String, queue_size=10)

    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        msg = "hello world {}".format(rospy.get_time())
        pub.publish(msg)
        # rospy.loginfo("Message '{}' published".format(msg))
        rate.sleep()


if __name__ == "__main__":
    init_pose_pub()