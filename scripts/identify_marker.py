import cv2
from pathlib import Path

MARKER = Path.home() / "PX4-Autopilot/Tools/simulation/gz/models/arucotag/arucotag.png"

def main():
    img = cv2.imread(str(MARKER), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise SystemExit(f"Could not read {MARKER}")
    
    print(img.shape)
    
    padded = cv2.copyMakeBorder(img,50,50,50,50,
                                cv2.BORDER_CONSTANT, value = 255)
    
    params = cv2.aruco.DetectorParameters()
    names = [n for n in dir(cv2.aruco) if n.startswith("DICT_")]
    
    for name in names:
        dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco,name))
        detector = cv2.aruco.ArucoDetector(dictionary, params)
        corners, ids, _ = detector.detectMarkers(padded)
        if ids is not None:
            print(f"{name}: {ids.flatten().tolist()}")

if __name__ == "__main__":
    main()