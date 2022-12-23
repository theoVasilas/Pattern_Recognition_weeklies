# -*- coding: utf-8 -*-
"""erg_6.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_4dXHTm9MGEsEqrEINU_9JzPG72OqoHJ
"""

from sklearn import datasets
import pandas as pd
import numpy as np

iris = datasets.load_iris() #Importing data set 
iris.keys()

iris = pd.DataFrame(
    data= np.c_[iris['data'], iris['target']],
    columns= iris['feature_names'] + ['target']
    )

species = []

for i in range(len(iris['target'])):
    if iris['target'][i] == 0:
        species.append("setosa")
    elif iris['target'][i] == 1:
        species.append('versicolor')
    else:
        species.append('virginica')


iris['species'] = species

import matplotlib.pyplot as plt

setosa = iris[iris.species == "setosa"]
versicolor = iris[iris.species=='versicolor']
virginica = iris[iris.species=='virginica']

fig, ax = plt.subplots()
fig.set_size_inches(13, 7) # adjusting the length and width of plot

# lables and scatter points
ax.scatter(setosa['petal length (cm)'], setosa['petal width (cm)'], label="Setosa", facecolor="blue")
ax.scatter(versicolor['petal length (cm)'], versicolor['petal width (cm)'], label="Versicolor", facecolor="yellow")
ax.scatter(virginica['petal length (cm)'], virginica['petal width (cm)'], label="Virginica", facecolor="red")


ax.set_xlabel("petal length (cm)")
ax.set_ylabel("petal width (cm)")
ax.grid()
ax.set_title("Iris petals")
ax.legend()

iris.describe()

"""remuving unuseful columns

spliting to train data 80% and test data 20% with random selection

scaling data with 0 mean remaning the standar diviation

tranforming to tensorflow

"""

from sklearn.model_selection import train_test_split
import torch
from sklearn.preprocessing import StandardScaler

# Droping the target and species since we only need the measurements
X = iris.drop(['target','species'], axis=1)

# converting into numpy array and assigning petal length and petal width
X = X.to_numpy()
y = iris['target'].to_numpy()

# Splitting into train and test
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2)

scaler = StandardScaler()
#X_train = scaler.fit_transform(X_train)
#X_test = scaler.transform(X_test)

X_train = torch.FloatTensor(X_train)
X_test = torch.FloatTensor(X_test)
y_train = torch.LongTensor(y_train)
y_test = torch.LongTensor(y_test)

print("Length of the test data : ", X_train.shape )
print("Length of the validation data : ", X_test.shape)

import torch.nn as nn

class NN_Sigmoid(nn.Module):
    def __init__(self):
        super(NN_Sigmoid, self).__init__()
        #self.flatten = nn.Flatten()
        self.linear_stack = nn.Sequential(
            nn.Linear(4, 30),
            nn.Sigmoid(),
            nn.Linear(30,3),
        )

    def forward(self, x):
        #x = self.flatten(x)
        logits = self.linear_stack(x)
        return logits

class NN_ReLU(nn.Module):
    def __init__(self):
        super(NN_ReLU, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_stack = nn.Sequential(
            nn.Linear(4, 30),
            nn.ReLU(),
            nn.Linear(30,3),
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_stack(x)
        return logits

class My_NN_Relu(nn.Module):
    def __init__(self):
        super(My_NN_Relu, self).__init__()
        #self.flatten = nn.Flatten()
        self.linear_stack = nn.Sequential(
            nn.Linear(4, 20),
            nn.ReLU(),
            nn.Linear(20,10),
            nn.ReLU(),
            nn.Linear(10,3),
        )

        # Define proportion or neurons to dropout
        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        #x = self.flatten(x)
        logits = self.linear_stack(x)
        logits = self.dropout(logits)
        return logits

models = [ NN_Sigmoid() , NN_ReLU() , My_NN_Relu() ]
torch.save(models, 'models.pth')

"""Create a trainuing loop """

def train_loop(model,optimizer,path_weigths,criterion,schedule,X_train,y_train,X_test,y_test,num_epochs,train_losses,test_losses):
    loss_train_old = 100
    for epoch in range(num_epochs):
        #clear out the gradients from the last step loss.backward()
        optimizer.zero_grad()

        # Compute prediction and loss
        #forward feed
        output_train = model(X_train)
        #calculate the loss
        loss_train = loss_fn(output_train, y_train)

        #backward propagation: calculate gradients
        loss_train.backward()
        #update the weights
        optimizer.step()

        #calculate train loss without optimizing model weights
        output_test = model(X_test)
        loss_test = criterion(output_test,y_test)

        train_losses[epoch] = loss_train.item()
        test_losses[epoch] = loss_test.item()
        correct_test = (output_test.argmax(1) == y_test).type(torch.float).sum().item()
            
        
        if (epoch + 1) % 50 == 0:
            print(f" Epoch {epoch+1}/{num_epochs}, Train Loss: {loss_train.item():.4f}, Test Loss: {loss_test.item():.4f}")
            correct_test /= len(X_test)
            print(f"Accuracy: {(100*correct_test):>0.1f}% \n")
        
        #save the best model weights if the train loss has decresed
        if train_losses[epoch] < loss_train_old :
          torch.save(model.state_dict(), path_weigths)
          loss_train_old = train_losses[epoch]
          print("saved ",end=" ")

    if schedule == 1 :
      #decreseng learning rate      
      scheduler.step()      


    print(f"Weights data have been saved in {(path_weigths)} \n")

def print_the_model(model):
  #print the model
  print(model)
  params = list(model.parameters())
  print("Number of learnable parameters' sets: " , len(params))
  for i in params:
    print(i.size()) 

model_selc = 0 ; #0:Sigmoid30 1:Relu30 2:MyNN
model = models[model_selc] ;

print_the_model(model)

#number o iterations
num_epochs = 10000
train_losses = np.zeros(num_epochs)
test_losses  = np.zeros(num_epochs)

# Initialize the loss function
loss_fn = nn.CrossEntropyLoss()

schedule_en = 0 #true=1 false=0

if schedule_en==1:
  #step each time
  learning_rate = 0.01
else:
  learning_rate = 0.001

optimizer_SGD = torch.optim.SGD(model.parameters(), lr=learning_rate) #,momentum=0.9)
optimizer_Adam = torch.optim.Adam(model.parameters(),lr=learning_rate)
optimizer_Adam_2 = torch.optim.Adam(model.parameters(),lr=learning_rate, weight_decay=0.05)
optimizers = [ optimizer_SGD , optimizer_Adam , optimizer_Adam_2 ]

path_weigths = ["best_weights_SGD.pth" , "best_weights_Adam.pth" , "best_weights_Adam_2.pth" ]

i = 0  # 0,1,2
PATH = path_weigths[i]
optimizer = optimizers[i]

#Decays the learning rate of each parameter group by gamma every epoch.
scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.9)

# start training 
train_loop(model,optimizer,PATH,loss_fn,schedule_en,X_train,y_train,X_test,y_test,num_epochs,train_losses,test_losses)

plt.figure(figsize=(10,10))
plt.plot(train_losses, label='train loss')
plt.plot(test_losses, label='test loss')
plt.legend()
plt.show()

print(f"load weights from {(PATH)}\n")
print_the_model(model)
#model.load_state_dict(torch.load(PATH))

"""Confusion map for train"""

output_train = model(X_train)

from sklearn import metrics

print("Precision, Recall, Confusion matrix, in training\n")

# Precision Recall scores
print(metrics.classification_report(y_train, output_train.argmax(1) , digits=3))

# Confusion matrix
print(metrics.confusion_matrix(y_train, output_train.argmax(1) ))

"""Confusion map for test"""

output_test = model(X_test)

from sklearn import metrics

print("Precision, Recall, Confusion matrix, in testing\n")

# Precision Recall scores
print(metrics.classification_report(y_test, output_test.argmax(1) , digits=3))

# Confusion matrix
print(metrics.confusion_matrix(y_test, output_test.argmax(1) ))