Scripts to analyze the pictures taken with a TWR-type interferometer ('asymmetric' Mach-Zenhder).

(Pictures are in a separate storage location)

# Short description of scripts:


# In folder scripts/matlab-libraries/u18

- load_sessions.m:
Definition of `packages`.
A `package` are the pictures taken from `date_start` to `date_end`.
The definition of a package has other self-documented properties.

- u20_packages_analysis.m:
Runs the selected packages as defined in the array `process_sessions`
This is the MAIN FILE. Just press F5 to run.

It runs the 'packages' listed in array `process_sessions`.

- u18w_general.m
Orchestrator script:
    - triggers main analisys of pictures to detect maxima
    - triggers plot making, analysis
    - generates .csv file with output data

- u18_plots.m:
makes the analysis and plot
generates .csv file

- u18_make_generalvideo.m
makes videos out of a folder of pics

- u18_analisis_fotos.m
detects and logs maxima per picture

- plotheightstar.m
`holds` the current plot and adds plots for stellar objects

- writeSummary.m
Writes .csv file

# In folder
- readdatetimealt.m
Read/caches the stellar data files generated in Stellarium


# In folder scripts/
- heightstar.ssc
Stellarium script to download stellar object data
