import numpy as np
import matplotlib.pyplot as plt
from model import model, index
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score, confusion_matrix, accuracy_score, roc_curve, auc
from sklearn.model_selection import train_test_split
# from preprocess.preprocessing import preprocess
from sklearn.model_selection import GridSearchCV
from sklearn.metrics.scorer import make_scorer
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from fileIO import writeToFile
from model import index




class DT(model):
    def __init__(self):
        self.dt_classifier = DecisionTreeClassifier()

    # def train(self, data_train):
    def gridSearch(self, X_train, y_train):
        # parameters:
        # min_sample_per_leaf: too small, overfit
        # max_depth: too large, overfit. default none.


  
        # clf = GridSearchCV(svr, parameters)
        # f1_scorer = make_scorer(f1_score)

        # X = data_train[:, 1:]
        # y = data_train[:, 0]
        # y = y.astype(int)
        y_train = y_train.astype(int)
        best_f1score, best_clf = 0, None
        X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.33, random_state=42)
        # for min_samples_leaf in np.arange(1, 21, 10):
        # for min_samples_leaf in np.arange(20, 60, 5):
        for min_samples_leaf in [21]:
            # # for max_features in ('auto', 'sqrt', 'log2'):
            # for max_features in ['sqrt', 'log2', None]:
            for max_features in [None]:
                # for max_depth in np.append([None], np.arange(4, 20, 2)):
                for max_depth in [None]:
                    dt = DecisionTreeClassifier(
                           min_samples_leaf = min_samples_leaf,
                           max_features = max_features
                           )
                    # rf = RandomForestClassifier()
                    dt.fit(X_train, y_train)
                    y_pred = dt.predict(X_test)
                    curr_score = f1_score(y_test, y_pred)
                    if(curr_score >= best_f1score):
                        best_f1score = curr_score
                        best_clf = dt
                    print "min_samples_leaf:", min_samples_leaf, "max_features", max_features, " max_depth: ", max_depth, "f1 score: ", curr_score
        

        # my_scorer = make_scorer(f1_score)
        # rf = RandomForestClassifier()
        # clf = GridSearchCV(rf, parameters, scoring=my_scorer)
        # clf.fit(X_train, y_train)
        # return clf 
        return best_clf

    
    def train(self, data_train):
        X_train = data_train[:, 1:]
        y_train = data_train[:, 0]
        # self.rf_classifier.fit(X_train, y_train)
        X_train, X_train_lr, y_train, y_train_lr = train_test_split(X_train, y_train, test_size=0.1, random_state=42)
        self.X_train, self.y_train = X_train, y_train.astype(int)
        self.X_train_lr, self.y_train_lr = X_train_lr, y_train_lr.astype(int)   # for plotting ROC curve
        self.dt_classifier = self.gridSearch(X_train, y_train)
        tree.export_graphviz(self.dt_classifier, out_file='decisionTree.dot')

    def predict(self, X_pred):
        y_pred = self.dt_classifier.predict(X_pred)
        return y_pred

    #def evaluate(self, data_test):

    # np.expand_dims(np.array([1,2,3,4]), 1)
    def evaluate(self, data_test):
        X_test = data_test[:,1:]
        y_test = data_test[:,0]
        y_test = y_test.astype(int)
        y_pred = self.dt_classifier.predict(X_test)
        f1score = f1_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)

        # calculate ROC
        dt = self.dt_classifier
        dt_enc = OneHotEncoder()
        dt_lm = LogisticRegression()
        # print "self.X_train.shape: ", self.X_train.shape
        # print np.squeeze(dt.apply(self.X_train)).shape
        # print dt.apply(self.X_train_lr).shape
        # print dt.apply(X_test).shape

        dt_enc.fit( np.expand_dims(dt.apply(self.X_train), 1) )
        dt_lm.fit(dt_enc.transform( np.expand_dims(dt.apply(self.X_train_lr), 1)), self.y_train_lr)
        y_pred_dt_lm = dt_lm.predict_proba(dt_enc.transform( np.expand_dims(dt.apply(X_test), 1) ))[:, 1]
        fpr_dt_lm, tpr_dt_lm, _ = roc_curve(y_test, y_pred_dt_lm)
        self.fpr_dt_lm, self.tpr_dt_lm = fpr_dt_lm, tpr_dt_lm
        auc_score = auc(fpr_dt_lm, tpr_dt_lm)
        self.roc_curve("roc_dt")
        self.lift_chart(y_pred, y_pred_dt_lm, "liftchart of decision tree classifier", "liftchart_dt")
        print "auc_score", auc_score
        print "accuracy: ", accuracy_score(y_test, y_pred)
        

        return index(None, f1score)

    def roc_curve(self, file_path):
        print 'ploting roc curve >>>>'
        plt.figure()
        plt.plot(self.fpr_dt_lm,self.tpr_dt_lm,color='blue',label='ROC curve')
        plt.xlim([0.0,1.0])
        plt.ylim([0.0,1.0])
        plt.title('Receiver operating characteristic')
        plt.xlabel('False Positive')
        plt.ylabel('True Positive')
        plt.savefig(file_path)    

    def lift_chart(self, y_test,y_score,title,file_path):
        pos = y_test
        npos = np.sum(pos)
        index = np.argsort(y_score)
        index = index[::-1]
        sort_pos = pos[index]
        cpos = np.cumsum(sort_pos) 

        rappel = cpos/float(npos)

        n = y_test.shape[0]
        taille = np.arange(start=1,stop=n+1,step=1)

        taille = taille / float(n)
        import matplotlib.pyplot as plt
        #title and axis labels
        plt.figure()
        plt.title(title)
        plt.xlabel('Sample Size')
        plt.ylabel('Percentage of Badbuy Found')
        plt.scatter(taille,taille,marker='.',linewidths=0.05,color='blue')
        plt.scatter(taille,rappel,marker='.',color='red')
        plt.savefig(file_path)

# data = np.load('preprocess/data.npy')
# X, y, X_submit = preprocess()
X = np.load("preprocess/X_train_labeled.npy")
X_submit = np.load("preprocess/X_test_labeled.npy")
y = np.load("preprocess/y.npy")


y = y.astype(int)
y = y.reshape(y.shape[0], 1)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
dt_classifier = DT()


data_train = np.hstack((y_train, X_train))
dt_classifier.train(data_train)

data_test = np.hstack((y_test, X_test))


# f1score, cm = dt_classifier.evaluate(data_test)
eval_index = dt_classifier.evaluate(data_test)

y_submit = dt_classifier.predict(X_submit)
# print "size of X_test: ", X_submit.shape
writeToFile('dt_result.csv', y_submit)

print "f1_score: ",  eval_index.F_score
# print "confusion matrix: "
# print cm








