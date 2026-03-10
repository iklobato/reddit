#!/usr/bin/env python3

"""
A simple script to verify that OpenCV is working correctly in the container.
This helps diagnose numpy and OpenCV compatibility issues.
"""

import sys

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    # Try to import numpy and print its version
    import numpy as np
    print(f"NumPy version: {np.__version__}")
except ImportError as e:
    print(f"Failed to import NumPy: {e}")
    sys.exit(1)

try:
    # Try to import OpenCV and print its version
    import cv2
    print(f"OpenCV version: {cv2.__version__}")
    
    # Try to create a simple matrix to confirm OpenCV is working
    test_matrix = np.zeros((10, 10, 3), dtype=np.uint8)
    test_result = cv2.cvtColor(test_matrix, cv2.COLOR_BGR2GRAY)
    print("Successfully performed OpenCV operation")
except ImportError as e:
    print(f"Failed to import OpenCV: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error using OpenCV: {e}")
    sys.exit(1)

print("OpenCV setup is working correctly")
sys.exit(0) 