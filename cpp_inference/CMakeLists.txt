"""
C++ Inference Engine (CMake configuration)

This module provides a CMakeLists.txt for building the C++ inference
engine that wraps ONNX Runtime or TensorRT for low-latency inference.
"""

cmake_minimum_required(VERSION 3.18)
project(sports_analysis_cpp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenCV
find_package(OpenCV REQUIRED)

# Include directories
include_directories(
    ${OpenCV_LIBS}
    include
)

# Source files
file(GLOB_RECURSE SOURCES "src/*.cpp")

# Create shared library
add_library(sports_analysis_cpp SHARED ${SOURCES})

# Link OpenCV
target_link_libraries(sports_analysis_cpp ${OpenCV_LIBS})

# TODO: Link ONNX Runtime or TensorRT
# find_package(ONNXRuntime REQUIRED)
# target_link_libraries(sports_analysis_cpp onnxruntime)

# TODO: Link TensorRT
# find_package(TensorRT REQUIRED)
# target_link_libraries(sports_analysis_cpp TensorRT::TensorRT)

# Compiler optimizations
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_options(sports_analysis_cpp PRIVATE -O3 -march=native)
endif()
