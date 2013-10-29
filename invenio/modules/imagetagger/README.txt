OpenCV compilation:
	requierments:
		see http://docs.opencv.org/doc/tutorials/introduction/linux_install/linux_install.html 
	installation :
		download  http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.6.1/opencv-2.4.6.1.tar.gz
		untar
		cd opencv-2.4.6.1/
		mkdir release
		cd release
		cmake -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=OFF -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON ..
		make
		sudo make install
	linking for invenio:
		ln -s /usr/local/lib/python2.7/dist-packages/cv* ./lib/python2.7/site-packages/




c-c++ code compilation, wrapper creation:

	swig -python -includeall -o normalization_warp.c normalization.i
	gcc -c csuPreprocessNormalize.c normalization_warp.c csuCommonMatrix.c csuCommonFile.c csuCommonUtil.c csuCommonSubspace.c csuCommonCommandLine.c csuCommonImage.c csuSubspaceEigen.c csuSubspaceFisher.c csuSubspaceCVEigen.c -Xlinker -export-dynamic -DHAVE_CONFIG_H -I/usr/include/python2.7 -I/usr/lib/python2.7/config -I/home/cern/Downloads/eigenfaces/src/wrap  -L/usr/lib/python2.7/config -lpython2.7 -lm -ld -fpic
	
	swig -c++ -python eigenfaces.i
	g++ -fPIC `pkg-config --cflags opencv` eigenfaces.cpp eigenfaces_wrap.cxx -I/usr/include/python2.7 -I/home/cern/Downloads/eigenfaces/src/wrap -o _eigenfaces.so `pkg-config --libs opencv` -shared

	swig -c++ -python bayesian.i
	gcc -c csuCommonMatrix.c csuCommonFile.c csuCommonUtil.c csuCommonSubspace.c csuCommonCommandLine.c csuCommonImage.c csuSubspaceEigen.c csuSubspaceFisher.c csuSubspaceCVEigen.c -I/home/cern/Downloads/eigenfaces/src/wrap -lm -fPIC
	g++ -c -fPIC `pkg-config --cflags opencv` BayesianRecognizer.cpp bayesian_wrap.cxx -I/usr/include/python2.7 -I/home/cern/Downloads/eigenfaces/src/wrap -fpermissive
	g++ -fPIC `pkg-config --cflags opencv` csuCommonMatrix.o csuCommonFile.o csuCommonUtil.o csuCommonSubspace.o csuCommonCommandLine.o csuCommonImage.o csuSubspaceEigen.o csuSubspaceFisher.o csuSubspaceCVEigen.o BayesianRecognizer.o bayesian_wrap.o -I/usr/include/python2.7 -I/home/cern/Downloads/eigenfaces/src/wrap -o _bayesian.so `pkg-config --libs opencv` -shared -fpermissive
	

OpenCV cascades learning for face detection:
	see http://docs.opencv.org/doc/user_guide/ug_traincascade.html for a tutorial


