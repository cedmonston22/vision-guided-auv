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

class CameraView(Node):
    def __init__(self):
        super().__init__("camera_view")
        self.create_subscription(Image, TOPIC, self.on_frame, QOS)

    def on_frame(self,msg):
        frame = np.frombuffer(msg.data, dtype =np.uint8).reshape(msg.height, msg.width, 3)
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("camera", bgr)
        cv2.waitKey(1)
            
        
        
def main():
    rclpy.init()
    node = CameraView()
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