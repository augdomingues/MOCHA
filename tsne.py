#
#  tsne.py
#
# Implementation of t-SNE in Python. The implementation was tested on Python
# 2.7.10, and it requires a working installation of NumPy. The implementation
# comes with an example on the MNIST dataset. In order to plot the
# results of this example, a working installation of matplotlib is required.
#
# The example can be run by executing: `ipython tsne.py`
#
#
#  Created by Laurens van der Maaten on 20-12-08.
#  Copyright (c) 2008 Tilburg University. All rights reserved.

import numpy as np
import pylab
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import os
import matplotlib as mpl

class TSNE:
    
    def __init__(self):

        # The labels and folders must be in the same order
        self.labels = ["INFOCOM", "INFOCOM2"]
        self.folders = ["trace_infocom05_41nodes_metrics_folder", "infoconer"]

        with open("Fitted Metrics Traces.csv", "w+") as saida:
            for l,f in zip(self.labels, self.folders):
                path = os.path.join(f, "fittedMetrics.txt")
                with open(path, "r") as entrada:
                    for line in entrada:
                        line = line.strip().split(",")
                        metricName = line[0].split(os.sep)[1].replace(".txt", "")
                        family = line[1]
                        saida.write("{},{},{}\n".format(l, metricName, family))

        values = {"lognorm": 0, "norm": 0, "logistic": 0, "expon": 1, "gamma": 1, "pareto": 2}

        trace = {}
        with open("TSNE input.txt", "w+") as saida:
            with open("Fitted Metrics Traces.csv", "r") as entrada:
                for i, line in enumerate(entrada):
                    line = line.strip().split(",")
                    metric = line[1]
                    dist_func = values[line[2]]
                    trace[metric] = dist_func
                    if (i+1)%9 == 0:
                        saida.write("{} ".format(trace["CODU"]))
                        saida.write("{} ".format(trace["TOPO"]))
                        saida.write("{} ".format(trace["EDGEP"]))
                        saida.write("{} ".format(trace["INCO"]))
                        saida.write("{} ".format(trace["CONEN"]))
                        saida.write("{} ".format(trace["VIST"]))
                        saida.write("{} ".format(trace["TRVD"]))
                        saida.write("{} ".format(trace["SPAV"]))
                        saida.write("{}\n".format(trace["RADG"]))
                        trace = {}
        self.lightning_graph()
    

    def lightning_graph(self):
        DISTANCE = 3
        DEVIATION = 1
        first = True

        with open("TSNE input.txt", "r") as entrada:
            for i,line in enumerate(entrada):
                oi = i
                i = i * DISTANCE
                trace = [i] * 9
                line = line.strip().split(" ")
                line = [float(l) for l in line]
                for j in range(0,len(line)):
                    if line[j] == 0:
                        trace[j] += DEVIATION
                    elif line[j] == 2:
                        trace[j] -= DEVIATION
                plt.plot(range(5,14),trace)
                plt.text(4,i+DEVIATION,self.labels[oi],verticalalignment="center", horizontalalignment="center",fontsize=7)
                if first:
                    plt.hlines(i,5,13,linestyles="dashdot",alpha=0.25, label="Exponential")
                    plt.hlines(i+DEVIATION,5,13,linestyles="dashed",alpha=0.25,label="Normal")
                    plt.hlines(i-DEVIATION,5,13,linestyles="dotted", alpha=0.25,label="Pareto")
                    first = False
                else:
                    plt.hlines(i,5,13,linestyles="dashdot",alpha=0.25)
                    plt.hlines(i+DEVIATION,5,13,linestyles="dashed",alpha=0.25)
                    plt.hlines(i-DEVIATION,5,13,linestyles="dotted", alpha=0.25)


        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                   ncol=3, mode="expand", borderaxespad=0.)
        plt.xticks(range(5,14), ["CODU", "TOPO", "EDGEP", "INCO", "CONEN",
            "VIST", "TRVD", "SPAV", "RADG"])
        plt.yticks([],[])
        plt.grid(True)
        plt.xlim(3,14)
        # CODU,TOPO,EDGEP,INCO,VIST,TRVD,RADG

        plt.show()

    def Hbeta(self,D=np.array([]), beta=1.0):
        """
            Compute the perplexity and the P-row for a specific value of the
            precision of a Gaussian distribution.
        """

        # Compute P-row and corresponding perplexity
        P = np.exp(-D.copy() * beta)
        sumP = sum(P)
        H = np.log(sumP) + beta * np.sum(D * P) / sumP
        P = P / sumP
        return H, P


    def x2p(self,X=np.array([]), tol=1e-5, perplexity=30.0):
        """
            Performs a binary search to get P-values in such a way that each
            conditional Gaussian has the same perplexity.
        """

        # Initialize some variables
        print("Computing pairwise distances...")
        (n, d) = X.shape
        sum_X = np.sum(np.square(X), 1)
        D = np.add(np.add(-2 * np.dot(X, X.T), sum_X).T, sum_X)
        P = np.zeros((n, n))
        beta = np.ones((n, 1))
        logU = np.log(perplexity)

        # Loop over all datapoints
        for i in range(n):

            # Print progress
            if i % 500 == 0:
                print("Computing P-values for point %d of %d..." % (i, n))

            # Compute the Gaussian kernel and entropy for the current precision
            betamin = -np.inf
            betamax = np.inf
            Di = D[i, np.concatenate((np.r_[0:i], np.r_[i+1:n]))]
            (H, thisP) = self.Hbeta(Di, beta[i])

            # Evaluate whether the perplexity is within tolerance
            Hdiff = H - logU
            tries = 0
            while np.abs(Hdiff) > tol and tries < 50:

                # If not, increase or decrease precision
                if Hdiff > 0:
                    betamin = beta[i].copy()
                    if betamax == np.inf or betamax == -np.inf:
                        beta[i] = beta[i] * 2.
                    else:
                        beta[i] = (beta[i] + betamax) / 2.
                else:
                    betamax = beta[i].copy()
                    if betamin == np.inf or betamin == -np.inf:
                        beta[i] = beta[i] / 2.
                    else:
                        beta[i] = (beta[i] + betamin) / 2.

                # Recompute the values
                (H, thisP) = self.Hbeta(Di, beta[i])
                Hdiff = H - logU
                tries += 1

            # Set the final row of P
            P[i, np.concatenate((np.r_[0:i], np.r_[i+1:n]))] = thisP

        # Return final P-matrix
        print("Mean value of sigma: %f" % np.mean(np.sqrt(1 / beta)))
        return P


    def pca(self,X=np.array([]), no_dims=50,labels=np.array([])):
        """
            Runs PCA on the NxD array X in order to reduce its dimensionality to
            no_dims dimensions.
        """

        print("Preprocessing the data using PCA...")
        (n, d) = X.shape
        X = X - np.tile(np.mean(X, 0), (n, 1))
        (l, M) = np.linalg.eig(np.dot(X.T, X))
        Y = np.dot(X, M[:, 0:no_dims])
        print("PCA: {}".format(Y))
        pylab.scatter(Y[:,0],Y[:,1])
        for x,y,l in zip(Y[:,0],Y[:,1],labels):
            label = l
            if label == "Dartmouth":
                pylab.text(x,y+0.15,label)
            elif label == "San Francisco":
                pylab.text(x,y-0.15,label)
            else:
                pylab.text(x ,y  ,label)
        pylab.grid(True)
        pylab.ylim(-2,2)
        pylab.xlim(-2,2)
        pylab.title("PCA")
        pylab.show()
        return Y


    def tsne(self,X=np.array([]), no_dims=2, initial_dims=50, perplexity=30.0,labels =
            np.array([])):
        """
            Runs t-SNE on the dataset in the NxD array X to reduce its
            dimensionality to no_dims dimensions. The syntaxis of the function is
            `Y = tsne.tsne(X, no_dims, perplexity), where X is an NxD NumPy array.
        """

        # Check inputs
        if isinstance(no_dims, float):
            print("Error: array X should have type float.")
            return -1
        if round(no_dims) != no_dims:
            print("Error: number of dimensions should be an integer.")
            return -1

        # Initialize variables
        X = self.pca(X, 2,labels).real
        (n, d) = X.shape
        max_iter = 1000
        initial_momentum = 0.5
        final_momentum = 0.8
        eta = 500
        min_gain = 0.01
        Y = np.random.randn(n, no_dims)
        dY = np.zeros((n, no_dims))
        iY = np.zeros((n, no_dims))
        gains = np.ones((n, no_dims))

        # Compute P-values
        P = self.x2p(X, 1e-5, perplexity)
        P = P + np.transpose(P)
        P = P / np.sum(P)
        P = P * 4.									# early exaggeration
        P = np.maximum(P, 1e-12)

        # Run iterations
        for iter in range(max_iter):

            # Compute pairwise affinities
            sum_Y = np.sum(np.square(Y), 1)
            num = -2. * np.dot(Y, Y.T)
            num = 1. / (1. + np.add(np.add(num, sum_Y).T, sum_Y))
            num[range(n), range(n)] = 0.
            Q = num / np.sum(num)
            Q = np.maximum(Q, 1e-12)

            # Compute gradient
            PQ = P - Q
            for i in range(n):
                dY[i, :] = np.sum(np.tile(PQ[:, i] * num[:, i], (no_dims, 1)).T * (Y[i, :] - Y), 0)

            # Perform the update
            if iter < 20:
                momentum = initial_momentum
            else:
                momentum = final_momentum
            gains = (gains + 0.2) * ((dY > 0.) != (iY > 0.)) + \
                    (gains * 0.8) * ((dY > 0.) == (iY > 0.))
            gains[gains < min_gain] = min_gain
            iY = momentum * iY - eta * (gains * dY)
            Y = Y + iY
            Y = Y - np.tile(np.mean(Y, 0), (n, 1))

            # Compute current value of cost function
            if (iter + 1) % 10 == 0:
                C = np.sum(P * np.log(P / Q))
                print("Iteration %d: error is %f" % (iter + 1, C))

            # Stop lying about P-values
            if iter == 100:
                P = P / 4.

        # Return solution
        return Y

    
    def extract_spatial(self,data,row):
        kk = np.ndarray(shape=(row,3))
        for i in range(0,row):
            kk[i,0] = data[i,6]
            kk[i,1] = data[i,7]
            kk[i,2] = data[i,8]
        return kk

    def extract_social(self,data,row):
        #social_metrics = ["CODU", "TOPO", "EDGEP", "INCO", "CONEN"]
        #NUMBER_OF_TRACES = len(self.traces)
        #NUMBER_OF_METRICS = len(social_metrics)
        #KK = np.ndarray(shape=(NUMBER_OF_TRACES,NUMBER_OF_METRICS))
        kk = np.ndarray(shape=(row,5))
        for i in range(0,row):
            kk[i,0] = data[i,0]
            kk[i,1] = data[i,1]
            kk[i,2] = data[i,2]
            kk[i,3] = data[i,3]
            kk[i,4] = data[i,4]
        return kk

    def extract_temporal(self,data,row):
        kk = np.ndarray(shape=(row,2))
        for i in range(0,row):
            kk[i,0] = data[i,5]
        return kk


    def read_data(self):
        # Features order:
        # CODU, TOPO, EDGEP, INCO, VIST, TRVT, TRVD, RADG, SPAV

        data = np.loadtxt("TSNE input.txt")
        KK = data
        number_of_traces = data.shape[0]
        number_of_features = data.shape[1]
        spatial = self.extract_spatial(data,number_of_traces)
        social = self.extract_social(data,number_of_traces)
        temporal = self.extract_temporal(data,number_of_traces)

        spatial = np.where(np.isfinite(spatial), spatial, 0)
        social = np.where(np.isfinite(social), social, 0)
        temporal = np.where(np.isfinite(temporal), temporal, 0)

        Y = self.tsne(spatial , 1, 2, 20.0, self.labels)
        X = self.tsne(social  , 1, 4, 20.0, self.labels)
        Z = self.tsne(temporal, 1, 1, 20.0, self.labels)
        
        line_type = ["solid", "dashed", "dashdot", "dotted", "-", "-.", ":", "solid", "dashed", "dashdot", "dotted", "-", "-.", ":", "solid", "dashed", "dashdot", "dotted", "-",
                "-.", ":"]
        color = [[0,0,0,0],[0,0,1,0], [0,0,1,1], [0,1,0,0], [0,1,0,1], [0,1,1,0], [0,1,1,1], [1,0,0,0], [1,0,0,1], [1,0,1,0], [1,0,1,1], [1,1,0,0], [1,1,0,1], [1,1,1,0]]

        
       # plt.subplot(3,1,1) 
        values = Y[:,0]
        social_values = X[:,0]
        temporal_values = Z[:,0]
        plt.hlines(1,min(values),max(values), alpha=0.25)
        for y,l,lt,c in zip(values,self.labels,line_type,color):
            #plt.text(y,1, '*')
            print("{}: {}".format(l,y))
            plt.eventplot([y],orientation='horizontal', alpha=0.05)
            plt.text(y,1,l,{"va": "center"},rotation=90)
        plt.axis('off')
        plt.title("Spatial")
        #plt.xticks(values,values)
        #plt.yticks([],[])
        #plt.xticks([],[])
        
        plt.ylim(0.45,1.55)
        #plt.spines['right'].set_color('none')
        plt.show()
        plt.clf()
        

       # plt.subplot(3,1,2)
        plt.hlines(1,min(social_values),max(social_values),alpha=0.25)
        for y,l,lt,c in zip(social_values,self.labels,line_type,color):
            plt.eventplot([y],orientation='horizontal',alpha=0.05)
            plt.text(y,1,l,{"va": "center"},rotation=90)
        plt.axis('off')
        plt.title("Social")
        plt.ylim(0.45,1.55)
        #plt.legend()
        plt.show()
        plt.clf()

        #print(Y[:,0])
       # plt.subplot(3,1,3)
        plt.hlines(1,min(temporal_values),max(temporal_values),alpha=0.25)# Draw a horizontal line
        for y,l in zip(temporal_values,self.labels):
            plt.eventplot([y],orientation='horizontal',alpha=0.05)
            plt.text(y,1,l,{"va": "center"},rotation=90)
        
        plt.axis('off')
        plt.title("Temporal")
        plt.ylim(0.45,1.55)
        plt.show()
        
        mpl.style.use("seaborn")
        plt.subplot(1,3,1)
       # plt.plot(Y,Z)
        for x,y,l in zip(Y[:,0],Z[:,0],self.labels):
            label = l
            print("{}: {}".format(x,l))
            plt.text(x,y,label,horizontalalignment='center',fontsize=6.5,verticalalignment='top')
        plt.scatter(Y[:, 0], Z[:, 0], 20)  
        plt.ylabel("Spatial dimension")
        plt.xlabel("Temporal dimension")
        plt.grid(True)
        plt.xticks([],[])
        plt.yticks([],[])
        #pylab.show()
        
        #plt.clf()
        #plt.plot(Y,X)
        plt.subplot(1,3,2)
        for x,y,l in zip(Y[:,0],X[:,0],self.labels):
            label = l
            plt.text(x,y,label,horizontalalignment='center',fontsize=6.5,verticalalignment='top')
        plt.scatter(Y[:,0],X[:,0])
        plt.ylabel("Spatial dimension")
        plt.xlabel("Social dimension")
        plt.xticks([],[])
        plt.yticks([],[])
        #pylab.show()
        #plt.clf()
        plt.subplot(1,3,3)
        for x,y,l in zip(Z[:,0],X[:,0],self.labels):
            label = l
            plt.text(x,y,label,horizontalalignment='center',fontsize=6.5,verticalalignment='top')
        plt.scatter(Z[:,0],X[:,0])
        plt.ylabel("Temporal dimension")
        plt.xlabel("Social dimension")
        plt.xticks([],[])
        plt.yticks([],[])
        #plt.plot(Z,X)
        plt.show()
        plt.tight_layout()
        plt.clf()


t = TSNE()
t.read_data()
'''
if __name__ == "__main__":
    print("Run Y = tsne.tsne(X, no_dims, perplexity) to perform t-SNE on your dataset.")
    print("Running example on 2,500 MNIST digits...")
    X = np.loadtxt("fitinput10.txt")
    KK = X
    for row in range(0,10):
        for column in range(0,9):
            if X[row,column] == 0.25:
                KK[row,column] = 0
            elif X[row,column] == 0.5:
                KK[row,column] = 1
            else:
                KK[row,column] = 2
    print(X)
    print(KK)
    

    
    labels = []
    z0axis = []
    with open("fit_label10.txt", "r") as nomes:
        for n in nomes:
            labels.append(n.strip())
            z0axis.append(-250)
    print(labels)
    number_of_desired_dimensions = 2
    number_of_original_dimensions = 9
    Y = tsne(KK, number_of_desired_dimensions, number_of_original_dimensions, 20.0,labels)
    print(Y)
    
    
    
    pylab.scatter(Y[:, 0], Y[:, 1], 20)
    for x,y,l in zip(Y[:,0],Y[:,1],labels):
        label = l
        pylab.text(x,y,label)
    pylab.title("t-SNE result")
    pylab.xlabel("Statistical distance")
    pylab.grid(True)
    pylab.show()
'''
