%module eigenfaces

%{
#define SWIG_FILE_WITH_INIT
#include "eigenfaces.h"
%}

%include "std_vector.i"
%include "std_string.i"
 
namespace std {
   %template(IntVector) vector<int>;
   %template(StringVector) vector<string>;
   %template(IntVectorVector) vector<vector<int> >;
}

%include eigenfaces.h


