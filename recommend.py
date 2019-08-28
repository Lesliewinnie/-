import numpy as np
#import Faker
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.python.keras.preprocessing.sequence import pad_sequences

from deepctr.models import DeepFM
from deepctr.inputs import SparseFeat, VarLenSparseFeat,get_fixlen_feature_names,get_varlen_feature_names
from bert_serving.client import BertClient
bc=BertClient()
def split(x):
    key_ans = x.split('|')
    for key in key_ans:
        if key not in key2index:
            # Notice : input value 0 is a special "padding",so we do not use 0 to encode valid feature for sequence input
            key2index[key] = len(key2index) + 1
    return list(map(lambda x: key2index[x], key_ans))

'''data = pd.read_excel("C:/Users/admin/Desktop/1.xlsx")
resume= pd.read_excel("C:/Users/admin/Desktop/resume_new.xlsx")
job= pd.read_excel("C:/Users/admin/Desktop/job_new1.xlsx")'''
data=load_data_from_excel("C:/Users/admin/Desktop/1.xlsx")
resume=load_resume_from_excel("C:/Users/admin/Desktop/resume_new.xlsx")
job=load_job_from_excel("C:/Users/admin/Desktop/job_new1.xlsx")
job.columns=['id','company_id','release_time','job_posting_line','work_exp','edu_exp','job_nature','min_salary','max_salary','position_labels','job_description','work_place','online_state','job_name']
all_column=list(range(len(data.columns.values)))
#max1=max(data["prof_skill_id"].values)
max2=max(data["project_exp_id"].values)
max3=max(data["school_exp_id"].values)
max4=max(data["paper_id"].values)
max5=max(data["working_exp_id"].values)
sparse_features = ["project_exp_id","school_exp_id","paper_id","working_exp_id"]
#dense_features=["job_description","job_name","self_description","expected_job","hobbies"]
dense_features=["job_description","job_name","skill"]
#for i in range(0,max1):
   # dense_features.append("skill"+str(i))
'''for i in range(0,max2):
    dense_features.append("associated_company"+str(i))
    dense_features.append("project_content"+str(i))
    dense_features.append("project_name"+str(i))
for i in range(0,max3):
    dense_features.append("school_exp_name"+str(i))
for i in range(0,max4):
    dense_features.append("paper_name"+str(i))
for i in range(0,max5):
    dense_features.append("company_name"+str(i))
    dense_features.append("department"+str(i))
    dense_features.append("job_content"+str(i))
    dense_features.append("job_name"+str(i))'''

target = ['label']
# 1.Label Encoding for sparse features,and process sequence features
for feat in sparse_features:
    lbe = LabelEncoder()
    data[feat] = lbe.fit_transform(data[feat])
# preprocess the sequence feature
for i in dense_features:
    data[i]=bc.encode(data[i].values.tolist()).tolist()
for i in ['job_description','job_name']:
    job[i]=bc.encode(job[i].tolist()).tolist()
for i in ["skill"]:
    resume[i]=bc.encode(resume[i].values.tolist()).tolist()
   # print(i)
#for i in dense_features:
 #   data[i]=list(map(embedding,list(data[i].values)))
'''data[sparse_features] = data[sparse_features].fillna(0)
print(data['hobby'])
data[dense_features] = data[dense_features].fillna([0])'''
    
'''key2index = {}
genres_list = list(map(split, data['skill'].values))
genres_length = np.array(list(map(len, genres_list)))
max_len = max(genres_length)
# Notice : padding=`post`
genres_list = pad_sequences(genres_list, maxlen=max_len, padding='post', )
varlen_feature_columns = [VarLenSparseFeat('skill', len(
    key2index) + 1, max_len, 'mean')]  # Notice : value 0 is for padding for sequence input feature'''
fixlen_feature_columns = [SparseFeat(feat, data[feat].nunique())
                    for feat in sparse_features]
varlen_feature_columns=[]
varlen_input = []
for feat in dense_features:
    varlen_input=varlen_input+[data[feat]]
#data['skill']=genres_list.copy()
# 2.count #unique features for each sparse field and generate feature config for sequence feature
#varlen_feature_columns2 = [VarLenSparseFeat(feat, len(data[feat].values)+1,max(np.array(list(map(len, data[feat].values)))))
                    #for feat in dense_features]  # Notice : value 0 is for padding for sequence input feature
linear_feature_columns = fixlen_feature_columns + varlen_feature_columns
dnn_feature_columns = fixlen_feature_columns + varlen_feature_columns
fixlen_feature_names = get_fixlen_feature_names(linear_feature_columns + dnn_feature_columns)

# 3.generate input data for model
fixlen_input = [data[name].values for name in fixlen_feature_names]
model_input = fixlen_input + varlen_input # make sure the order is right
varlen_feature_names=dense_features

# 4.Define Model,compile and train
model = DeepFM(linear_feature_columns,dnn_feature_columns,task='regression')
model.compile("adam", "mse", metrics=['mse'], )
history = model.fit(model_input, data[target].values,
                    batch_size=256, epochs=10, verbose=2, validation_split=0.2, )

choose=input("Recommend resumes for jobs: input 0,else input 1:")
if(choose=='0'):
    job_id=input("Please input the job id:")
    for i in range(0,len(job)):
        if(job.iloc[i,0]==job_id):
            temp=job.iloc[i]
            temp.values[-4]=bc.encode([str(temp.values[-4])]).tolist()
            temp.values[-1]=bc.encode([str(temp.values[-1])]).tolist()
            break
    result=[]
    for i in range(0,len(resume)):
        if((resume.loc[i,['working_exp_id']].values[0]>=temp.values[4])&(resume.loc[i,['school_exp_id']].values[0]>=temp.values[5])
           &(resume.loc[i,['work_place']].values[0] in str(temp.values[-3]))):
            test_input=[np.array([resume.loc[i,['project_exp_id']].values[0]]),np.array([resume.loc[i,['school_exp_id']].values[0]]),
                        np.array([resume.loc[i,['paper_id']].values[0]]),np.array([resume.loc[i,['working_exp_id']].values[0]]),
                        pd.Series(temp.values[-4]),pd.Series(temp.values[-1]),pd.Series([resume.loc[i,['skill']].values[0]])]
            result.append([resume.loc[i,['id']].values[0],model.predict(test_input, batch_size=256)])
    result.sort(key=lambda x:x[1],reverse=True)
    code=[]
    for i in range(0,len(result)):
        code.append(result[i][0])
    print(code)
elif(choose=='1'):
    resume_id=input("Please input the resume id:")
    for i in range(0,len(resume)):
        if(str(resume.iloc[i,0])==resume_id):
            temp=resume.iloc[i]
            break
    result=[]
    for i in range(0,len(job)):
        if((temp['working_exp_id']>=job.iloc[i,4])&(temp['school_exp_id']>=job.iloc[i,5])
           &(temp['work_place'] in job.loc[i,'work_place'])):
            test_input=[np.array([temp['project_exp_id']]),np.array([temp['school_exp_id']]),
                        np.array([temp['paper_id']]),np.array([temp['working_exp_id']]),
                        pd.Series(job.iloc[i,-4]),pd.Series(job.iloc[i,-1]),pd.Series([temp['skill']])]
            result.append([job.loc[i,'id'],model.predict(test_input, batch_size=256)])
    result.sort(key=lambda x:x[1],reverse=True)
    code=[]
    for i in range(0,len(result)):
        code.append(result[i][0])
    print(code)
