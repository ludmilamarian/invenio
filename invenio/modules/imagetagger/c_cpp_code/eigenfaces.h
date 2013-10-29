#ifndef EIGENFACES_H
#define EIGENFACES_H
#include "opencv2/contrib/contrib.hpp"
#include "opencv2/flann/flann.hpp"
#include "opencv2/features2d/features2d.hpp"
#include "opencv2/objdetect/objdetect.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/imgproc/imgproc_c.h"
#include "opencv2/core/internal.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <vector>
#include <iostream>
#include <fstream>

std::vector<std::vector<int> > test(std::vector<std::vector<int> > list);

class Eigenfaces2 
{
private:
    //subspace dimension
    int _num_components;
    //threshold for returning the prediction
    double _threshold;
    //faces projected onto the PCA space
    cv::Mat _projections;
    //labels(classes) of the faces
	std::vector<int> labels;
    //PCA space description
    cv::Mat _eigenvectors;
    cv::Mat _eigenvalues;
    cv::Mat _mean;
    //structure to do nearest neighbor
    cv::Ptr<cv::DescriptorMatcher> matcher;

	void save(cv::FileStorage& fs);
	void load(const cv::FileStorage& fs);
public: 
    ~Eigenfaces2(){}

    Eigenfaces2(int num_components = 0, double threshold = DBL_MAX) :
        _num_components(num_components),
        _threshold(threshold) {}

    void save(char* filename){
        cv::FileStorage fs(filename, cv::FileStorage::WRITE);
        if (!fs.isOpened()){
            std::cerr<<"couldn't open to save to file"<<std::endl;
			return;
		}
        this->save(fs);
        fs.release();
    }   

    bool load(char* filename){
        cv::FileStorage fs(filename, cv::FileStorage::READ);
        if (!fs.isOpened()){
            std::cerr<<"couldn't open to load from file"<<std::endl;
			return false;
		}
        try{
        	this->load(fs);
        }catch(cv::Exception){
    		std::cerr<<"couldn't load recognizer: "<<filename<<std::endl;
    		fs.release();
    		return false;
    	}
        fs.release();
        return true;
    }

    bool train(std::vector<std::string> data, std::vector<int> labels);

    std::vector<std::vector<cv::DMatch> > predictN(std::vector<cv::Mat> src, int n);

    std::vector<std::vector<int> > predictN(std::string imagePath, int n);

    bool isTrained();
};
#endif
