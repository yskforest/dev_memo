# Script memo

##
```cpp
UTextureRenderTarget2D* RenderTargetRuntime;

RenderTargetRuntime = NewObject<UTextureRenderTarget2D>(this);
RenderTargetRuntime->InitCustomFormat(VideoSize.X, VideoSize.Y, PF_A32B32G32R32F, false);
RenderTargetRuntime->UpdateResource();

Scene_Capture->TextureTarget = RenderTargetRuntime;

FRenderTarget* renderTarget;
renderTarget = RenderTargetRuntime->GameThread_GetRenderTargetResource();
renderTarget->ReadLinearColorPixels(ColorDataFloat);
int cvColorMode = CV_32FC4;

cv::Mat img(height, width, cvColorMode, ColorDataFloat);
cv::cvtColor(img, img, cv::COLOR_RGBA2BGR);
cv::imshow(windowName, img);
```

```cpp
bool ImgShow(std::string windowName, const int width, const int height, const int cvColorMode, void *srcPtr)
{
	if (srcPtr == nullptr)
		return false;

	// 直接Mat化
	cv::Mat img(height, width, cvColorMode, srcPtr);
	cv::cvtColor(img, img, cv::COLOR_RGBA2BGR);

	cv::imshow(windowName, img);

	return true;
}

bool CvImgProc(const int width, const int height, const int cvColorMode, void *srcPtr)
{
	if (srcPtr == nullptr)
		return false;

	// img.at<cv::Vec3b>(y, x)で入力
	float *floatDataPtr = (float *)srcPtr;
	cv::Mat img(height, width, CV_8UC3);
	const int matDim = 4;
	for (int y = 0; y < height; y++)
	{
		for (int x = 0; x < width; x++)
		{
			const int index = y * width + x;
			img.at<cv::Vec3b>(y, x) = cv::Vec3b((uchar)floor(floatDataPtr[index * matDim + 2] * 255),
												(uchar)floor(floatDataPtr[index * matDim + 1] * 255),
												(uchar)floor(floatDataPtr[index * matDim + 0] * 255));
		}
	}
	cv::imshow("CvImgProc", img);

	// for (int y = 0; y < height; y++)
	// {
	// 	cv::Vec3b *src = dataPtr<cv::Vec3b>(y);
	// 	for (int x = 0; x < width; x++)
	// 	{
	// 		const int index = y * width + x;
	// 		src[i]; // i番目にアクセス
	// 	}
	// }

	// // vector<float>化
	// std::vector<float> data;
	// data.reserve(width * height * 3);
	// for (int y = 0; y < height; y++)
	// {
	// 	for (int x = 0; x < width; x++)
	// 	{
	// 		const int index = y * width + x;
	// 		data.emplace_back(floatDataPtr[index * matDim + 0]);
	// 		data.emplace_back(floatDataPtr[index * matDim + 1]);
	// 		data.emplace_back(floatDataPtr[index * matDim + 2]);
	// 	}
	// }
	// CvImgProc("vector<float>", width, height, data);

	return true;
}
```