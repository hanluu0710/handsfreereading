"""
Callibrartion stage program.

1. Inform the user that calibration is beginning and provide four seconds to prepare.
2. Instruct the user to look toward the center of the book. Allow two seconds for adjustment and record the normalized eye position for three seconds.
3. Instruct the user to look toward a comfortable point beyond the book's upper-right corner. Allow two seconds for adjustment and record for three seconds.
4. Repeat the procedure for the upper-left gaze position.
5. Validate that the three recorded gaze regions can be reliabley distinguished. If validation fails, repeat calibration.
6. Inform the user that calibration is complete.
7. Permit recalibration using the calibration button whenever the mechanism is safely idle.
"""

import sys
import time
import cv2
from picamera2 import Picamera2

from gaze_tracking import GazeTracking

def display_instruction(frame, text):
	"""Use for displaying text on the video frame user sees."""
	cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

def record_position(region, gaze, camera):
	"""
	Parameters:
	region: Center/Left/Right
	frame: video output still on which text will be displayed
	gaze: object of gaze-tracking module
	Outputs:
	x: x-coordinate of recorded eye position
	y: y-coordinate of recorded eye position
	
	Function:
	1. Instruct the user to look toward the center of the book. 
	2. Allow two seconds for adjustment. 
	3. Record the average eye position for next three seconds.
	"""
	duration = 2 #duration of allowing user to adjust their eyesight
	
	end_time = time.monotonic() + duration
	
	while time.monotonic() < end_time:
		frame = camera.capture_array()
		text = f"Look towards {region} of the book."
		display_instruction(frame, text)
		cv2.imshow("Adjustment period.", frame)
	
	duration = 3 #duration of recording eye position
	
	end_time = time.monotonic() + duration
	
	count = 0 #number of times valid positions are recorded
	
	running_sum_left_pupil_x = 0
    running_sum_left_pupil_y = 0
    running_sum_right_pupil_x = 0
    running_sum_right_pupil_y = 0
	
	while time.monotonic() < end_time:
		frame = camera.capture_array()
		# We send this frame to GazeTracking to analyze it
		gaze.refresh(frame)

		frame = gaze.annotated_frame()
		text = ""
		
		if gaze.is_blinking():
			text = "Blinking."
		else:
			text = f"Keep looking towards the {region}."
			left_pupil = gaze.pupil_left_coords()
			right_pupil = gaze.pupil_right_coords()
			
			running_sum_left_pupil_x += left_pupil[0]
			running_sum_left_pupil_y += left_pupil[1]
			running_sum_right_pupil_x += right_pupil[0]
			running_sum_right_pupil_y += right_pupil[1]
			
			count += 1
			
		display_instruction(frame, text)	
		cv2.imshow("Demo", frame)
		time.sleep(0.01) #capture position every 0.01 seconds
		
	avg_left_pupil_x = running_sum_left_pupil_x/count
	avg_left_pupil_y = running_sum_left_pupil_y/count
	avg_right_pupil_x = running_sum_right_pupil_x/count
	avg_right_pupil_y = running_sum_right_pupil_y/count
	
	return (avg_left_pupil_x, avg_left_pupil_y), (avg_right_pupil_x, avg_right_pupil_y)
	

gaze = GazeTracking()
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

center_left_coords, center_right_coords = record_position("center", gaze, picam2)
left_left_coords, left_right_coords = record_position("left", gaze, picam2)
right_left_coords, right_right_coords = record_position("right", gaze, picam2)

picam2.stop()
cv2.destroyAllWindows()

print(f"center_left_coords = {center_left_coords}, center_right_coords = {center_right_coords}.")
print(f"left_left_coords = {left_left_coords}, left_right_coords = {left_right_coords}.")
print(f"right_left_coords = {right_left_coords}, right_right_coords = {right_right_coords}.")
