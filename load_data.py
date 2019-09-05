import pandas as pd
import py_eureka_client.eureka_client as eureka_client
import pymysql
import config
import json

# 初始化
# 注册eureka_client
eureka_client.init_discovery_client(config.eureka_server)

# 从本地的excel中获取data
def load_data_from_excel():
    return pd.read_excel(config.excel_data_path)
def load_resume_from_excel():
    return pd.read_excel(config.excel_resume_path)
def load_job_from_excel():
    return pd.read_excel(config.excel_job_path)

# 通过接口获取resume
def load_resume_from_service():
    res = eureka_client.do_service("ZUUL", "/api/resumeservice/resume/getAllResume")
    resume = json.loads(res)['content']
    print(resume)

    # 这边你自己把结构调成你要的frame最后return

    return None


# 职位数据过多，直接查库
def load_job_from_mysql():
    connector = pymysql.connect(user=config.mysql_user, password=config.mysql_pwd, database='job_service_prod',
                                use_unicode=True, host=config.mysql_host, port=config.mysql_port)
    cursor = connector.cursor()
    sql = 'select * from job_new limit 1000' # 实际操作的时候把limit去掉，因为20W职位数据，测试仅用1000够了
    column_name = ['id', 'company_id', 'release_time', 'job_posting_line', 'work_experience_requirements',
                   'educational_requirements', 'job_nature', 'minimum_salary', 'maximum_salary',
                   'position_labels', 'job_description', 'work_places', 'online_state', 'job_name'] # 读取到的字段顺序
    cursor.execute(sql)
    values  = cursor.fetchall()
    df=pd.DataFrame(list(values))
    # 这边你自己把value的结构调成你要的frame最后return

    cursor.close()
    connector.close()

    return df

if __name__ == '__main__':
    # load_job_from_mysql()
    load_resume_from_service()
