Configuring R shared library
==============================

To configure the static R library needed to compute the qbeta function, follow the [instructions from the R project](http://cran.r-project.org/doc/manuals/r-release/R-admin.html#Unix_002dalike-standalone).

Then, you can use the `--Rlib` argument to link to the generated _.so_ (or _.dylib_).
By default, the script will try to use _libRmath.so_ in his parent directory.


