
	TArray<float> TesnorImage;
	UNeuralNetwork* Network = nullptr;
	TArray<float> InputImageCPU;
	TArray<FString> ClassNames = { TEXT("person"), TEXT("bicycle"), TEXT("car"),
		TEXT("motorcycle"), TEXT("airplane"), TEXT("bus"),
		TEXT("train"), TEXT("truck"), TEXT("boat"),
		TEXT("traffic light"), TEXT("fire hydrant"), TEXT("stop sign"),
		TEXT("parking meter"), TEXT("bench"), TEXT("bird"),
		TEXT("cat"), TEXT("dog"), TEXT("horse"),
		TEXT("sheep"), TEXT("cow"), TEXT("elephant"),
		TEXT("bear"), TEXT("zebra"), TEXT("giraffe"),
		TEXT("backpack"), TEXT("umbrella"), TEXT("handbag"),
		TEXT("tie"), TEXT("suitcase"), TEXT("frisbee"),
		TEXT("skis"), TEXT("snowboard"), TEXT("sports ball"),
		TEXT("kite"), TEXT("baseball bat"), TEXT("baseball glove"),
		TEXT("skateboard"), TEXT("surfboard"), TEXT("tennis racket"),
		TEXT("bottle"), TEXT("wine glass"), TEXT("cup"),
		TEXT("fork"), TEXT("knife"), TEXT("spoon"),
		TEXT("bowl"), TEXT("banana"), TEXT("apple"),
		TEXT("sandwich"), TEXT("orange"), TEXT("broccoli"),
		TEXT("carrot"), TEXT("hot dog"), TEXT("pizza"),
		TEXT("donut"), TEXT("cake"), TEXT("chair"),
		TEXT("couch"), TEXT("potted plant"), TEXT("bed"),
		TEXT("dining table"), TEXT("toilet"), TEXT("tv"),
		TEXT("laptop"), TEXT("mouse"), TEXT("remote"),
		TEXT("keyboard"), TEXT("cell phone"), TEXT("microwave"),
		TEXT("oven"), TEXT("toaster"), TEXT("sink"),
		TEXT("refrigerator"), TEXT("book"), TEXT("clock"),
		TEXT("vase"), TEXT("scissors"), TEXT("teddy bear"),
		TEXT("hair drier"), TEXT("toothbrush") };

	// OpenCVの関数に使用する際にメンバ変数にしないとクラッシュする（要検証）
	cv::Mat Blob32;
	std::vector<cv::Mat> MatSplitRGBs;

	// std::vector<int> NmsResults;
	std::vector<int> ClassIds;
	std::vector<float> Confidences;
	std::vector<cv::Rect> Boxes;
	int FrameCount = 0;
	InterfaceYolo 


	const std::vector<cv::Scalar> colors = { cv::Scalar(255, 255, 0), cv::Scalar(255, 0, 255), cv::Scalar(0, 255, 255),
		cv::Scalar(255, 0, 0), cv::Scalar(0, 255, 0), cv::Scalar(0, 0, 255),
		cv::Scalar(0, 127, 127), cv::Scalar(127, 0, 127), cv::Scalar(127, 127, 0),
		cv::Scalar(127, 0, 0), cv::Scalar(0, 127, 0), cv::Scalar(0, 0, 127) };
	const float INPUT_WIDTH = 640.0;
	const float INPUT_HEIGHT = 640.0;
	const float SCORE_THRESHOLD = 0.2;
	const float NMS_THRESHOLD = 0.4;
	const float CONFIDENCE_THRESHOLD = 0.4;

void SetModel(UNeuralNetwork* Model)
{
	Network = Model;
}

// cv::Mat format_yolov5(const cv::Mat& source)
// {
// 	cv::Mat buf;
// 	cv::cvtColor(source, buf, cv::COLOR_RGBA2RGB);
// 	int col = buf.cols;
// 	int row = buf.rows;
// 	int _max = MAX(col, row);
// 	cv::Mat result = cv::Mat::zeros(_max, _max, CV_8UC3);
// 	buf.copyTo(result(cv::Rect(0, 0, col, row)));
// 	return result;
// }

// void Detector(cv::Mat src)
// {
// 	auto input_image = format_yolov5(src);
// 	float x_factor = input_image.cols / INPUT_WIDTH;
// 	float y_factor = input_image.rows / INPUT_HEIGHT;

// 	const int YoloWidth = 640;
// 	const int YoloHeight = 640;
// 	const int PixelCount = YoloWidth * YoloHeight;
// 	float conf_threshold = 0.3f;

// 	TArray<float> PixelR;
// 	TArray<float> PixelG;
// 	TArray<float> PixelB;

// 	TesnorImage.Reset();
// 	TesnorImage.Reserve(PixelCount * 3);

// 	cv::Mat blob;
// 	cv::resize(input_image, blob, cv::Size(YoloWidth, YoloHeight));

// 	// blob.convertTo(Blob32, CV_32FC3, 1.0 / 255);
// 	// cv::split(Blob32, MatSplitRGBs);

// 	// クラッシュする
// 	// cv::dnn::blobFromImage(input_image, blob, 1. / 255., cv::Size(INPUT_WIDTH, INPUT_HEIGHT), cv::Scalar(), true,
// 	// false);
// 	int ch = blob.channels();
// 	uint8* srcPtr = blob.ptr();

// 	// float* imagePtr = TesnorImage.GetData();
// 	// imagePtr = (float*)(MatSplitRGBs[0].ptr());
// 	//(imagePtr + PixelCount) = (float*)(MatSplitRGBs[0].ptr());
// 	//(imagePtr + PixelCount) = (float*)(MatSplitRGBs[0].ptr());

// 	// imagePtr[0]) =

// 	// 入力テンソル作成
// 	// netronで確認したときは1x3x640x640だったが、640x640x3x1にしないと検出してくれない
// 	for (int y = 0; y < YoloHeight; y++) {
// 		int srcOffset = YoloWidth * ch * y;
// 		for (int x = 0; x < YoloWidth; x++) {
// 			PixelR.Add(srcPtr[srcOffset + x * ch] / 255.f);
// 			PixelG.Add(srcPtr[srcOffset + x * ch + 1] / 255.f);
// 			PixelB.Add(srcPtr[srcOffset + x * ch + 2] / 255.f);
// 		}
// 	}
// 	TesnorImage += PixelR;
// 	TesnorImage += PixelG;
// 	TesnorImage += PixelB;

// 	Network->ResetStats();
// 	Network->SetInputFromArrayCopy(TesnorImage);
// 	// 推論を実行
// 	Network->Run();
// 	// 出力テンソルを取得
// 	TArray<float> output = Network->GetOutputTensor().GetArrayCopy<float>();
// 	// TArray<float> predictions, obj_conf, box_info;
// 	// YOLO 640x640の出力テンソル1x25200x85
// 	//  new
// 	float* data = output.GetData();
// 	const int dimensions = 85;
// 	const int rows = 25200;

// 	// std::vector<int> NmsResults;
// 	// std::vector<int> ClassIds;
// 	// std::vector<float> Confidences;
// 	// std::vector<cv::Rect> Boxes;

// 	// NmsResults.clear();
// 	// ClassIds.clear();
// 	// Confidences.clear();
// 	// Boxes.clear();
// 	// NmsResults.shrink_to_fit();
// 	// ClassIds.shrink_to_fit();
// 	// Confidences.shrink_to_fit();
// 	// Boxes.shrink_to_fit();

// 	for (int i = 0; i < rows; ++i) {
// 		float confidence = data[4];
// 		if (confidence >= CONFIDENCE_THRESHOLD) {
// 			float* classes_scores = data + 5;
// 			cv::Mat scores(1, ClassNames.Num(), CV_32FC1, classes_scores);
// 			cv::Point class_id;
// 			double max_class_score;
// 			minMaxLoc(scores, 0, &max_class_score, 0, &class_id);
// 			if (max_class_score > SCORE_THRESHOLD) {
// 				Confidences.push_back(confidence);
// 				ClassIds.push_back(class_id.x);

// 				float x = data[0];
// 				float y = data[1];
// 				float w = data[2];
// 				float h = data[3];
// 				int left = int((x - 0.5 * w) * x_factor);
// 				int top = int((y - 0.5 * h) * y_factor);
// 				int width1 = int(w * x_factor);
// 				int height1 = int(h * y_factor);
// 				Boxes.push_back(cv::Rect(left, top, width1, height1));

// 				cv::rectangle(src, cv::Rect(left, top, width1, height1), colors[class_id.x % colors.size()], 3);
// 			}
// 		}
// 		data += 85;
// 	}

// 	////Boxes
// 	////クラッシュする
// 	// cv::dnn::NMSBoxes(Boxes, Confidences, SCORE_THRESHOLD, NMS_THRESHOLD, NmsResults);
// 	// for (int i = 0; i < NmsResults.size(); i++) {
// 	//	int idx = NmsResults[i];
// 	//	//Detection result;
// 	//	//result.class_id = class_ids[idx];
// 	//	//result.confidence = confidences[idx];
// 	//	//result.box = Boxes[idx];
// 	//	cv::rectangle(src, Boxes[idx], colors[ClassIds[idx] % colors.size()], 3);
// 	//	//output.push_back(result);
// 	// }

// 	////cv::imshow("tensor", src);
// 	// Frame += 1;
// }