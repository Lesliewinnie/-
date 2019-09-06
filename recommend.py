import numpy as np
#import Faker
import load_data
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.python.keras.preprocessing.sequence import pad_sequences

from deepctr.models import DeepFM
from deepctr.inputs import SparseFeat, VarLenSparseFeat,get_fixlen_feature_names,get_varlen_feature_names
from bert_serving.client import BertClient
bc=BertClient()

def recommend_resume2job(job_id):#输入职位id，得到推荐的简历id
    for i in range(0,len(job)):
        if(job.iloc[i,0]==job_id):
            print("vccccccccc")
            temp=job.iloc[i]
            temp.values[-4]=bc.encode([str(temp.values[-4])]).tolist()
            temp.values[-1]=bc.encode([str(temp.values[-1])]).tolist()
            break
    result=[]
    for i in range(0,len(resume)):
        if((len(resume.loc[i,['workingExperiences']].values[0])>=temp.values[4])&
           (resume.loc[i,['basicInfo']].values[0]['location'] in str(temp.values[-3]))):
            test_input=[np.array([len(resume.loc[i,['workingExperiences']].values[0])]),
                        pd.Series(temp.values[-4]),pd.Series(temp.values[-1]),pd.Series([resume.loc[i,['skill']].values[0]])]
            result.append([resume.loc[i,['userId']].values[0],model.predict(test_input, batch_size=256)])
    result.sort(key=lambda x:x[1],reverse=True)
    code=[]
    length=min(10,len(result))
    for i in range(length):
        code.append(result[i][0])
    res={job_id:code}
    return res
def recommend_job2resume(resume_id):#输入简历id，得到推荐的职位id
    for i in range(0,len(resume)):
        if(str(resume.iloc[i,0])==resume_id):
            temp=resume.iloc[i]
            break                
    result=[]
    for i in range(0,len(job)):
        if((len(temp['workingExperiences'])>=job.iloc[i,4])
           &(temp['basicInfo']['location'] in job.loc[i,'work_place'])):
            test_input=[np.array([len(temp['workingExperiences'])]),
                        pd.Series(job.iloc[i,-4]),pd.Series(job.iloc[i,-1]),pd.Series([temp['skill']])]
            result.append([job.loc[i,'id'],model.predict(test_input, batch_size=256)])
    result.sort(key=lambda x:x[1],reverse=True)
    code=[]
    length=min(10,len(result))
    for i in range(length):
        code.append(result[i][0])
    res={resume_id:code}
    return res

def combine(x):
    print(x)
    skill=""
    for i in range(len(x)):
        skill=skill+x[i]['skill']
    return skill

#训练模型
training_data = pd.read_excel("C:/Users/admin/Desktop/1.xlsx")#已标注的训练数据
resume= load_data.load_resume_from_service()#简历数据库
job=load_data.load_job_from_mysql()#职位数据库
resume['skill']=list(map(combine,resume['skills']))
for i in range(len(resume)):
    if(resume.loc[i,['basicInfo']].values[0]['location']!=None):
        resume.loc[i,['basicInfo']].values[0]['location']=resume.loc[i,['basicInfo']].values[0]['location'].replace("/","-")
    else:
        resume.loc[i,['basicInfo']].values[0]['location']=""
job.columns=['id','company_id','release_time','job_posting_line','work_exp','edu_exp','job_nature','min_salary','max_salary','position_labels','job_description','work_place','online_state','job_name']
all_column=list(range(len(training_data.columns.values)))
sparse_features = ["working_exp_id"]
dense_features=["job_description","job_name","skill"]

target = ['label']
# 1.Label Encoding for sparse features,and process sequence features
for feat in sparse_features:
    lbe = LabelEncoder()
    training_data[feat] = lbe.fit_transform(training_data[feat])
# preprocess the sequence feature
for i in dense_features:
    training_data[i]=bc.encode(training_data[i].values.tolist()).tolist()
for i in ['job_description','job_name']:
    job[i]=bc.encode(job[i].tolist()).tolist()
for i in range(len(resume)):
    if(resume.loc[i,'skill']!=''):
        resume.loc[i,'skill']=bc.encode([resume.loc[i,'skill']])
    else:
        resume.loc[i,'skill']=[0]*768  
fixlen_feature_columns = [SparseFeat(feat, training_data[feat].nunique())
                    for feat in sparse_features]
varlen_feature_columns=[]
varlen_input = []
for feat in dense_features:
    varlen_input=varlen_input+[training_data[feat]]
# 2.count #unique features for each sparse field and generate feature config for sequence feature


linear_feature_columns = fixlen_feature_columns + varlen_feature_columns
dnn_feature_columns = fixlen_feature_columns + varlen_feature_columns
fixlen_feature_names = get_fixlen_feature_names(linear_feature_columns + dnn_feature_columns)

# 3.generate input data for model
fixlen_input = [training_data[name].values for name in fixlen_feature_names]
model_input = fixlen_input + varlen_input # make sure the order is right
varlen_feature_names=dense_features

# 4.Define Model,compile and train
model = DeepFM(linear_feature_columns,dnn_feature_columns,task='regression')
model.compile("adam", "mse", metrics=['mse'], )
history = model.fit(model_input, training_data[target].values,
                    batch_size=256, epochs=10, verbose=2, validation_split=0.2, )
#示例
result=recommend_job2resume("f66959f9-e64c-408c-8f82-55058c777640")
print(result)


