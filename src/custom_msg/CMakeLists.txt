cmake_minimum_required(VERSION 3.8) #change is that earlier i put up 3.5 version now ros2 maybe has updated to 3.8 version
project(custom_msg) # change is that the message package is now called custom_msg instead of message :prolly the naming convention shit in ros2



# u don't need this
# Default to C++14
#if(NOT CMAKE_CXX_STANDARD)
  #set(CMAKE_CXX_STANDARD 14)
#endif()


if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Joints.msg"
  "msg/MotorControl.msg"
 )

ament_export_dependencies(rosidl_default_runtime)

ament_package()