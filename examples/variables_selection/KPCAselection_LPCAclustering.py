import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import OpenMORe.model_order_reduction as model_order_reduction
import OpenMORe.clustering as clustering
from OpenMORe.utilities import *

file_options = {
    "path_to_file"              : "/Users/giuseppedalessio/Dropbox/GitHub/data", 
    #"path_to_file"              : "/Users/giuseppedalessio/Dropbox/GitLab/OpenMORe/data",
    "input_file_name"           : "cfdf.csv",
}

settings = {
    #centering and scaling options
    
    "center"                    : True,
    "centering_method"          : "mean",
    "scale"                     : True,
    "scaling_method"            : "auto",

    #variables selection options
    "select_variables"          : True,
    "method"                    : "procustes", #b2, b4, procustes, procustes rotation
    "number_of_PCs"             : 8,
    "number_of_variables"       : 50,
    "path_to_labels"            : "/Users/giuseppedalessio/Dropbox/GitLab/OpenMORe/data",
    "labels_name"               : "none.csv",

    #clustering options
    #set the number of clusters
    "number_of_clusters"        : 8,
    #set the initialization method (random, observations, kmeans, pkcia, uniform)
    "initialization_method"     : "uniform",
    #enable additional options:
    "adaptive_PCs"              : False,    # --> use a different number of PCs in each cluster (to test)
    "correction_factor"         : "off",    # --> enable eventual corrective coefficients for the LPCA algorithm:
                                            #     'off', 'mean', 'min', 'max', 'std', 'phc_standard', 'phc_median', 'phc_robust', 'medianoids', 'medoids' are available
    "classify"                  : False,    # --> classify a new matrix Y on the basis of the lpca clustering
    "write_on_txt"              : True,     # --> write the idx vector with the class for each observation
    "evaluate_clustering"       : True,     # --> enable the calculation of indeces to evaluate the goodness of the clustering


}

X = readCSV(file_options["path_to_file"], file_options["input_file_name"])
Y = X
print("matrix dimensions: {}".format(X.shape))

if settings["select_variables"]:

    KPVs = model_order_reduction.KPCA(X)
    KPVs.eigens = settings["number_of_PCs"]
    KPVs.retained = settings["number_of_variables"]
    KPVs.path_to_labels = "/home/peppe/Dropbox/GitLab/OpenMORe/data"
    KPVs.labels_file_name = "none.csv"
    KPVs.kernel_type = 'polynomial'

    labels, ____, numbers = KPVs.select_variables()

    X = X[:,numbers]

print("The new data dimensions are: {}".format(X.shape))

model = clustering.lpca(X)
model.clusters = settings["number_of_clusters"]
model.eigens = settings["number_of_PCs"]
model.initialization = settings["initialization_method"]
model.correction = settings["correction_factor"]

index = model.fit()


if settings["evaluate_clustering"]:

    #evaluate the clustering solution
    PHC_coeff, PHC_deviations = evaluate_clustering_PHC(Y, index, method='PHC_standard')
    print(PHC_coeff)

    #evaluate the clustering solution by means of the Davies-Bouldin index
    X_tilde = center_scale(Y, center(Y, method=settings["centering_method"]), scale(Y, method=settings["scaling_method"]))
    DB = evaluate_clustering_DB(X_tilde, index)


    text_file = open("stats_clustering_solution.txt", "wt")
    DB_index = text_file.write("DB index equal to: {} \n".format(DB))
    PHC_coeff = text_file.write("Average PHC is: {} \n".format(np.mean(PHC_coeff)))
    text_file.close()


