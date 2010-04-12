This directory contains the files that mirror other files in the source tree.
The files in this directory represent minimal (non-TriMet) versions, with all 
TriMet specific environment dependency removed.

Such versions are necessary for complining the code without benefit of the TriMet environment.
Specifically, the TriMet code requires the existance of the TRANS enterprise database,
which is obviously not available outside of TriMet.  Thus, the versions of the code here 
remove that dependency, allowing the code (minus the org.trime specific stuff) to build built 
externally.

NOTE: the files here are only put into play via the Ant Task 'generic-zip', which replaces the tTriMet specific versions
with these replacments in the outgoig zip file.

Frank Purcell
purcellf@trimet.org
11-03-2006
