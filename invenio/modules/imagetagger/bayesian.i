%module bayesian

%{
#define SWIG_FILE_WITH_INIT
#include "BayesianRecognizer.h"
%}

%include "std_vector.i"
%include "std_string.i"

namespace std {
   %template(StringVector) vector<string>;
}

%include BayesianRecognizer.h
