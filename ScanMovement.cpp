#include <opencv2/opencv.hpp>
#include <iostream>

using namespace std;
using namespace cv;

int main(int argc, char** args) {
    if (argc == 1)
        throw std::invalid_argument("No input mp4 file given");
    string inputFile = args[1];
    string outputFile = argc > 2 ? args[2] : "output.mp4";

    VideoCapture vidReader(inputFile);

    // Check if video is imported successfully
    if (vidReader.isOpened() == false) {
        cout << "Cannot open the video file" << endl;
        cin.get(); //wait for any key press
        return -1;
    }

    int frames = (int)vidReader.get(CAP_PROP_FRAME_COUNT);
    int fps = (int)vidReader.get(CAP_PROP_FPS);

    double dWidth = vidReader.get(CAP_PROP_FRAME_WIDTH);
    double dHeight = vidReader.get(CAP_PROP_FRAME_HEIGHT);
    Size frameSize(dWidth, dHeight);

    VideoWriter vidWriter(outputFile, VideoWriter::fourcc('m', 'p', '4', 'v'), fps, frameSize, true);

    Mat prevFrame;
    Mat frame;
        
    vidReader.read(prevFrame);
    for (int i=0; i<frames-1; i++) {
        vidReader.read(frame);
        for (int y=0; y<frame.rows;y++) {
            for (int x=0; x<frame.cols;x++) {
                Vec3b& pixel = frame.at<Vec3b>(y, x);
                Vec3b& prevPixel = prevFrame.at<Vec3b>(y, x);
                if (abs(pixel[0] + pixel[1] + pixel[2] - (prevPixel[0] + prevPixel[1] + prevPixel[2])) < 10) {
                    prevPixel = pixel;
                } else {
                    prevPixel = pixel;
                    pixel[0] = pixel[1] = 0;
                    pixel[2] = 255;
                }
            }
        }
        vidWriter.write(frame);
    }
    cout << "Successfully scanned video for pixel changes (at output.mp4)" << endl;
    return 0;
}