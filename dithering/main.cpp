#include <iostream>
#include <string>
#include <array>
#include <opencv2/opencv.hpp>
#include <algorithm>
#include <cmath>
#include <tuple>

const std::array<cv::Vec3f, 7> cColors {
    cv::Vec3f(0,    0,      0),
    cv::Vec3f(1,    0,      0),
    cv::Vec3f(0,    1,      0),
    cv::Vec3f(0,    0,      1),
    cv::Vec3f(0,    0.5,    1),
    cv::Vec3f(0,    1,      1),
    cv::Vec3f(1,    1,      1),
};

std::tuple<int, int> getDirSpacing(int size, int maxSize) {
    if (size == maxSize)
        return std::make_tuple(0, 0);

    float space = float(maxSize - size) / 2.0f;
    return std::make_tuple(floor(space), ceil(space));
}

cv::Mat loadImg(cv::Size maxSize, std::string path) {
    cv::Mat img = cv::imread(path);
    int nCols = 1;
    int nRows = 1;

    if (img.rows > img.cols) {
        nRows = maxSize.height;
        nCols = std::clamp(img.cols * nRows / img.rows, 1, maxSize.width);

    } else {
        nCols = maxSize.width;
        nRows = std::clamp(img.rows * nCols / img.cols, 1, maxSize.height);
    }

    cv::resize(img, img, cv::Size(nCols, nRows));
    img.convertTo(img, CV_32FC3, 1/255.0);

    const auto [left, right] = getDirSpacing(img.cols, maxSize.width);
    const auto [top, bottom] = getDirSpacing(img.rows, maxSize.height);

    cv::Mat res = cv::Mat(maxSize, img.type());
    cv::copyMakeBorder(img, res, top, bottom, left, right, cv::BORDER_CONSTANT);
    return res;
}

cv::Vec3f getNewVal(cv::Vec3f oldVal) {
    return *std::min_element(std::begin(cColors), std::end(cColors), [oldVal](const cv::Vec3f &a, const cv::Vec3f &b){
        return cv::norm(oldVal, a) < cv::norm(oldVal, b);
    });
}

cv::Mat dither(cv::Mat img) {
    for (int y = 0; y < img.rows; y++) {
        for (int x = 0; x < img.cols; x++) {
            cv::Vec3f oldVal = img.at<cv::Vec3f>(y, x);
            img.at<cv::Vec3f>(y, x) = getNewVal(oldVal);

            cv::Vec3f err = oldVal - img.at<cv::Vec3f>(y, x);
            if (x < img.cols - 1) img.at<cv::Vec3f>(y, x+1) += err * 7 / 16;
            if (y < img.rows - 1) {
                img.at<cv::Vec3f>(y+1, x) += err * 5 / 16;
                if (x > 0) img.at<cv::Vec3f>(y+1, x-1) += err * 3 / 16;
                if (x < img.cols - 1) img.at<cv::Vec3f>(y+1, x+1) += err / 16;
            }
        }
    }

    return img;
}

int main(int argc, char* argv[]) {
    if (argc != 5) {
        printf("ERROR:\tBad number of arguments.\n\tPlease path to input image, path to where it should be saved and its desired max width and height\n");
        return 1;
    }

    try {
        std::string inputPath(argv[1]);
        std::string outputPath(argv[2]);
        int width = atoi(argv[3]); 
        int height = atoi(argv[4]);

        cv::Mat inputImg = loadImg(cv::Size(width, height), inputPath);
        cv::Mat outputImg = dither(inputImg);
        outputImg.convertTo(outputImg, CV_32SC3, 255);
        cv::imwrite(outputPath, outputImg);
    } catch(const std::exception& e) {
        printf("Error:\tError while processing image\n%s", e.what());
        return 1;
    }
    return 0;
}