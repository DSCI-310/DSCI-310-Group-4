# Obtain image from this source
FROM rocker/rstudio

RUN apt-get update && apt-get install -y --no-install-recommends build-essential r-base python3.9 python3-pip python3-setuptools python3-dev

# Install python3 package with package
RUN pip3 install argparse==1.4.0

# Install required dependencies for R Markdown

RUN Rscript -e "install_version('tidyverse')"
RUN Rscript -e "install.packages('knitr', dependencies = TRUE)"
RUN Rscript -e "install.packages('bookdown')"
RUN Rscript -e "tinytex::install_tinytex()"

 
# Install python package with package
RUN conda install --yes --quiet --channel conda-forge \
    matplotlib=3.5.1 \
    numpy=1.22.2 \
    pandas=1.4.1 \
    seaborn=0.11.2 \
    xgboost=1.5.1 \
    scikit-learn=1.0.2 \
    plotly=5.6.0 \
    pytest=7.1.0
    
    
   


