#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from visualization_msgs.msg import MarkerArray, Marker
from xml.etree.ElementTree import Element, SubElement, ElementTree
import gpxpy

# http://docs.ros.org/en/fuerte/api/rviz/html/marker__array__test_8py_source.html
# https://github.com/tkrajina/gpxpy
# https://aotoshiro.jpn.org/2021/2376

def make_gpx(msg):
    gpx_file_w = open('sample_timefix.gpx', 'w')
    gpx = gpxpy.gpx.GPX()
    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Create points:
    for marker in msg.markers:
        x = marker.pose.position.x
        y = marker.pose.position.y
        ele = marker.pose.position.z
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(x, y, elevation=ele))

    gpx_file_w.write(gpx.to_xml())
    gpx_file_w.close()


def callback(msg):
    for marker in msg.markers:
        print(marker.pose.position.x)
        print(marker.pose.position.y)
        print(marker.pose.position.z)
    # rospy.loginfo("Message '{}' recieved".format(msg.markers[0]))


def subscriber():
    rospy.init_node("waypoints_subsc")
    rospy.Subscriber("/global_waypoints_rviz", MarkerArray, make_gpx)
    rospy.spin()

def subscriber_once():
    t = rospy.wait_for_message("/global_waypoints_rviz", MarkerArray)
    print(t)
    # rospy.init_node("waypoints_subsc")
    # rospy.Subscriber("/global_waypoints_rviz", MarkerArray, callback)
    # rospy.spin()



if __name__ == "__main__":
    # subscriber_once()
    subscriber()