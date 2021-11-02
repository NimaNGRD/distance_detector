
##############################################
##          Distance Detector Demo          ##
##############################################

import pyrealsense2 as rs
import numpy as np
import cv2

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))
print('Series of the camera: ' + device_product_line)

# Start streaming
pipeline.start(config)

try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap & greyscale on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.08), cv2.COLORMAP_JET)
        depth_greyscale = cv2.cvtColor(cv2.convertScaleAbs(depth_image, alpha=0.08), cv2.COLOR_GRAY2BGR)

        # Show distance for the center point
        point = (320, 240)
        distance = depth_image[point[1], point[0]]
        distance2 = depth_colormap[point[1], point[0]]
        cv2.circle(color_image, point, 4, (0, 2*(int(distance2[0] - 128)), 255 - 2*(int(distance2[0] - 128))))
        cv2.putText(color_image, "{}mm".format(distance), (point[0], point[1] - 5), cv2.FONT_HERSHEY_PLAIN, 1, (0, 2*(int(distance2[0] - 128)), 255 - 2*(int(distance2[0] - 128))), 1)

        # Stack both images horizontally
        images = np.hstack((depth_colormap, color_image, depth_greyscale))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        key = cv2.waitKey(1)

        # Interrupt by pressing the 'n' button
        if key == 110:
            break

finally:

    # Stop streaming
    pipeline.stop()