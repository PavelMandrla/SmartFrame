cmake_minimum_required(VERSION 3.0.0)
project(ImageAnalysis1 VERSION 0.1.0)

find_package(OpenCV REQUIRED)
find_package(OpenMP REQUIRED)

set (CMAKE_CXX_STANDARD 17)

add_executable(
    dithering
    
    main.cpp
)

target_link_libraries(
    dithering

    ${OpenCV_LIBS}
    OpenMP::OpenMP_CXX
)
