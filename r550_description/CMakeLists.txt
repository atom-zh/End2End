cmake_minimum_required(VERSION 3.8)
project(r550_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}
  FILES_MATCHING PATTERN "*.urdf" PATTERN "*.pdf"
)

install(
  DIRECTORY gazebo radar autoware
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
