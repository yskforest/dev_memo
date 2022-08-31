
print("Saving paraeters ...... ", end="")
cv_file = cv2.FileStorage("cv_remap.xml", cv2.FILE_STORAGE_WRITE)
cv_file.write("map_x", map_x)
cv_file.write("map_y", map_y)
print("end")

cv_file = cv2.FileStorage("cv_remap.xml", cv2.FILE_STORAGE_READ)
map_x = cv_file.getNode("map_x").mat()
map_y = cv_file.getNode("map_y").mat()
cv_file.release()

cv::FileStorage cv_file_w = cv::FileStorage("cv_remap.xml", cv::FileStorage::WRITE);
cv_file.write("map_x", map_x);
cv_file.write("map_y", map_y);
cv_file.release();

cv::FileStorage cv_file = cv::FileStorage("cv_remap.xml", cv::FileStorage::READ);
cv_file["map_x"] >> map_x;
cv_file["map_y"] >> map_y;
cv_file.release();

cv::remap(cvMat, dst, map_x, map_y, cv::INTER_CUBIC);
