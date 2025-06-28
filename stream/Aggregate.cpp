#include <iostream>
#include <opencv2/videoio.hpp>
#include <filesystem>

namespace fs = std::filesystem;

/**
 * Aggregates video files in directory created by CameraArchiver into one video
 * 
 * usage: Aggregate directory [output] [seconds]
 * directory: directory containing all the videos
 * output: output video file, default is aggregated.mp4
 * seconds: maximum number of seconds to write to output
 * 
 * Uses video structure:
 * directory/
 *          * media0.mp4
 *          * media1.mp4
 *          * ...
 *          * media{n}.mp4 
 */
int main(int argc, char** argv) {
    // the user must provide a video directory, if not throw error
    if (argc == 1) {
        throw std::invalid_argument("No arguments passed, needs a video directory");
        return 0;
    }
    std::string inputPath = argv[1];
    std::string outputPath = argc >= 3 ? argv[2] : "aggregated.mp4";

    // simply count files because this assumes the structure of the filesystem to be:
    // xxxx/media0.mp4, media1.mp4, media'n'.mp4
    unsigned int fileCount = 0;
    for (const auto & entry : fs::directory_iterator(inputPath)) {
        fileCount++;
    }

    // read the first video in the directory and get its properties
    // if the videos have different props it breaks (it really should anyway)
    cv::VideoCapture vidreader(inputPath + "media0.mp4");
    int fps = vidreader.get(cv::CAP_PROP_FPS);
    cv::Size frameSize(vidreader.get(cv::CAP_PROP_FRAME_WIDTH), 
                       vidreader.get(cv::CAP_PROP_FRAME_HEIGHT));

    // Note, if -1 is passed in, this is 4294967295. You get chaos if you ask for chaos.
    unsigned int maxFrames = argc >= 4 ? std::stoi(argv[3]) * fps : 0;
    unsigned int writtenFrames = 0;

    // instantiate video writer and frame to write frames from videos into new video
    cv::VideoWriter vidwriter(outputPath, cv::VideoWriter::fourcc('a', 'v', 'c', '1'), fps, frameSize, true);
    cv::Mat frame;
    // loop through every file and copy and paste each frame (unless max frames is reached)
    for (unsigned int i = 0; i < fileCount; i++) {
        if (maxFrames) {
            std::cout << inputPath+std::to_string(i)+".mp4 "<<writtenFrames/fps<<"s/"<<maxFrames/fps<<"s" << std::endl;
        } else {
            std::cout << inputPath+std::to_string(i)+".mp4 "<<writtenFrames/fps<<"s" << std::endl;
        }

        cv::VideoCapture vidreader(inputPath+"media"+std::to_string(i)+".mp4");
        while (vidreader.read(frame)) {
            vidwriter.write(frame);
            // keep track of written frame count and exit when reached
            writtenFrames++;
            if (maxFrames && writtenFrames > maxFrames) {
                std::cout << "Aggregated "<<writtenFrames/fps<<" seconds from "<<inputPath<<" as "<<outputPath << std::endl;
                return 0;
            }
        }
    }
    std::cout << "Aggregated all in directory "<<inputPath<<" as "<<outputPath << std::endl;
    return 0;
}