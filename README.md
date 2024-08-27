# `ssb-wrapr-python`
## To do:
    1. Port all test files for SSB-GaussSuppression, and SSBtools
    2. Better conversion handling for output
        - Convert ordered dictionaries (which are vectors) to numpy arrays
        - Convert ordered dictionaries (which are lists) to dictionaries
        - Convert lists (which are vectors) to vectors
        - Convert lists (which are lists) to lists
        - S4 CLASSES ARE TRICKY!
    3. Better conversion handling for input!
        - S4 CLASSES ARE TRICKY
    4. Refactor modules, into seperate files 
        - Convert shoudld be split into three (maybe four) sub-modules/files
            1. rutils
            2. convert_in
            3. convert_out
           (4.) py->r->py wrapping function factory
    5. Better warning handling (this will likely be tricky)
