import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy
from sensor_msgs.msg import Image
import numpy as np
import cv2

TOPIC = "/world/default/model/x500_mono_cam_down_0/link/camera_link/sensor/camera/image"

QOS = QoSProfile(
    depth=1,
    history=HistoryPolicy.KEEP_LAST,
    reliability=ReliabilityPolicy.RELIABLE,
)

ARUCO_DICT = cv2.aruco.DICT_4X4_50

class MarkerDetector(Node):
    def __init__(self):
        super().__init__("marker_detector")
        dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(dictionary, params)
        self.create_subscription(Image, TOPIC, self.on_frame, QOS)
        
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
            self.get_logger().info(f"err_x={err_x:+.1f} err_y={err_y:+.1f}")
        cv2.imshow("detect", bgr)
        cv2.waitKey(1)
                
                
                
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