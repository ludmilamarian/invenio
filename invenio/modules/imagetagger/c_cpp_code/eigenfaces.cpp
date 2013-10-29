#include "eigenfaces.h"
using namespace cv;
using namespace std;

std::vector<std::vector<int> > test(std::vector<std::vector<int> > list){
	vector<vector<int> > result;
	for(int i=0;i<list.size();i++){
		result.push_back(vector<int>());
		for(int j=0;j<list[i].size();j++){
			result[i].push_back(list[i][j]+1);
		}
	}
	return result;
}

template<typename _Tp>
inline void readFileNodeList(const FileNode& fn, vector<_Tp>& result) {
cout<<"hgjgj";
    if (fn.type() == FileNode::SEQ) {
        for (FileNodeIterator it = fn.begin(); it != fn.end();) {
            _Tp item;
            it >> item;
cout<<"sritting"<<item;
            result.push_back(item);
        }
    }
}

template<typename _Tp>
inline void writeFileNodeList(FileStorage& fs, const string& name,
                              const vector<_Tp>& items) {
    typedef typename vector<_Tp>::const_iterator constVecIterator;
    fs << name << "[";
    for (constVecIterator it = items.begin(); it != items.end(); ++it) {
        fs << *it;
    }
    fs << "]";
}

static Mat asRowMatrix(InputArrayOfArrays src, int rtype, double alpha=1, double beta=0) {
    // make sure the input data is a vector of matrices or vector of vector
    if(src.kind() != _InputArray::STD_VECTOR_MAT && src.kind() != _InputArray::STD_VECTOR_VECTOR) {
        string error_message = "The data is expected as InputArray::STD_VECTOR_MAT (a std::vector<Mat>) or _InputArray::STD_VECTOR_VECTOR (a std::vector< vector<...> >).";
        CV_Error(CV_StsBadArg, error_message);
    }
    // number of samples
    size_t n = src.total();
    // return empty matrix if no matrices given
    if(n == 0)
        return Mat();
    // dimensionality of (reshaped) samples
    size_t d = src.getMat(0).total();
    // create data matrix
    Mat data((int)n, (int)d, rtype);
    // now copy data
    for(unsigned int i = 0; i < n; i++) {
        // make sure data can be reshaped, throw exception if not!
        if(src.getMat(i).total() != d) {
            string error_message = format("Wrong number of elements in matrix #%d! Expected %d was %d.", i, d, src.getMat(i).total());
            CV_Error(CV_StsBadArg, error_message);
        }
        // get a hold of the current row
        Mat xi = data.row(i);
        // make reshape happy by cloning for non-continuous matrices
        if(src.getMat(i).isContinuous()) {
            src.getMat(i).reshape(1, 1).convertTo(xi, rtype, alpha, beta);
        } else {
            src.getMat(i).clone().reshape(1, 1).convertTo(xi, rtype, alpha, beta);
        }
    }
    return data;
}

inline Mat getData(vector<string> data){
	Mat result;
	for(int i=0;i<data.size();i++){
		result.push_back(imread(data[i],0).reshape(0,1).clone());
	}
	return result;
}

bool Eigenfaces2::train(vector<string> _data, vector<int> labels) {
	Mat data = getData(_data);

	if(data.rows<5)
		return false;
    // number of samples
   int n = data.rows;
    // assert there are as much samples as labels
    if(static_cast<int>(labels.size()) != n) {
        string error_message = format("The number of samples (src) must equal the number of labels (labels)! len(src)=%d, len(labels)=%d.", n, labels.size());
        CV_Error(CV_StsBadArg, error_message);
    }
    // clip number of components to be valid
    if((_num_components <= 0) || (_num_components > n))
        _num_components = n;

    // perform the PCA
    PCA pca(data, Mat(), CV_PCA_DATA_AS_ROW, _num_components);
    // copy the PCA results
    _mean = pca.mean.reshape(1,1); // store the mean vector
    _eigenvalues = pca.eigenvalues.clone(); // eigenvalues by row
    transpose(pca.eigenvectors, _eigenvectors); // eigenvectors by column
    // store labels for prediction
    this->labels = labels;
    // save projections
    for(int sampleIdx = 0; sampleIdx < data.rows; sampleIdx++) {
        Mat p = subspaceProject(_eigenvectors, _mean, data.row(sampleIdx));
        p.convertTo(p, CV_32F);
    	if(_projections.rows==0)
    		_projections=p;
    	else
            _projections.push_back(p);
    }
    matcher = DescriptorMatcher::create("BruteForce");
    return true;
}

vector<vector<DMatch> > Eigenfaces2::predictN(vector<Mat> src, int n) {
    Mat vectors;
    for(int i=0;i<src.size();i++){
        Mat p = subspaceProject(_eigenvectors, _mean, src[i].reshape(1,1));
        p.convertTo(p, CV_32F);
        vectors.push_back(p);
    }
    
    vector<vector<DMatch> > matches;
    matcher->knnMatch(vectors, _projections, matches, n);
    return matches;
}

vector<vector<int> > Eigenfaces2::predictN(string imagePath, int n){
    vector<Mat> images;
    vector<vector<int> > result;
    images.push_back(imread(imagePath, 0));
    vector<vector<DMatch> > matches = predictN(images, n);
    for(int i=0;i<matches.size();i++){
        result.push_back(vector<int>());
        for(int j=0;j<matches[i].size();j++){
            result[i].push_back(labels[matches[i][j].trainIdx]);
        }
    }
    return result;
}

void Eigenfaces2::save(FileStorage& fs){
    fs << "num_components" << _num_components;
    fs << "mean" << _mean;
    fs << "eigenvalues" << _eigenvalues;
    fs << "eigenvectors" << _eigenvectors;
	fs<<"projections"<<_projections;
    fs << "labels" << labels;
}

void Eigenfaces2::load(const FileStorage& fs) {
    fs["num_components"] >> _num_components;
    fs["mean"] >> _mean;
    fs["eigenvalues"] >> _eigenvalues;
    fs["eigenvectors"] >> _eigenvectors;
    fs["projections"]>>_projections;
    fs["labels"] >> labels;
    /*matcher->add(_projections);
    matcher->train();*/
}

bool Eigenfaces2::isTrained(){
    return labels.size() != 0;
}

int main( int argc, char** argv )
{
   cout<<"bla";
   return 0;
}
