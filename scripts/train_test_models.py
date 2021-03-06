# A fourth script that reads the data from the second script, performs the modeling and summarizes the results as a figure(s) and a table(s). 
# These analysis artifacts should be written to files. This should take at least two arguments: (path/filename pointing to the data, a path/filename prefix where to write the figure(s)/table(s) to and what to call it (e.g., results/this_analysis))

# Usage: python3 scripts/preprocessing_data.py <input_X_train> <input_y_train> <input_X_test> <input_y_test> <output_path>
# input_X_train:   Path to the data file for x training set
# input_y_train:   Path to the data file for y training set
# input_X_test:   Path to the data file for x testing set
# input_y_test:   Path to the data file for y testing set
# output_path:  Path of where to locally write the file

# load libraries/packages or source functions from other scripts

#from src import preprocess as pp
import os
#%matplotlib inline
import sys
sys.path.append('.')
import os


# import functions
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
    plot_confusion_matrix,
)
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    cross_val_score,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.svm import SVC
import random
import plotly.express as px
import plotly.figure_factory as ff


from group4package import preprocess as pp
from group4package import summary_stats_function as ss
from group4package import metrics_function as cm
from group4package import function_count_plot as cp
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score

# parse arguments
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('input_X_train', type=str,
                    help='Path to the data file for x training set')
parser.add_argument('input_y_train', type=str,
                    help='Path to the data file for y training set')
parser.add_argument('input_X_test', type=str,
                    help='Path to the data file for x testing set')
parser.add_argument('input_y_test', type=str,
                    help='Path to the data file for y testing set')
parser.add_argument('output_path', type=str,
                    help='Path of where to locally write the file')

args = parser.parse_args()

def train_test_models(X_train, y_train, X_test, y_test, output_path):
    
    X_train = pd.read_csv(X_train)
    y_train = pd.read_csv(y_train)
    X_test = pd.read_csv(X_test)
    y_test = pd.read_csv(y_test)
    
    # 29
    numeric_feats = [     # apply scaling
    "LIMIT_BAL",
    "BILL_AMT1",
    "BILL_AMT2",
    "BILL_AMT3",
    "BILL_AMT4", 
    "BILL_AMT5",
    "BILL_AMT6",
    "PAY_AMT1",
    "PAY_AMT2",
    "PAY_AMT3",
    "PAY_AMT4",
    "PAY_AMT5",
    "PAY_AMT6",
    "AGE",]

    categorical_feats = [  # apply one-hot encoding
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "PAY_4",
    "PAY_5",
    "PAY_6",
    "EDUCATION",
    "SEX",
    "MARRIAGE",]
    
    # 30
    ct = make_column_transformer(
        (StandardScaler(), numeric_feats,),
        (OneHotEncoder(handle_unknown="ignore"), categorical_feats,),

    )    
    # 31
    dummy = DummyClassifier()

    pipe = make_pipeline(ct, dummy)

    scores = cross_validate(pipe, X_train, y_train, return_train_score=True, cv=5, scoring="roc_auc")
    scores_1 = pd.DataFrame(scores)
    output_path_scores_1 = output_path + 'scores_1.csv'
    scores_1.to_csv(output_path_scores_1, index = False)
        
    # 32
    random.seed()

    train_scores = []
    cv_scores = []

    C = 10.0 ** np.arange(-1.5, 2, 0.5)
 
    for c in C:
        pipe_lr = make_pipeline(ct, LogisticRegression(max_iter=1000, C=c),)
    
        results = cross_validate(pipe_lr, X_train, y_train, return_train_score=True, scoring = "roc_auc")
    
        train_scores.append(results["train_score"].mean())
        cv_scores.append(results["test_score"].mean())
    

    scores_2 = pd.DataFrame({"C": C, "Train Scores": train_scores, "CV Scores": cv_scores })
    output_path_scores_2 = output_path + 'scores_2.csv'
    scores_2.to_csv(output_path_scores_2, index = False)
        
    # 33
    best_C = scores_2.loc[scores_2["CV Scores"].idxmax(), "C"]
    ## TODO
        
    # 34
    random.seed()

    model = make_pipeline(ct, LogisticRegression(max_iter=1000, C=best_C),)
    model.fit(X_train, y_train)
        
    # 35
    ohe_feature_names = (
    model.named_steps["columntransformer"]
    .named_transformers_["onehotencoder"]
    .get_feature_names()
    .tolist())
        
    feat_names = (numeric_feats + ohe_feature_names)
        
    # 36
    coefs = {
    "coefficient": model.named_steps["logisticregression"].coef_[0].tolist(),
    "absolute_value": np.absolute(model.named_steps["logisticregression"].coef_[0].tolist()),}
        
    df_coefs = pd.DataFrame(coefs, index=feat_names).sort_values("absolute_value", ascending=False)
    output_path_de_coefs = output_path + 'coefs.csv'
    df_coefs.to_csv(output_path_de_coefs, index = False)


    x0_2_OR = np.exp(df_coefs.iat[0,0])
    ## TODO
    x0_0_OR = np.exp(df_coefs.iat[1,0])
    ## TODO
        
    # 39

    # prediction probabilities on test set 
    lr_prob = model.predict_proba(X_test)[:,1]

    # roc_auc score on test set 
    roc_lr = roc_auc_score(y_test, lr_prob)
    
    fpr, tpr, thresholds = roc_curve(y_test, lr_prob)

    roc_lr = round(roc_lr, 4)

    auc_label = "AUC is " + str(roc_lr)

    plt.plot(fpr, tpr, label="ROC Curve")
    plt.xlabel("FPR")
    plt.ylabel("TPR (recall)")
    plt.fill_between(fpr, tpr, color='blue', alpha=0.2, label=auc_label)
    plt.legend(loc="best");
    output_path_fig = output_path + 'roc.png'
    plt.savefig(output_path_fig)
    
    # 40
    predict = model.predict(X_test)

    TN, FP, FN, TP = confusion_matrix(y_test, predict).ravel()

    TN = int(TN)
    FP = int(FP)
    FN = int(FN)
    TP = int(TP)

    res = cm.calculate_metrics(FP, FN, TP)
    output_path_res = output_path + 'metrics.csv'
    res.to_csv(output_path_res)

    plot_confusion_matrix(model,
                          X_test,
                          y_test,
                          display_labels=["Non default", "default"],
                          values_format="d",
                          cmap=plt.cm.Blues,)
    output_path_confusion_mtx = output_path + 'confusion_matrix.png'
    plt.savefig(output_path_confusion_mtx)
    
        
        
def main(X_train, y_train, X_test, y_test, output_path):
    train_test_models(X_train, y_train, X_test, y_test, output_path)

if __name__ == "__main__":
    main(args.input_X_train, args.input_y_train, args.input_X_test, args.input_y_test, args.output_path)
