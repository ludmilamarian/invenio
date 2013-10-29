%module normalization 
%{
#define SWIG_FILE_WITH_INIT
#include "csuPreprocessNormalize.h"
%}

// Now list ANSI C/C++ declarations
void normalizeImages(char* eyeFile, char* inputDir, char* sfiDir);
void normalizeImageAndWrite(char* imagePath, char* outputPath, double eyelx, double eyely, double eyerx, double eyery, int type);
Image* getRawImages(char* eyeFile, char* inputDir, char* sfiDir, int n);
int getWidth(Image* images, int img);
int getHeight(Image* images, int img);
int getChannels(Image* images, int img);
double getData(Image* images, int img, int col, int row, int channel);

