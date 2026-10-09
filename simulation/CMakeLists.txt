cmake_minimum_required(VERSION 3.8)
project(simulation)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS nodes/scan_to_16line.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
