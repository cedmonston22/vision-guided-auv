import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy
from sensor_msgs.msg import Image
import numpy as np
import cv2
from gz.transport13 import Node as GzNode
from gz.msgs10.pose_v_pb2 import Pose_V

TOPIC = "/world/default/model/x500_mono_cam_down_0/link/camera_link/sensor/camera/image"

QOS = QoSProfile(
    depth=1,
    history=HistoryPolicy.KEEP_LAST,
    reliability=ReliabilityPolicy.RELIABLE,
)

ARUCO_DICT = cv2.aruco.DICT_4X4_50
POSE_TOPIC = "/world/default/pose/info"
MODEL_NAME = "x500_mono_cam_down_0"

class MarkerDetector(Node):
    def __init__(self):
        super().__init__("marker_detector")
        dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(dictionary, params)
        self.create_subscription(Image, TOPIC, self.on_frame, QOS)
        self.altitude = None
        self.gz = GzNode()
        self.gz.subscribe(Pose_V, POSE_TOPIC, self.on_pose)
        
    def on_frame(self, msg):
        frame = np.frombuffer(msg.data, dtype = np.uint8).reshape(msg.height, msg.width, 3)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(bgr, corners, ids)
            center = corners[0][0].mean(axis=0)
            err_x = center[0] - msg.width / 2
            err_y = center[1] - msg.height / 2
            alt = self.altitude
            alt_s = f"{alt:.2f}" if alt is not None else "?"
            self.get_logger().info(f"alt={alt_s}m err_x={err_x:+.1f} err_y={err_y:+.1f}")
        cv2.imshow("detect", bgr)
        cv2.waitKey(1)

    def on_pose(self, msg):
        for pose in msg.pose:
            if pose.name == MODEL_NAME:
                self.altitude = pose.position.z
                return
                
                
                
def main():
    rclpy.init()
    node = MarkerDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()
 

if __name__ == "__main__":
    main()