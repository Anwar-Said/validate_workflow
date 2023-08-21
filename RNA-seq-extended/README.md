# RNA-seq-extended Workflow Description 
The following description will tell the user how to prepare and execute the workflow for a succesfull
repreat of the original experiment.

## Environment
For the execution environment, you are going to need a linux based machine with [cwltool](https://github.com/common-workflow-language/cwltool)
installed on it. Additionally, you will also need [docker](https://docs.docker.com/engine/install/) installed to be able to run
the containerized computing elements.

## Description

### RNA-seq-extended
1.	The model identifies bio-features / genes that distinguish TRD (Treatment resistant responders) from Healthy Control (HC) samples. The identified bio-features will help define the biological basis of TRD.
2.	List of inputs - 2 files are provided as inputs:
	1.	metadata.txt - File containing the metadata which indicates which samples correspond to TRD and which samples correspond to HC group
	2.	htseq_counts_matrix.txt - This file contains Raw counts of reads obtained from blood mapped to each gene (rows) for each sample (columns) in the metadata. This data is obtained from an RNA-seq experiment.
3.	List of outputs - Output is the csv file &#39;whole_blood_responder_vs_control_eff.csv&#39;. This file has 2 columns. Column 1 contains gene IDs of the genes which are indicative of treatment resistant responder (TRD) patients compared to healthy controls (HC). Column 2 is the Effect size of the gene (coefficients from the logistic regression model).
4.	Model environment, packages and versions-
	1.	The model environment is Python version 3.9.
	2.	Packages required are Scikit-learn, Pandas and Numpy 
	3.	scikit-learn v1.0.2, pandas v1.4.0 and numpy v1.23.5
    4.  Platform - linux/amd64
    5.  R program v3.5
5.	Model parameter C was selected using using 10-fold cross validation for the Logistic regression model with L1 penalty. liblinear solver was utilized.
6.	Workflow is an end-to-end model. 
7.	Execution environment is dockerized. Docker images are available at https://hub.docker.com/r/aarthir239/rnaseq and https://hub.docker.com/r/aarthir239/get_vst_from_counts
8.	Training and test data is an intermediate CSV file containing the VST normalized counts from HC and TRD blood RNA-seq samples. A metadata txt file is also required which elaborates on which samples are TRD and which are HC. This data has been uploaded to UDCP under Bootcamp Data -&gt; bootcampdata_MSSM_MURROUGH V10


### Required inputs
 - content : 


### Generated outputs
 - genes : 


## Execution
To run the workflow, you need to give the following command:
```
cwltool --no-match-user --no-read-only --tmpdir $PWD --preserve-environment LEAP_CLI_DIR RNA-seq-extended.cwl.json --content ... 
```