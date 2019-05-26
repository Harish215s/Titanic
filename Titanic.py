# -*- coding: utf-8 -*-
"""
Created on Sun May 26 18:31:34 2019

@author: Harish
"""


# Import the needed referances
import pandas as pd
import numpy as np
import csv as csv

from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier

#Shuffle the datasets
from sklearn.utils import shuffle

#Learning curve
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
from sklearn.model_selection import ShuffleSplit

import seaborn as sns

addpoly = True
plot_lc = 0   # 1--display learning curve/ 0 -- don't display

#loading the data sets from the csv files
print('--------load train & test file------')
Train = pd.read_csv('E:/project/New folder/train.csv')
Test = pd.read_csv('E:/project/New folder/test.csv')

sns.countplot('Survived',data=Train)
plt.show()

sns.countplot('Sex',hue='Survived',data=Train)
plt.show()

sns.countplot('Pclass', hue='Survived', data=Train)
plt.title('Pclass: Sruvived vs Dead')
plt.show()

sns.factorplot('Pclass', 'Survived', hue='Sex', data=Train)
plt.show()

f,ax=plt.subplots(1,2,figsize=(18,8))
sns.violinplot('Pclass','Age',hue='Survived',data=Train,split=True,ax=ax[0])
ax[0].set_title('PClass and Age vs Survived')
ax[0].set_yticks(range(0,110,10))
sns.violinplot("Sex","Age", hue="Survived", data=Train,split=True,ax=ax[1])
ax[1].set_title('Sex and Age vs Survived')
ax[1].set_yticks(range(0,110,10))
plt.show()


f,ax=plt.subplots(1,2,figsize=(20,8))
sns.barplot('SibSp','Survived', data=Train,ax=ax[0])
ax[0].set_title('SipSp vs Survived in BarPlot')
sns.factorplot('SibSp','Survived', data=Train,ax=ax[1])
ax[1].set_title('SibSp vs Survived in FactorPlot')
plt.close(2)
plt.show()

print('train dataset: %s, test dataset %s' %(str(Train.shape), str(Test.shape)) )
Train.head()

print('Id is unique.') if Train.PassengerId.nunique() == Train.shape[0] else print('oops')
print('Train and test sets are distinct.') if len(np.intersect1d(Train.PassengerId.values, Test.PassengerId.values))== 0 else print('oops')

datasetHasNan = False
if Train.count().min() == Train.shape[0] and Test.count().min() == Test.shape[0] :
  print('We do not need to worry about missing values.') 
else:
  datasetHasNan = True
print('oops we have nan')

print('----train dataset column types information-------')
dtype_df = Train.dtypes.reset_index()
dtype_df.columns = ["Count", "Column Type"]
dtype_df.groupby("Column Type").aggregate('count').reset_index()

print('----train dataset information-------')
dtype_df

#Check for missing data & list them 
if datasetHasNan == True:
  nas = pd.concat([Train.isnull().sum(), Test.isnull().sum()], axis=1, keys=['Train Dataset', 'Test Dataset']) 
print('Nan in the data sets')
print(nas[nas.sum(axis=1) > 0])

# Class vs Survived
print(Train[['Pclass', 'Survived']].groupby(['Pclass'], as_index=False).mean().sort_values(by='Survived', ascending=False))

# sex vs Survived
print(Train[["Sex", "Survived"]].groupby(['Sex'], as_index=False).mean().sort_values(by='Survived', ascending=False))


print(Train[["SibSp", "Survived"]].groupby(['SibSp'], as_index=False).mean().sort_values(by='Survived', ascending=False))

print(Train[["Parch", "Survived"]].groupby(['Parch'], as_index=False).mean().sort_values(by='Survived', ascending=False))

# Data sets cleaing, fill nan (null) where needed and delete uneeded columns
print('----Strat data cleaning ------------')



#manage Age
train_random_ages = np.random.randint(Train["Age"].mean() - Train["Age"].std(),
                                      Train["Age"].mean() + Train["Age"].std(),
                                      size = Train["Age"].isnull().sum())

test_random_ages = np.random.randint(Test["Age"].mean() - Test["Age"].std(),
                                     Test["Age"].mean() + Test["Age"].std(),
                                     size = Test["Age"].isnull().sum())

Train["Age"][np.isnan(Train["Age"])] = train_random_ages
Test["Age"][np.isnan(Test["Age"])] = test_random_ages
Train['Age'] = Train['Age'].astype(int)
Test['Age']    = Test['Age'].astype(int)

# Embarked 
Train["Embarked"].fillna('S', inplace=True)
Test["Embarked"].fillna('S', inplace=True)
Train['Port'] = Train['Embarked'].map( {'S': 0, 'C': 1, 'Q': 2} ).astype(int)
Test['Port'] = Test['Embarked'].map({'S': 0, 'C': 1, 'Q': 2}).astype(int)
del Train['Embarked']
del Test['Embarked']

# Fare
Test["Fare"].fillna(Test["Fare"].median(), inplace=True)

# Feature that tells whether a passenger had a cabin on the Titanic
Train['Has_Cabin'] = Train["Cabin"].apply(lambda x: 0 if type(x) == float else 1)
Test['Has_Cabin'] = Test["Cabin"].apply(lambda x: 0 if type(x) == float else 1)

# engineer a new Title feature
# group them
full_dataset = [Train, Test]

##engineer the family size feature
for dataset in full_dataset:
  dataset['FamilySize'] = dataset['SibSp'] + dataset['Parch'] + 1
### new try 

# Create new feature IsAlone from FamilySize
for dataset in full_dataset:
  dataset['IsAlone'] = 0
  dataset.loc[dataset['FamilySize'] == 1, 'IsAlone'] = 1



# Get titles from the names
Train['Title'] = Train.Name.str.extract(' ([A-Za-z]+)\.', expand=False)
Test['Title'] = Test.Name.str.extract(' ([A-Za-z]+)\.', expand=False)

for dataset in full_dataset:
  dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess','Capt', 'Col','Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
  dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
  dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
  dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')



## Create new column "FamilySizeGroup" and assign "Alone", "Small" and "Big"
for dataset in full_dataset:
  dataset['FamilySizeGroup'] = 'Small'
  dataset.loc[dataset['FamilySize'] == 1, 'FamilySizeGroup'] = 'Alone'
  dataset.loc[dataset['FamilySize'] >= 5, 'FamilySizeGroup'] = 'Big'

## Get the average survival rate of different FamilySizes
Train[['FamilySize', 'Survived']].groupby(['FamilySize'], as_index=False).mean()

for dataset in full_dataset:
  dataset['Sex'] = dataset['Sex'].map( {'female': 1, 'male': 0} ).astype(int)

for dataset in full_dataset:    
  dataset.loc[ dataset['Age'] <= 14, 'Age'] = 0
  dataset.loc[(dataset['Age'] > 14) & (dataset['Age'] <= 32), 'Age'] = 1
  dataset.loc[(dataset['Age'] > 32) & (dataset['Age'] <= 48), 'Age'] = 2
  dataset.loc[(dataset['Age'] > 48) & (dataset['Age'] <= 64), 'Age'] = 3
 
for dataset in full_dataset:
  dataset.loc[ dataset['Fare'] <= 7.91, 'Fare'] = 0
  dataset.loc[(dataset['Fare'] > 7.91) & (dataset['Fare'] <= 14.454), 'Fare'] = 1
  dataset.loc[(dataset['Fare'] > 14.454) & (dataset['Fare'] <= 31), 'Fare']   = 2
  dataset.loc[ dataset['Fare'] > 31, 'Fare'] = 3
  dataset['Fare'] = dataset['Fare'].astype(int)
# map the new features
title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}
family_mapping = {"Small": 0, "Alone": 1, "Big": 2}
for dataset in full_dataset:
  dataset['Title'] = dataset['Title'].map(title_mapping)
  dataset['FamilySizeGroup'] = dataset['FamilySizeGroup'].map(family_mapping)

# engineer a new  features
for dataset in full_dataset:
  dataset['IsChildandRich'] = 0
  dataset.loc[(dataset['Age'] <= 0) & (dataset['Pclass'] == 1 ),'IsChildandRich'] = 1  
  dataset.loc[(dataset['Age'] <= 0) & (dataset['Pclass'] == 2 ),'IsChildandRich'] = 1  


for data in full_dataset:
  # classify Cabin by fare
  data['Cabin'] = data['Cabin'].fillna('X')
  data['Cabin'] = data['Cabin'].apply(lambda x: str(x)[0])
  data['Cabin'] = data['Cabin'].replace(['A', 'D', 'E', 'T'], 'M')
  data['Cabin'] = data['Cabin'].replace(['B', 'C'], 'H')
  data['Cabin'] = data['Cabin'].replace(['F', 'G'], 'L')
  data['Cabin'] = data['Cabin'].map({'X': 0, 'L': 1, 'M': 2, 'H': 3}).astype(int) 


# Delete Name column from datasets (No need for them in the analysis)
del Train['Name']
del Test['Name']

del Train['SibSp']
del Test['SibSp']

del Train['Parch']
del Test['Parch']

del Train['FamilySize']
del Test['FamilySize']


del Train['Cabin']
del Test['Cabin']

# Delete Ticket column from datasets  (No need for them in the analysis)
del Train['Ticket']
del Test['Ticket']

del Train['Port']
del Test['Port']




print('----Finish data cleaning ------------')

print('train dataset: %s, test dataset %s' %(str(Train.shape), str(Test.shape)) )
Train.head()

del Train['PassengerId']


X_train = Train.drop("Survived",axis=1)
Y_train = Train["Survived"]
X_test  = Test.drop("PassengerId",axis=1).copy()

print(X_train.shape)
print(Y_train.shape)
print(X_test.shape)

from sklearn.preprocessing import MinMaxScaler,PolynomialFeatures

if addpoly:
  all_data = pd.concat((X_train,
                        X_test), ignore_index=True)

  scaler = MinMaxScaler()
  scaler.fit(all_data)
  all_data=scaler.transform(all_data)
  poly = PolynomialFeatures(2)
  all_data=poly.fit_transform(all_data)

  X_train = all_data[:Train.shape[0]]
  X_test = all_data[Train.shape[0]:]
##
  print(X_train.shape)
  print(Y_train.shape)
  print(X_test.shape)

# Learning curve
cv = ShuffleSplit(n_splits=100, test_size=0.2, random_state=0)
logreg_model = LogisticRegression()
def Learning_curve_model(X, Y, model, cv, train_sizes):
  
  plt.figure()
  plt.title("Learning curve")
  plt.xlabel("Training examples")
  plt.ylabel("Score")


  train_sizes, train_scores, test_scores = learning_curve(model, X, Y, cv=cv, n_jobs=4, train_sizes=train_sizes)

  train_scores_mean = np.mean(train_scores, axis=1)
  train_scores_std  = np.std(train_scores, axis=1)
  test_scores_mean  = np.mean(test_scores, axis=1)
  test_scores_std   = np.std(test_scores, axis=1)
  plt.grid()

  plt.fill_between(train_sizes, train_scores_mean - train_scores_std,train_scores_mean + train_scores_std, alpha=0.1,
                 color="r")
  plt.fill_between(train_sizes, test_scores_mean - test_scores_std,test_scores_mean + test_scores_std, alpha=0.1, color="g")
  plt.plot(train_sizes, train_scores_mean, 'o-', color="r",label="Training score")
  plt.plot(train_sizes, test_scores_mean, 'o-', color="g",label="Cross-validation score")

  plt.legend(loc="best")
  return plt

#learn curve
if plot_lc==1:
  train_size=np.linspace(.1, 1.0, 15)
  Learning_curve_model(X_train,Y_train , logreg_model, cv, train_size)

# Logistic Regression
logreg = LogisticRegression() #(C=0.1, penalty='l1', tol=1e-6)
logreg.fit(X_train, Y_train)
Y_pred = logreg.predict(X_test)

result_train = logreg.score(X_train, Y_train)
result_val = cross_val_score(logreg,X_train, Y_train, cv=5).mean()
print('taring score = %s , while validation score = %s' %(result_train , result_val))

### Support Vector Machines
svc = SVC(C = 0.1, gamma=0.1)
svc.fit(X_train, Y_train)
Y_pred = svc.predict(X_test)

result_train = svc.score(X_train, Y_train)
result_val = cross_val_score(svc,X_train, Y_train, cv=5).mean()
print('taring score = %s , while validation score = %s' %(result_train , result_val))

# Random Forests

random_forest = RandomForestClassifier(criterion='gini', 
                                       n_estimators=1000,
                                       min_samples_split=10,
                                       min_samples_leaf=1,
                                       max_features='auto',
                                       oob_score=True,
                                       random_state=1,
                                       n_jobs=-1)

seed= 42
random_forest =RandomForestClassifier(n_estimators=1000, criterion='entropy', max_depth=5, min_samples_split=2,
                                      min_samples_leaf=1, max_features='auto',    bootstrap=False, oob_score=False, 
                                      n_jobs=1, random_state=seed,verbose=0)

random_forest.fit(X_train, Y_train)
Y_pred = random_forest.predict(X_test)

result_train = random_forest.score(X_train, Y_train)
result_val = cross_val_score(random_forest,X_train, Y_train, cv=5).mean()

print('taring score = %s , while validation score = %s' %(result_train , result_val))

submission = pd.DataFrame({
  "PassengerId": Test["PassengerId"],
  "Survived": Y_pred
})
submission.to_csv('titanic.csv', index=False)
print('Exported')