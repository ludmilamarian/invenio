/*
Copyright (c) 2003 Colorado State University

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom
the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
*/

#ifndef BAYESIAN_RECOGNIZER_H
#define BAYESIAN_RECOGNIZER_H
extern "C"{
#include <csuCommon.h>
}
#include <math.h>
#include <iostream>
#include <vector>
using namespace std;

typedef struct
{
  char *imageList;
  char *imageDirectory;
  char *trainingFilename;

  char *distanceMatrix;
  int maxRank;

  int nExtrapersonal;
  int nIntrapersonal;

  int cutOffMode;
  double cutOff;
  int dropNVectors;

}
TrainingArguments;

typedef struct {
  char* intrapersonalTrainingFile;
  char* extrapersonalTrainingFile;
  char* imageNamesFile;
  char* imageDirectory;
  char* maxLikelihoodDistDirectory;
  char* bayesianDistDirectory;
  char* distanceMatrix;
  int   maxRank;
  int   N;
}
PredictArguments;

typedef struct {
  char* eyeFile;
  char* imageFile;
}
TestArguments;

class BayesianRecognizer{

public:
	BayesianRecognizer(){
	}
	void train(char* imageList, char* imageDir);
	int predict(char* imagePath, std::vector<std::string> possibilities);
	bool load(char* pathIntra, char* pathExtra);
	void save(char* pathIntra, char* pathExtra);
	double getIRho();
	double getERho();
	void setIRho(double iRho);
	void setERho(double eRho);

private:
	void train(TrainingArguments args);
	void predict(PredictArguments args);

	Subspace intraPersonal;
    Subspace extraPersonal;
    FTYPE iRho, eRho;
};


#endif
