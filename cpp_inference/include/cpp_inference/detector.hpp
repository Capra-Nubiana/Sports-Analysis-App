#pragma once

#include <string>
#include <vector>
#include <opencv2/opencv.hpp>

namespace sports_analysis {

struct Detection {
    float x1, y1, x2, y2;
    int class_id;
    float confidence;
};

class Detector {
public:
    explicit Detector(const std::string& model_path);
    bool load();
    std::vector<Detection> detect(const cv::Mat& frame);

private:
    std::string model_path_;
    // TODO: ONNX Runtime / TensorRT session
};

}  // namespace sports_analysis
