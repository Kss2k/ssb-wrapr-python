# `ssb-wrapr-python`
## To do:
    1. Port all test files for SSB-GaussSuppression, and SSBtools
    2. Better conversion handling
        - Convert ordered dictionaries (which are vectors) to numpy arrays
        - Convert ordered dictionaries (which are lists) to dictionaries
        - Convert lists (which are vectors) to vectors
        - Convert lists (which are lists) to lists
    3. Better warning handling (this will likely be tricky)
    4. Create function for writing R-source code, which can be used as 
        native python code
    5. Maybe not load all functions by default? The indexing takes a while if
        the repo is very large... Maybe just find a way to load it faster?
