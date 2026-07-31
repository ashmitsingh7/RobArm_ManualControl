cmake_minimum_required(VERSION 3.8)
project(controls)

if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/MotorControl.msg"
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following linter hooks are implemented on top of ament_lint_auto:
  # ament_lint_common, ament_cpplint, ament_pycodestyle, ament_uncrustify
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()