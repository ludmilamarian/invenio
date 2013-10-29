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
#include "BayesianRecognizer.h"
#include <fstream>
using namespace std;

/******************************************************************************
*           REVISED BAYESIAN PROBABILITY EQUATIONS                           *
*****************************************************************************/

/* Use nomenclature consistent with Moghaddam and Pentland */
#define CONST_N(s)  (s->numPixels)
#define CONST_M(s)  (s->basis->col_dim)  /* Number of principal components that we kept */
#define CONST_Nt(s) (s->basisDim)
#define EACH_SUBJECT(srt, subject)           (subject = srt; subject != NULL; subject = subject->next_subject)
#define EACH_REPLICATE(srt, replicate)       (replicate = srt; replicate != NULL; replicate = replicate->next_replicate)


FTYPE
	computeRho (Subspace *s)
{
	int i;
	FTYPE tmp = 0.0;

	tmp = 0.0;
	for (i = CONST_M(s); i < CONST_Nt(s); i++){
		if(!isnan(ME(s->values,i,0)))
			tmp += ME(s->values,i,0);
	}
	return tmp / (CONST_Nt(s) - CONST_M(s));
}

FTYPE computeMaxLikelihood (Matrix delta, Subspace *s, FTYPE rho)
{
	int i;
	Matrix y, deltaCentered;
	FTYPE mahSumOfSquares, ySumOfSquares, deltaSumOfSquares;
	FTYPE ySquared, epsilonSquaredOfX, score;

	/* y is the projection of X into the s. Note that
	* as a side-effect, centerThenProjectImages mean
	* centers deltaCentered */

	deltaCentered = duplicateMatrix(delta);
	y = centerThenProjectImages(s, deltaCentered);

	mahSumOfSquares   = 0.0;
	ySumOfSquares     = 0.0;
	deltaSumOfSquares = 0.0;

	for (i = 0; i < CONST_M(s); i++)
		if (ME(s->values,i,0) != 0.0)
		{
			ySquared = SQR(ME(y,i,0));

			mahSumOfSquares += ySquared / ME(s->values,i,0);
			ySumOfSquares   += ySquared;
		}

		for (i = 0; i < CONST_N(s); i++) 
			deltaSumOfSquares += SQR(ME(deltaCentered,i,0));

		epsilonSquaredOfX = deltaSumOfSquares - ySumOfSquares;
		score = mahSumOfSquares + epsilonSquaredOfX / rho;

		/* Clean up */

		freeMatrix (deltaCentered);
		freeMatrix (y);

		return  score;
}

bool BayesianRecognizer::load(char* pathIntra, char* pathExtra){
	readSubspace2(&intraPersonal, pathIntra);
	readSubspace2(&extraPersonal, pathExtra);
	iRho = computeRho(&intraPersonal);
	eRho = computeRho(&extraPersonal);
}

void BayesianRecognizer::save(char* pathIntra, char* pathExtra){
	writeSubspace2(&intraPersonal, pathIntra);
	writeSubspace2(&extraPersonal, pathExtra);
}

void BayesianRecognizer::setIRho(double iRho){
	this->iRho = iRho;
}

void BayesianRecognizer::setERho(double eRho){
	this->eRho = eRho;
}

double BayesianRecognizer::getIRho(){
	return iRho;
}

double BayesianRecognizer::getERho(){
	return eRho;
}

TrainingArguments buildTrainingArgs(char* imageList, char* imageDir){
	TrainingArguments targs;
	targs.nIntrapersonal = 100;
	targs.nExtrapersonal = 100;
	targs.distanceMatrix = NULL;
	targs.maxRank = -1;
	targs.cutOffMode = CUTOFF_SIMPLE;
	targs.cutOff = DEFAULT_CUTOFF_PERCENT_SIMPLE;
	targs.dropNVectors = 0;
	targs.imageDirectory = imageDir;
	targs.imageList = imageList;
	targs.trainingFilename = NULL;
	return targs;
}

void BayesianRecognizer::train(char* imageList, char* imageDir){
	TrainingArguments args = buildTrainingArgs(imageList, imageDir);
	train(args);
}

void BayesianRecognizer::train(TrainingArguments args){
	Matrix intraImages, extraImages;
	checkReadableDirectory (args.imageDirectory, "%s is not a readable directory");
	checkReadableFile (args.imageList, "Cannot read subject replicates list %s");
	makeDifferenceImages (args.imageDirectory,
		args.imageList,
		args.distanceMatrix,
		args.maxRank,
		args.nIntrapersonal,
		args.nExtrapersonal,
		&intraImages,
		&extraImages
		);
	subspaceTrain (&intraPersonal, intraImages, NULL, args.nIntrapersonal, args.dropNVectors, (CutOffMode)args.cutOffMode, args.cutOff, 0, 0);
	intraPersonal.basisDim = intraPersonal.basis->row_dim;
	subspaceTrain (&extraPersonal, extraImages, NULL, args.nExtrapersonal, args.dropNVectors, (CutOffMode)args.cutOffMode, args.cutOff, 0, 0);
	extraPersonal.basisDim = extraPersonal.basis->row_dim;
	iRho = computeRho(&intraPersonal);
	eRho = computeRho(&extraPersonal);
	cout<<"erho"<<eRho<<"iRho"<<iRho<<endl;

}

vector<string> parse(char* imageList){
	return vector<string>();
}

int BayesianRecognizer::predict(char* imagePath, vector<string> nPossibilities){
	vector<string> trainingImages = nPossibilities;
	int nImages = 1, numPixels = autoFileLength (imagePath), N = trainingImages.size();
	Matrix delta = makeMatrix (numPixels, 1);
	Matrix data = makeMatrix (numPixels, nImages);
	Matrix dataModel = makeMatrix (numPixels, N*nImages);

	//reading of the N possible matches for the tested image
	for(int i = 0; i < N; i++){
		readFile (trainingImages[i].c_str(), i, dataModel);
	}

	Matrix maxLikelihoodDistances = makeMatrix (nImages, N);
	Matrix bayesianDistances      = makeMatrix (nImages, N);
	double min_dists_ml = -1, min_dists_map = -1;
	int min_pos_ml = -1, min_pos_map = -1;
	FTYPE iLikelihood, eLikelihood;
	//distance computation using difference images and 2 different methods
	for(int j = 0; j < N; j++){
		for (int k = 0; k < data->row_dim; k++)
			ME (delta, k, 0) = ME (data, k, 0) - ME (dataModel, k, j);
		iLikelihood = computeMaxLikelihood (delta, &intraPersonal, iRho);
		eLikelihood = computeMaxLikelihood (delta, &extraPersonal, eRho);
		ME(maxLikelihoodDistances, 0, j) = iLikelihood;
		if(!isnan(iLikelihood)){
			if(min_dists_ml == -1 || min_dists_ml > iLikelihood){
				min_dists_ml = iLikelihood;
				min_pos_ml = j;
			}
		}
		ME(bayesianDistances, 0, j)      = iLikelihood - eLikelihood;
		if(!isnan(iLikelihood - eLikelihood)){
			if(min_dists_map == -1 || min_dists_map > iLikelihood - eLikelihood){
				min_dists_map = iLikelihood - eLikelihood;
				min_pos_map = j;
			}
		}
	}	

	if(isnan(min_dists_ml))
		return min_pos_map;
	else
		return min_pos_ml;
}
